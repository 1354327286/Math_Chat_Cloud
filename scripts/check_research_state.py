#!/usr/bin/env python3
"""Read-only navigation checks; never proof certification or compaction."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
from typing import Iterator, Sequence
from urllib.parse import unquote, urlsplit


NAVIGATION_FILES = ("research_state.md", "subgoal.md")
BYTE_BUDGET = 24_576
LINE_BUDGET = 250
STATE_SECTIONS = (
    "Research State",
    "Known Theorems",
    "Open Problems",
    "Failed Attempts",
    "Current Goal",
    "References",
)


@dataclass
class NavigationCheck:
    path: Path
    size_bytes: int | None = None
    line_count: int | None = None
    milestone: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def conditional_proposal(self) -> bool:
        """Size plus caller-reported milestone, never consent or verification."""
        return (
            self.size_bytes is not None
            and self.size_bytes > BYTE_BUDGET
            and self.line_count is not None
            and bool(self.milestone)
        )


def _without_code(text: str) -> str:
    """Mask common Markdown code blocks/spans while keeping list continuations.

    List content starts after its marker and padding. Four more columns start
    indented code; four columns at the document margin also start code. Merely
    looking for a bullet on an indented line would confuse these two contexts.
    """
    lines: list[str] = []
    list_indents: list[int] = []
    previous_blank = True
    fence_character: str | None = None
    fence_length = 0
    fence_base = 0
    for line in text.splitlines(keepends=True):
        expanded = line.expandtabs(4)
        indent = len(expanded) - len(expanded.lstrip(" "))
        blank = not expanded.strip()
        masked = "\n" if line.endswith("\n") else ""
        if fence_character is not None:
            closing = re.match(r"^(`{3,}|~{3,})[ \t]*(?:\n)?$", expanded.lstrip(" "))
            if (
                closing
                and fence_base <= indent <= fence_base + 3
                and closing.group(1)[0] == fence_character
                and len(closing.group(1)) >= fence_length
            ):
                fence_character = None
            lines.append(masked)
            previous_blank = blank
            continue
        if blank:
            lines.append(line)
            previous_blank = True
            continue

        marker = re.match(r"^ *(?:([-+*]|\d+[.)]))( +)(.*)$", expanded)
        # A sibling/outdented item selects its parent's content indentation.
        # Unindented paragraph text can be a lazy list continuation only when
        # it has no intervening blank line or new block marker.
        new_block = re.match(r"^ *(?:#{1,6}(?: |$)|>|`{3,}|~{3,}|[-*_]{3,}\s*$)", expanded)
        if marker or previous_blank or new_block:
            while list_indents and indent < list_indents[-1]:
                list_indents.pop()
        base = list_indents[-1] if list_indents else 0
        relative_indent = max(0, indent - base)
        body = expanded[base:] if indent >= base else expanded.lstrip(" ")

        if marker and indent >= base and relative_indent < 4:
            padding = len(marker.group(2))
            # Five or more spaces after the marker begin indented code within
            # the item; only the first space belongs to its list indentation.
            content_base = indent + len(marker.group(1)) + (padding if padding <= 4 else 1)
            list_indents.append(content_base)
            base = content_base
            relative_indent = 0 if padding <= 4 else padding - 1
            body = (" " * relative_indent) + marker.group(3)
        if relative_indent >= 4:
            lines.append(masked)
        else:
            opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", body)
            if opening:
                fence_character = opening.group(1)[0]
                fence_length = len(opening.group(1))
                fence_base = base
                lines.append(masked)
            else:
                lines.append(line)
        previous_blank = False
    return re.sub(r"(`+)(?!`)(.*?)\1(?!`)", "", "".join(lines), flags=re.DOTALL)


def _destination(text: str, start: int) -> str | None:
    """Read a common Markdown destination, allowing escaped/balanced parentheses."""
    position = start
    while position < len(text) and text[position].isspace():
        position += 1
    if position == len(text):
        return None
    if text[position] == "<":
        end = position + 1
        while end < len(text):
            if text[end] == "\\":
                end += 2
            elif text[end] == ">":
                return text[position + 1 : end]
            elif text[end] == "\n":
                return None
            else:
                end += 1
        return None
    start = position
    depth = 0
    while position < len(text):
        character = text[position]
        if character == "\\":
            position += 2
            continue
        if character == "(":
            depth += 1
        elif character == ")":
            if depth == 0:
                break
            depth -= 1
        elif character.isspace():
            break
        position += 1
    if depth:
        return None
    return text[start:position]


def _destinations(text: str) -> Iterator[str]:
    # Definitions are checked even if no reference currently uses their label.
    for match in re.finditer(r"(?<!\\)!?\[[^\]\n]*\]\(", text):
        destination = _destination(text, match.end())
        if destination:
            yield destination
    for match in re.finditer(r"(?m)^ {0,3}\[[^\]\n]+\]:[ \t]*", text):
        destination = _destination(text, match.end())
        if destination:
            yield destination


def _local_link_errors(markdown: str, directory: Path) -> list[str]:
    errors: list[str] = []
    # Registered problems are top-level repository directories. Sibling inbox/
    # and framework links are legitimate; traversal outside that parent is not.
    repository = directory.absolute().parent.resolve()
    for destination in dict.fromkeys(_destinations(markdown)):
        destination = re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])", r"\1", destination)
        if any(ord(character) < 32 or ord(character) == 127 for character in destination):
            errors.append(f"unsafe control character in Markdown link target: {destination!r}")
            continue
        try:
            parsed = urlsplit(destination)
        except ValueError:
            errors.append(f"cannot parse Markdown link target: {destination}")
            continue
        # Never access a network target or execute a URI. Unknown schemes and
        # local file URIs are diagnostics rather than a bypass for path checks.
        if parsed.scheme:
            if parsed.scheme.lower() not in {"http", "https", "mailto", "ftp", "ftps", "doi", "arxiv"}:
                errors.append(f"unsafe or unsupported link scheme: {destination}")
            continue
        if parsed.netloc or not parsed.path:
            continue
        local_path = unquote(parsed.path)
        if (
            any(ord(character) < 32 or ord(character) == 127 for character in local_path)
            or "\\" in local_path
            or Path(local_path).is_absolute()
            or re.match(r"^[A-Za-z]:", local_path)
        ):
            errors.append(f"unsafe local link target (use a relative repository path): {destination!r}")
            continue
        try:
            lexical = Path(os.path.abspath(directory / local_path))
            if not lexical.is_relative_to(repository):
                errors.append(f"unsafe local link target escapes repository: {destination}")
                continue
            # Resolve the original expression: stripping '..' first changes
            # its meaning when the preceding component is a symlink.
            resolved = (directory / local_path).resolve()
            if not resolved.is_relative_to(repository):
                errors.append(f"unsafe local link target resolves outside repository: {destination}")
                continue
            exists = resolved.exists()
        except (OSError, ValueError, RuntimeError):
            exists = False
        if not exists:
            errors.append(f"missing local link target: {destination}")
    return errors


def check_navigation_file(
    problem_dir: Path,
    file_name: str = "research_state.md",
    *,
    check_links: bool = False,
    milestone: str | None = None,
) -> NavigationCheck:
    """Inspect one file without writes, mathematical inference, or consent changes."""
    if file_name not in NAVIGATION_FILES:
        raise ValueError(f"file must be one of {', '.join(NAVIGATION_FILES)}")
    result = NavigationCheck(
        path=Path(problem_dir) / file_name,
        milestone=milestone.strip() if milestone and milestone.strip() else None,
    )
    try:
        raw = result.path.read_bytes()
    except OSError as exc:
        result.errors.append(f"cannot read selected navigation file: {exc}")
        return result
    result.size_bytes = len(raw)
    try:
        # Decode for diagnostics only. No bytes are normalized or written back.
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        result.errors.append(f"selected navigation file is not valid UTF-8: {exc}")
        return result
    result.line_count = len(text.splitlines())
    markdown = _without_code(text)
    if not text.strip():
        result.errors.append("selected navigation file is empty")
    if file_name == "research_state.md":
        headings = [
            match.group(1).strip()
            for match in re.finditer(
                r"(?m)^ {0,3}##(?!#)[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*$", markdown
            )
        ]
        for heading in STATE_SECTIONS:
            count = headings.count(heading)
            if count == 0:
                result.errors.append(f"missing required state section: {heading}")
            elif count > 1:
                result.errors.append(f"duplicate state section: {heading}")
    # subgoal.md intentionally has no mandatory headings or automatic migration.
    if check_links:
        result.errors.extend(_local_link_errors(markdown, result.path.parent))
    if result.size_bytes > BYTE_BUDGET:
        result.warnings.append(
            f"exceeds the advisory byte budget ({BYTE_BUDGET:,} bytes); "
            "size alone does not authorize compaction or a reminder"
        )
    if result.line_count > LINE_BUDGET:
        result.warnings.append(
            f"exceeds the advisory line budget ({LINE_BUDGET} lines); "
            "line count alone does not trigger a compaction proposal"
        )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem_dir", type=Path, help="selected mathematical problem directory")
    parser.add_argument("--file", choices=NAVIGATION_FILES, default="research_state.md")
    parser.add_argument("--check-links", action="store_true", help="check local Markdown file targets only")
    parser.add_argument(
        "--milestone",
        help="caller-reported recorded substantive outcome; not verified by this helper",
    )
    args = parser.parse_args(argv)
    if args.milestone is not None and not args.milestone.strip():
        parser.error("--milestone must describe a recorded substantive outcome")
    result = check_navigation_file(
        args.problem_dir,
        args.file,
        check_links=args.check_links,
        milestone=args.milestone,
    )
    print(f"Navigation file: {result.path}")
    if result.size_bytes is not None:
        print(f"Raw UTF-8 size: {result.size_bytes:,} bytes ({result.size_bytes / 1024:.2f} KiB)")
    if result.line_count is not None:
        print(f"Lines: {result.line_count}")
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.conditional_proposal:
        print(
            "CONDITIONAL PROPOSAL ONLY: The selected file exceeds 24,576 bytes "
            "and a milestone was supplied."
        )
        print(f"Caller-reported milestone (not verified): {result.milestone}")
        print(
            "Before asking once about this named file, verify the milestone's evidence "
            "and check memory/events.md for outstanding or deferred proposals. "
            "Explicit user agreement is required before drafting, archiving, or rewriting. "
            "Follow docs/state_compaction.md; no action or reminder was sent or recorded."
        )
    print(
        "Read-only navigation diagnostics only. No files changed; no proof, milestone, "
        "heading anchor, archive integrity, or user approval was certified."
    )
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
