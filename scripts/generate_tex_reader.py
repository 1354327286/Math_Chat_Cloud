#!/usr/bin/env python3
"""Generate a read-only Markdown companion for a formal TeX review manuscript.

The TeX file remains the source of truth.  The generated ``*.reader.md`` file
is a disposable local reading copy whose citations prefer version-matched
local reference sources recorded in ``refs/catalog.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


STATEMENT_NAMES = {
    "theorem": "Theorem",
    "proposition": "Proposition",
    "lemma": "Lemma",
    "corollary": "Corollary",
    "claim": "Claim",
    "definition": "Definition",
    "remark": "Remark",
}

MATH_MACROS = {
    r"\OKp": r"\mathcal O_{K'}",
    r"\OK": r"\mathcal O_K",
    r"\Spf": r"\operatorname{Spf}",
    r"\Spec": r"\operatorname{Spec}",
    r"\Vect": r"\operatorname{Vect}",
    r"\Perf": r"\operatorname{Perf}",
    r"\Loc": r"\operatorname{Loc}",
    r"\Coh": r"\operatorname{Coh}",
    r"\RHom": r"R\!\operatorname{Hom}",
    r"\Hom": r"\operatorname{Hom}",
    r"\Ext": r"\operatorname{Ext}",
    r"\Tor": r"\operatorname{Tor}",
    r"\pd": r"\operatorname{pd}",
    r"\Supp": r"\operatorname{Supp}",
    r"\length": r"\operatorname{length}",
    r"\Rees": r"\operatorname{Rees}",
    r"\gr": r"\operatorname{gr}",
    r"\an": r"\mathrm{an}",
    r"\crys": r"\mathrm{crys}",
    r"\refl": r"\mathrm{refl}",
    r"\et": r"\mathrm{\acute et}",
    r"\cA": r"\mathcal A",
    r"\cE": r"\mathcal E",
    r"\cP": r"\mathcal P",
    r"\cK": r"\mathcal K",
    r"\cG": r"\mathcal G",
    r"\cL": r"\mathcal L",
    r"\cM": r"\mathcal M",
    r"\m": r"\mathfrak m",
    r"\DeltaSite": r"\mathbin{\Delta}",
    r"\DeltaSp": r"\mathbin{\Delta}^{\mathrm{sp}}",
    r"\derivedtensor": r"\mathbin{\otimes}^{L}",
}


@dataclass
class CatalogReference:
    key: str
    entry: dict[str, Any]
    project_root: Path

    def local_path(self) -> Path | None:
        for field in ("tex_main", "txt_fallback", "pdf"):
            value = self.entry.get(field)
            if isinstance(value, str) and value:
                candidate = self.project_root / "refs" / value
                if candidate.is_file():
                    return candidate
        return None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strip_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in text.splitlines())


def normalize_source_identifier(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def bibliography_blocks(tex: str) -> dict[str, str]:
    match = re.search(r"\\begin\{thebibliography\}.*?\n(.*?)\\end\{thebibliography\}", tex, re.S)
    if not match:
        return {}
    body = match.group(1)
    pieces = re.split(r"(?=\\bibitem\{)", body)
    result: dict[str, str] = {}
    for piece in pieces:
        item = re.match(r"\\bibitem\{([^}]+)\}\s*(.*)", piece, re.S)
        if item:
            result[item.group(1)] = item.group(2).strip()
    return result


def match_catalog(project_root: Path, bibitems: dict[str, str]) -> dict[str, CatalogReference]:
    catalog_path = project_root / "refs" / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entries = [entry for entry in catalog.get("references", []) if isinstance(entry, dict)]
    result: dict[str, CatalogReference] = {}
    for key, block in bibitems.items():
        arxiv_match = re.search(r"arXiv:(\d{4}\.\d{4,5})(v\d+)?", block, re.I)
        doi_match = re.search(r"https?://doi\.org/([^}\s]+)", block, re.I)
        chosen = None
        for entry in entries:
            if arxiv_match and entry.get("arxiv_id") == arxiv_match.group(1):
                chosen = entry
                break
            if doi_match and normalize_source_identifier(str(entry.get("doi") or "")) == normalize_source_identifier(doi_match.group(1)):
                chosen = entry
                break
        if chosen:
            result[key] = CatalogReference(key, chosen, project_root)
    return result


def theorem_declarations(lines: list[str]) -> dict[str, tuple[str, str, str | None]]:
    declarations: dict[str, tuple[str, str, str | None]] = {}
    own = re.compile(r"\\newtheorem\*?\{([^}]+)\}\{([^}]+)\}(?:\[([^]]+)\])?")
    shared = re.compile(r"\\newtheorem\*?\{([^}]+)\}\[([^]]+)\]\{([^}]+)\}")
    for line in lines:
        match = shared.search(line)
        if match:
            declarations[match.group(1)] = (match.group(3), match.group(2), None)
            continue
        match = own.search(line)
        if match:
            declarations[match.group(1)] = (match.group(2), match.group(1), match.group(3))
    return declarations


def statement_ranges(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    declarations = theorem_declarations(lines)
    counters: dict[str, int] = {}
    section = 0
    main_letters: dict[str, int] = {}
    ranges: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if re.search(r"\\section\*?\{", line):
            section += 1
            for env, (_, root, within) in declarations.items():
                if within == "section" or declarations.get(root, (None, None, None))[2] == "section":
                    counters[root] = 0
        begin = re.search(r"\\begin\{([^}]+)\}", line)
        if not begin or begin.group(1) not in declarations:
            continue
        env = begin.group(1)
        display, root, within = declarations[env]
        root_display, _, root_within = declarations.get(root, (display, root, within))
        within = within or root_within
        counters[root] = counters.get(root, 0) + 1
        if within == "section":
            number = f"{section}.{counters[root]}"
        elif root.lower().startswith("main") or env.lower().startswith("main"):
            main_letters[root] = main_letters.get(root, 0) + 1
            number = chr(64 + main_letters[root])
        else:
            number = str(counters[root])
        end = index
        depth = 0
        for cursor in range(index, len(lines)):
            depth += len(re.findall(r"\\begin\{" + re.escape(env) + r"\}", lines[cursor]))
            depth -= len(re.findall(r"\\end\{" + re.escape(env) + r"\}", lines[cursor]))
            if depth == 0:
                end = cursor
                break
        ranges.append({"display": display, "number": number, "start": index + 1, "end": end + 1})
    return ranges


def locate_reference(path: Path, locator: str) -> str:
    clean = locator.replace("~", " ").replace(r"\S", "Section ")
    match = re.search(
        r"(Theorem|Proposition|Lemma|Corollary|Definition)s?\s+(\d+(?:\.\d+)+|[A-Z])",
        clean,
        re.I,
    )
    if match and path.suffix.lower() == ".tex":
        wanted_display = match.group(1).lower()
        wanted_number = match.group(2)
        for item in statement_ranges(path):
            if item["display"].lower() == wanted_display and item["number"] == wanted_number:
                return f"L{item['start']}-L{item['end']}"

    if match:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        patterns = (
            rf"{re.escape(match.group(1))}\s*{re.escape(match.group(2))}",
            rf"{re.escape(match.group(1).upper())}\s*{re.escape(match.group(2))}",
        )
        for index, line in enumerate(lines):
            if any(re.search(pattern, line, re.I) for pattern in patterns):
                return f"L{max(1, index + 1)}-L{min(len(lines), index + 16)}"
    return ""


def relative_link(output: Path, target: Path, fragment: str = "") -> str:
    relative = Path(os.path.relpath(target, output.parent)).as_posix()
    return f"{relative}#{fragment}" if fragment else relative


def aux_labels(source: Path) -> dict[str, str]:
    labels: dict[str, str] = {}
    for aux in source.parent.glob(f"build*/{source.stem}.aux"):
        for match in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", aux.read_text(encoding="utf-8", errors="replace")):
            labels[match.group(1)] = match.group(2)
    return labels


def expand_math_macros(value: str) -> str:
    for macro, expansion in sorted(MATH_MACROS.items(), key=lambda item: len(item[0]), reverse=True):
        value = re.sub(re.escape(macro) + r"(?![A-Za-z])", lambda _match, replacement=expansion: replacement, value)
    return value


def replace_balanced_command(text: str, command: str, formatter: Any, arguments: int = 1) -> str:
    token = f"\\{command}"
    cursor = 0
    output: list[str] = []
    while True:
        start = text.find(token, cursor)
        if start < 0:
            output.append(text[cursor:])
            break
        boundary = start + len(token)
        if boundary < len(text) and text[boundary].isalpha():
            output.append(text[cursor:boundary])
            cursor = boundary
            continue
        scan = boundary
        values: list[str] = []
        ok = True
        for _ in range(arguments):
            while scan < len(text) and text[scan].isspace():
                scan += 1
            if scan >= len(text) or text[scan] != "{":
                ok = False
                break
            depth = 1
            end = scan + 1
            while end < len(text) and depth:
                if text[end] == "{" and text[end - 1] != "\\":
                    depth += 1
                elif text[end] == "}" and text[end - 1] != "\\":
                    depth -= 1
                end += 1
            if depth:
                ok = False
                break
            values.append(text[scan + 1 : end - 1])
            scan = end
        if not ok:
            output.append(text[cursor:boundary])
            cursor = boundary
            continue
        output.append(text[cursor:start])
        output.append(formatter(*values))
        cursor = scan
    return "".join(output)


class ReaderConverter:
    def __init__(self, source: Path, output: Path, project_root: Path):
        self.source = source
        self.output = output
        self.project_root = project_root
        self.raw = source.read_text(encoding="utf-8")
        self.bibitems = bibliography_blocks(self.raw)
        self.catalog = match_catalog(project_root, self.bibitems)
        self.labels = aux_labels(source)
        self.statement_counter = 0
        self.statement_numbers: dict[str, int] = {}
        self.emitted_labels: set[str] = set()

    def citation(self, match: re.Match[str]) -> str:
        locator = (match.group(1) or "").strip()
        keys = [key.strip() for key in match.group(2).split(",")]
        rendered: list[str] = []
        for key in keys:
            label = f"{key}, {self.plain(locator)}" if locator else key
            reference = self.catalog.get(key)
            path = reference.local_path() if reference else None
            if path:
                fragment = locate_reference(path, locator) if locator else ""
                rendered.append(f"[{label}]({relative_link(self.output, path, fragment)})")
            else:
                rendered.append(f"[{label}]")
        return "; ".join(rendered)

    def plain(self, value: str) -> str:
        value = replace_balanced_command(value, "href", lambda _url, label: label, 2)
        value = replace_balanced_command(value, "texorpdfstring", lambda first, _second: first, 2)
        for command in ("emph", "textup", "upshape"):
            value = replace_balanced_command(value, command, lambda body: body)
        value = expand_math_macros(value)
        value = value.replace("~", " ")
        value = value.replace(r"\S", "§")
        value = value.replace(r"\'e", "é").replace(r"\`e", "è")
        value = value.replace(r"\v{C}", "Č")
        value = re.sub(r"\\(?:smallskip|noindent|sloppy|raggedright|begingroup|endgroup)\b", "", value)
        return re.sub(r"\s+", " ", value).strip()

    def inline(self, value: str) -> str:
        value = re.sub(r"\\cite(?:\[([^]]*)\])?\{([^}]+)\}", self.citation, value)
        value = replace_balanced_command(value, "href", lambda url, label: f"[{self.plain(label)}]({url})", 2)
        value = replace_balanced_command(value, "url", lambda url: f"[{url}]({url})")
        value = replace_balanced_command(value, "emph", lambda body: f"*{self.plain(body)}*")
        value = replace_balanced_command(value, "textup", lambda body: self.plain(body))
        value = replace_balanced_command(value, "texorpdfstring", lambda first, _second: first, 2)

        def equation_ref(match: re.Match[str]) -> str:
            label = match.group(1)
            number = self.labels.get(label, label)
            return f"[({number})](#{label})"

        def ordinary_ref(match: re.Match[str]) -> str:
            label = match.group(1)
            number = self.labels.get(label, label)
            return f"[{number}](#{label})"

        value = re.sub(r"\\eqref\{([^}]+)\}", equation_ref, value)
        value = re.sub(r"\\ref\{([^}]+)\}", ordinary_ref, value)
        value = expand_math_macros(value)
        value = value.replace(r"\(", "$ ").replace(r"\)", " $")
        value = value.replace(r"\'e", "é").replace(r"\`e", "è").replace(r"\v{C}", "Č")
        value = value.replace("~", " ")
        value = value.replace(r"\S", "§")
        value = re.sub(r"\\(?:smallskip|noindent|sloppy|raggedright|begingroup|endgroup)\b", "", value)
        return value.strip()

    def title(self) -> str:
        match = re.search(r"\\title\{(.*?)\}\s*\\author", self.raw, re.S)
        if not match:
            return self.source.stem
        value = match.group(1).replace(r"\\", ": ")
        value = re.sub(r"\\large\s*", "", value)
        return self.plain(value).replace("$", "")

    def reference_section(self) -> list[str]:
        if not self.bibitems:
            return []
        output = ["## References", ""]
        for key, block in self.bibitems.items():
            clean = re.sub(r"\\url\{[^}]+\}", "", block)
            clean = self.inline(clean).replace("\\mathbf", r"\mathbf")
            clean = re.sub(r"\s+", " ", clean).strip().rstrip(".") + "."
            links: list[str] = []
            reference = self.catalog.get(key)
            if reference:
                local = reference.local_path()
                if local:
                    links.append(f"[local source]({relative_link(self.output, local)})")
                public = reference.entry.get("source_url")
                if isinstance(public, str) and public:
                    links.append(f"[public source]({public})")
            suffix = f" {' · '.join(links)}" if links else ""
            output.extend([f"- <a id=\"ref-{key}\"></a> **{key}.** {clean}{suffix}", ""])
        return output

    def convert(self) -> str:
        body_match = re.search(r"\\begin\{document\}(.*)\\end\{document\}", self.raw, re.S)
        if not body_match:
            raise ValueError("TeX source has no document environment")
        body = re.sub(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", "", body_match.group(1), flags=re.S)
        body = strip_comments(body)
        lines = body.splitlines()
        output = [
            "<!--",
            "generated-reader-copy",
            f"source: {self.source.name}",
            f"source-sha256: {sha256(self.source)}",
            f"source-mtime: {datetime.fromtimestamp(self.source.stat().st_mtime).astimezone().isoformat(timespec='seconds')}",
            "do-not-edit: true",
            "-->",
            "",
            f"# {self.title()}",
            "",
            "> Internal reading copy. The linked TeX manuscript is the only formal review source; regenerate this file after every TeX change.",
            "",
            f"[Formal TeX source]({self.source.name})",
        ]
        pdf_candidates = list(self.source.parent.glob(f"build*/{self.source.stem}.pdf"))
        if pdf_candidates:
            output[-1] += f" · [Compiled PDF]({relative_link(self.output, pdf_candidates[0])})"
        output.append("")

        index = 0
        list_stack: list[tuple[str, int]] = []
        while index < len(lines):
            raw = lines[index]
            line = raw.strip()
            if not line or line in {r"\maketitle", r"\begingroup", r"\endgroup", r"\sloppy", r"\raggedright"}:
                output.append("")
                index += 1
                continue
            if line.startswith(r"\begin{abstract}"):
                block: list[str] = []
                index += 1
                while index < len(lines) and not lines[index].strip().startswith(r"\end{abstract}"):
                    block.append(lines[index].strip())
                    index += 1
                output.extend(["## Abstract", "", self.inline(" ".join(block)), ""])
                index += 1
                continue
            if line.startswith((r"\section{", r"\subsection{")) and line.count("{") > line.count("}"):
                joined = [line]
                balance = line.count("{") - line.count("}")
                while index + len(joined) < len(lines) and balance > 0:
                    continuation = lines[index + len(joined)].strip()
                    joined.append(continuation)
                    balance += continuation.count("{") - continuation.count("}")
                line = " ".join(joined)
                index += len(joined) - 1
            section = re.match(r"\\(section|subsection)\{(.*)\}", line)
            if section:
                level = "##" if section.group(1) == "section" else "###"
                output.extend([f"{level} {self.inline(section.group(2))}", ""])
                index += 1
                continue
            if re.match(r"\\begin\{(" + "|".join(STATEMENT_NAMES) + r")\}\[", line) and "]" not in line:
                joined = [line]
                while index + len(joined) < len(lines) and "]" not in joined[-1]:
                    joined.append(lines[index + len(joined)].strip())
                line = " ".join(joined)
                index += len(joined) - 1
            statement = re.match(r"\\begin\{(" + "|".join(STATEMENT_NAMES) + r")\}(?:\[(.*)\])?", line)
            if statement:
                env, heading = statement.groups()
                label = ""
                probe = index + 1
                while probe < min(len(lines), index + 5):
                    label_match = re.search(r"\\label\{([^}]+)\}", lines[probe])
                    if label_match:
                        label = label_match.group(1)
                        break
                    probe += 1
                number = self.labels.get(label, "") if label else ""
                anchor = f'<a id="{label}"></a>\n\n' if label else ""
                if label:
                    self.emitted_labels.add(label)
                title = STATEMENT_NAMES[env] + (f" {number}" if number else "")
                if heading:
                    title += f" ({self.inline(heading)})"
                output.extend([f"{anchor}#### {title}", ""])
                index += 1
                continue
            end_statement = re.match(r"\\end\{(" + "|".join(STATEMENT_NAMES) + r")\}", line)
            if end_statement:
                output.append("")
                index += 1
                continue
            if line.startswith(r"\begin{proof}[") and "]" not in line:
                joined = [line]
                while index + len(joined) < len(lines) and "]" not in joined[-1]:
                    joined.append(lines[index + len(joined)].strip())
                line = " ".join(joined)
                index += len(joined) - 1
            proof = re.match(r"\\begin\{proof\}(?:\[(.*)\])?", line)
            if proof:
                label = self.inline(proof.group(1)) if proof.group(1) else "Proof"
                output.extend([f"**{label}.**", ""])
                index += 1
                continue
            if line.startswith(r"\end{proof}"):
                output.extend(["□", ""])
                index += 1
                continue
            display = re.match(r"\\begin\{(equation|aligned|align\*?|gather\*?)\}", line)
            if display:
                env = display.group(1)
                block: list[str] = []
                labels: list[str] = []
                index += 1
                while index < len(lines) and not re.search(r"\\end\{" + re.escape(env) + r"\}", lines[index]):
                    labels.extend(re.findall(r"\\label\{([^}]+)\}", lines[index]))
                    block.append(re.sub(r"\\label\{[^}]+\}", "", lines[index]))
                    index += 1
                for label in labels:
                    output.extend([f'<a id="{label}"></a>', ""])
                math = expand_math_macros("\n".join(block).strip())
                output.extend(["$$", math, "$$", ""])
                index += 1
                continue
            if line == r"\[":
                block = []
                index += 1
                while index < len(lines) and lines[index].strip() != r"\]":
                    block.append(lines[index])
                    index += 1
                output.extend(["$$", expand_math_macros("\n".join(block).strip()), "$$", ""])
                index += 1
                continue
            begin_list = re.match(r"\\begin\{(enumerate|itemize)\}", line)
            if begin_list:
                list_stack.append((begin_list.group(1), 0))
                index += 1
                continue
            if re.match(r"\\end\{(enumerate|itemize)\}", line):
                if list_stack:
                    list_stack.pop()
                output.append("")
                index += 1
                continue
            if line.startswith(r"\item"):
                content = re.sub(r"^\\item(?:\[[^]]+\])?\s*", "", line)
                if list_stack:
                    kind, count = list_stack[-1]
                    list_stack[-1] = (kind, count + 1)
                    prefix = f"{count + 1}." if kind == "enumerate" else "-"
                else:
                    prefix = "-"
                output.append(f"{prefix} {self.inline(content)}")
                index += 1
                continue
            label_only = re.fullmatch(r"\\label\{([^}]+)\}", line)
            if label_only:
                if label_only.group(1) not in self.emitted_labels:
                    output.extend([f'<a id="{label_only.group(1)}"></a>', ""])
                    self.emitted_labels.add(label_only.group(1))
                index += 1
                continue
            if re.match(r"\\(?:end|begin)\{", line):
                index += 1
                continue

            paragraph = [line]
            index += 1
            while index < len(lines):
                candidate = lines[index].strip()
                if not candidate or re.match(r"\\(?:begin|end|section|subsection|item|label|\[)", candidate):
                    break
                paragraph.append(candidate)
                index += 1
            output.extend([self.inline(" ".join(paragraph)), ""])

        output.extend(self.reference_section())
        compact: list[str] = []
        for line in output:
            if line == "" and compact and compact[-1] == "":
                continue
            compact.append(line.rstrip())
        return "\n".join(compact).strip() + "\n"


def find_project_root(source: Path) -> Path:
    for parent in source.parents:
        if (parent / "refs" / "catalog.json").is_file():
            return parent
    raise ValueError("Cannot find the problem directory containing refs/catalog.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="formal TeX manuscript")
    parser.add_argument("--output", type=Path, help="generated Markdown path (default: SOURCE.reader.md)")
    parser.add_argument("--check", action="store_true", help="fail if the existing reader copy is stale")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source = args.source.resolve()
    if source.suffix.lower() != ".tex" or not source.is_file():
        raise SystemExit("source must be an existing .tex file")
    output = (args.output or source.with_suffix(".reader.md")).resolve()
    project_root = find_project_root(source)
    try:
        source.relative_to(project_root)
        output.relative_to(project_root)
    except ValueError as exc:
        raise SystemExit("source and output must stay inside one problem directory") from exc
    generated = ReaderConverter(source, output, project_root).convert()
    if args.check:
        if not output.is_file():
            raise SystemExit(f"stale reader copy: {output}")
        existing = output.read_text(encoding="utf-8")
        recorded = re.search(r"(?m)^source-sha256:\s*([0-9a-f]{64})$", existing)
        if not recorded or recorded.group(1) != sha256(source):
            raise SystemExit(f"stale reader copy: {output}")
        print(f"Reader copy is current: {output}")
        return 0
    output.write_text(generated, encoding="utf-8", newline="\n")
    print(f"Generated reader copy: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
