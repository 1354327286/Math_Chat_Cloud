#!/usr/bin/env python3
"""Fail when private research data are staged or tracked by Git."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Iterable, List, Optional


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

    violations = find_violations(_git_paths(args.repo, args.tracked))
    violations.extend(public_registry_violations(args.repo))
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
