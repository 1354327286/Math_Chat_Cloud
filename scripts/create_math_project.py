#!/usr/bin/env python3
"""Create a local math-research project with the repository's standard layout."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.project_registry import (
    PROJECT_ROLES,
    RegistryError,
    add_local_project,
    find_project,
)


PROJECT_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
MEMORY_FILES = {
    "immediate_conclusions.md": "# Immediate Conclusions\n",
    "toy_examples.md": "# Toy Examples\n",
    "counterexamples.md": "# Counterexamples\n",
    "failed_paths.md": "# Failed Paths\n",
    "subgoals_state.md": "# Subgoals State\n",
    "search_results.md": "# Search Results\n",
    "events.md": "# Events\n",
}
EMAIL_FILES = {
    "README.md": (
        "# Private Academic Correspondence\n\n"
        "Keep contacts, incoming messages, drafts, actual sent text, contribution "
        "provenance, and source attachments here. See "
        "[the email workflow](../../docs/email_workflow.md). A draft is not sent; "
        "a sent proposal is not mutual agreement. Record the exact manuscript/version "
        "and distinguish work before the exchange, the correspondent's contribution, "
        "and later development. Check [the index](index.md) at manuscript "
        "finalization/release for version-scoped obligations and attribution.\n"
    ),
    "contacts.md": (
        "# Academic Contacts\n\n"
        "No contacts recorded yet.\n\n"
        "| Name | Verified address | Affiliation | Verification date/source | "
        "Relevant projects |\n"
        "| --- | --- | --- | --- | --- |\n"
    ),
    "index.md": (
        "# Correspondence Index\n\n"
        "No correspondence recorded yet.\n\n"
        "| Date/thread | Artifact/version | Message status and evidence | "
        "Obligation/condition | Owner/due or review point | Resolution/evidence |\n"
        "| --- | --- | --- | --- | --- | --- |\n\n"
        "For each substantive exchange, link the work before the exchange, "
        "the received contribution, and later development. Keep conditional "
        "obligations distinct from present commitments; state the exact trigger "
        "and the evidence that it occurred. Do not infer consent, delivery, "
        "collaboration, priority, or agreement from a draft or silence.\n"
    ),
}


def _write(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def create_project(repo_root: Path, name: str, title: str) -> Path:
    if not PROJECT_NAME_RE.fullmatch(name):
        raise ValueError("name must match ^[a-z][a-z0-9_]*$")

    project_dir = repo_root / name
    if project_dir.exists():
        raise FileExistsError(f"project already exists: {project_dir}")

    # Validate and read both required templates before creating any directory.
    # A missing/unreadable template must not leave a partial project behind.
    templates = {}
    for filename in ("research_state.md", "subgoal_plan.md"):
        template_path = repo_root / "templates" / filename
        if not template_path.is_file():
            raise FileNotFoundError(f"missing template: {template_path}")
        templates[filename] = template_path.read_text(encoding="utf-8")

    for child in (
        "notes", "memory", "refs", "downloads", "email", "email/attachments", "handoff"
    ):
        (project_dir / child).mkdir(parents=True, exist_ok=False)
        _write(project_dir / child / ".gitkeep", "")

    _write(
        project_dir / "README.md",
        f"# {title}\n\n"
        "This directory represents one mathematical research problem. "
        "Research notes and references remain local and are ignored by Git.\n",
    )
    _write(project_dir / ".gitkeep", "")

    state = templates["research_state.md"].replace(
        "<short descriptive title>", title
    )
    _write(project_dir / "research_state.md", state)
    _write(project_dir / "goal.md", f"# Goal\n\n## Main Problem\n\n<state {title} precisely>\n")
    _write(project_dir / "progress.md", "# Progress\n")
    _write(
        project_dir / "subgoal.md",
        templates["subgoal_plan.md"].replace("<short descriptive title>", title),
    )

    for filename, heading in MEMORY_FILES.items():
        _write(project_dir / "memory" / filename, heading)
    for filename, content in EMAIL_FILES.items():
        _write(project_dir / "email" / filename, content)

    catalog_template = repo_root / "templates" / "reference_catalog.json"
    if catalog_template.is_file():
        _write(
            project_dir / "refs" / "catalog.json",
            catalog_template.read_text(encoding="utf-8"),
        )
    _write(
        project_dir / "refs" / "README.md",
        "# Local Reference Library\n\n"
        "Store PDFs in `papers/`, version-matched TeX in `sources/`, and provenance "
        "in `catalog.json`. See `../../docs/reference_workflow.md`.\n",
    )

    return project_dir


def register_project(
    repo_root: Path,
    name: str,
    title: str,
    role: str,
    description: str,
) -> None:
    if role not in PROJECT_ROLES:
        raise ValueError(f"unsupported project role: {role}")

    try:
        added = add_local_project(
            repo_root,
            {
                "path": name,
                "title": title,
                "role": role,
                "description": description,
            },
        )
    except RegistryError as exc:
        raise ValueError(str(exc)) from exc
    if not added:
        raise ValueError(f"project already registered: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="ASCII directory slug, for example my_math_problem")
    parser.add_argument("--title", required=True, help="human-readable mathematical problem title")
    parser.add_argument("--role", choices=sorted(PROJECT_ROLES), default="active")
    parser.add_argument("--description", default="", help="one-line project description")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    title = args.title.strip()
    if not title:
        parser.error("--title must be non-empty")
    if args.description and "\n" in args.description:
        parser.error("--description must be one line")

    try:
        if find_project(repo_root, args.name) is not None:
            parser.error(f"project already registered: {args.name}")
    except RegistryError as exc:
        parser.error(str(exc))

    project_dir = create_project(repo_root, args.name, title)
    register_project(
        repo_root,
        args.name,
        title,
        args.role,
        args.description.strip(),
    )
    print(project_dir)
    print("Registered in private projects.local.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
