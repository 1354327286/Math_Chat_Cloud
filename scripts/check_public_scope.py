#!/usr/bin/env python3
"""Fail when private research data are staged or tracked by Git."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Iterable, List, Optional, Sequence


PUBLIC_ROOT_FILES = {
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "projects.json",
    "pyproject.toml",
    "reference_index.py",
    "search_arxiv_theorems.py",
    "search_references.py",
}
PUBLIC_PATH_ALLOWLIST = {"templates/research_state.md"}
PUBLIC_TOP_LEVEL_DIRECTORIES = {
    ".github",
    ".githooks",
    "dashboard",
    "docs",
    "example_math_problem",
    "inbox",
    "lean",
    "scripts",
    "skills",
    "templates",
    "tests",
}
EXPECTED_PUBLIC_REGISTRY = {
    "schema_version": 1,
    "projects": [
        {
            "path": "example_math_problem",
            "title": "Example math problem",
            "role": "example",
            "description": "Reusable example workspace with no private research content",
        }
    ],
}
PRIVATE_STATE_FILES = {"research_state.md", "goal.md", "progress.md", "subgoal.md"}
PRIVATE_SUBDIRECTORIES = {"notes", "memory", "refs", "downloads", "handoff"}
PRIVATE_LEAN_PREFIX = ("lean", "MathDailyLean", "Projects")
PUBLIC_LEAN_PROJECTS_README = "lean/MathDailyLean/Projects/README.md"
BLOCKED_SUFFIXES = {".pdf", ".tar", ".tgz", ".zip", ".lancedb"}
DATED_NOTE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
PRIVATE_TERMS_FILE = "private_terms.local.txt"
TEXT_SUFFIXES = {
    "",
    ".css",
    ".html",
    ".js",
    ".json",
    ".lean",
    ".md",
    ".py",
    ".sh",
    ".tex",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(?:github_pat_[A-Za-z0-9_]{20,}|gh[opsu]_[A-Za-z0-9]{30,})\b"),
    "OpenAI API key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}


def violation_reason(raw_path: str) -> Optional[str]:
    path = PurePosixPath(raw_path.replace("\\", "/"))
    parts = path.parts
    if not parts:
        return None
    if path.as_posix() in PUBLIC_PATH_ALLOWLIST:
        return None

    if path.as_posix() == "projects.local.json":
        return "the private project registry must never be public"

    if len(parts) == 1 and path.as_posix() not in PUBLIC_ROOT_FILES:
        return "root files are private unless explicitly allowlisted"

    if len(parts) >= 2 and parts[0] not in PUBLIC_TOP_LEVEL_DIRECTORIES:
        return "unrecognized top-level directories are private project workspaces"

    if parts[0] == "inbox" and path.name != "README.md":
        return f"research {parts[0]} content must remain local"

    if (
        len(parts) >= 4
        and tuple(parts[:3]) == PRIVATE_LEAN_PREFIX
        and path.as_posix() != PUBLIC_LEAN_PROJECTS_README
    ):
        return "problem-specific Lean source must remain local and travel in a problem bundle"

    if len(parts) >= 2 and parts[1] in PRIVATE_SUBDIRECTORIES:
        if path.name != ".gitkeep":
            return f"content under project {parts[1]}/ must remain local"

    if len(parts) == 2 and path.name in PRIVATE_STATE_FILES:
        return "per-problem state and progress files must remain local"

    if len(parts) == 2 and DATED_NOTE_RE.fullmatch(path.name):
        return "dated research notes must remain local"

    lowered_parts = {part.lower() for part in parts}
    if ".lancedb" in lowered_parts or any(part.endswith(".lancedb") for part in lowered_parts):
        return "LanceDB indexes are generated local data"
    if any(part.endswith(".extracted") for part in lowered_parts):
        return "extracted reference trees are local data"

    if path.suffix.lower() in BLOCKED_SUFFIXES:
        return f"{path.suffix} files are not part of the public framework"

    return None


def _git_paths(repo_root: str, tracked: bool) -> List[str]:
    command = ["git", "ls-files", "-z"] if tracked else [
        "git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"
    ]
    result = subprocess.run(
        command,
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def find_violations(paths: Iterable[str]) -> List[str]:
    violations: List[str] = []
    for path in paths:
        reason = violation_reason(path)
        if reason:
            violations.append(f"{path}: {reason}")
    return violations


def load_private_terms(repo_root: Path) -> tuple[List[str], List[str]]:
    """Load exact private terms without ever returning them in diagnostics."""

    terms: List[str] = []
    errors: List[str] = []
    registry = repo_root / "projects.local.json"
    if registry.is_file():
        try:
            data = json.loads(registry.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"projects.local.json: cannot load private content audit metadata: {exc}")
        else:
            projects = data.get("projects", []) if isinstance(data, dict) else []
            if isinstance(projects, list):
                for project in projects:
                    if not isinstance(project, dict):
                        continue
                    for field, minimum in (("path", 4), ("title", 6), ("description", 12)):
                        value = project.get(field)
                        if isinstance(value, str) and len(value.strip()) >= minimum:
                            terms.append(value.strip())

    private_terms = repo_root / PRIVATE_TERMS_FILE
    if private_terms.is_file():
        try:
            for raw in private_terms.read_text(encoding="utf-8").splitlines():
                value = raw.strip()
                if value and not value.startswith("#") and len(value) >= 4:
                    terms.append(value)
        except OSError as exc:
            errors.append(f"{PRIVATE_TERMS_FILE}: cannot load private content audit terms: {exc}")

    deduplicated = list(dict.fromkeys(term.casefold() for term in terms))
    return deduplicated, errors


def sensitive_content_reasons(text: str, private_terms: Sequence[str]) -> List[str]:
    reasons: List[str] = []
    folded = text.casefold()
    if any(term in folded for term in private_terms):
        reasons.append("contains text copied from private project metadata or the local private-term list")
    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            reasons.append(f"contains a possible {label}")
    return reasons


def _content_for_path(repo_root: Path, path: str, staged: bool) -> Optional[str]:
    suffix = PurePosixPath(path).suffix.lower()
    if suffix not in TEXT_SUFFIXES:
        return None
    try:
        if staged:
            result = subprocess.run(
                ["git", "show", f":{path}"],
                cwd=repo_root,
                check=True,
                capture_output=True,
            )
            payload = result.stdout
        else:
            payload = (repo_root / path).read_bytes()
    except (OSError, subprocess.CalledProcessError):
        return None
    if len(payload) > 2 * 1024 * 1024:
        return None
    return payload.decode("utf-8", errors="replace")


def content_violations(repo_root: Path, paths: Sequence[str], staged: bool) -> List[str]:
    private_terms, errors = load_private_terms(repo_root)
    violations = list(errors)
    for path in paths:
        text = _content_for_path(repo_root, path, staged)
        if text is None:
            continue
        for reason in sensitive_content_reasons(text, private_terms):
            violations.append(f"{path}: {reason}")
    return violations


def public_registry_violations(repo_root: str) -> List[str]:
    registry_path = Path(repo_root) / "projects.json"
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"projects.json: cannot validate public registry: {exc}"]
    if data != EXPECTED_PUBLIC_REGISTRY:
        return [
            "projects.json: public registry must exactly match the allowlisted example record"
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tracked",
        action="store_true",
        help="check every tracked file instead of only staged additions and modifications",
    )
    parser.add_argument("--repo", default=".", help="repository root (default: current directory)")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    paths = _git_paths(str(repo_root), args.tracked)
    violations = find_violations(paths)
    violations.extend(public_registry_violations(str(repo_root)))
    violations.extend(content_violations(repo_root, paths, staged=not args.tracked))
    if violations:
        print("Private research data detected:")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    scope = "tracked files" if args.tracked else "staged changes"
    print(f"Public-scope check passed for {scope}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
