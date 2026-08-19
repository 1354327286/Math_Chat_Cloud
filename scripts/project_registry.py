"""Load the public project template plus an optional private local overlay."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


PUBLIC_REGISTRY_NAME = "projects.json"
LOCAL_REGISTRY_NAME = "projects.local.json"
SCHEMA_VERSION = 1
PROJECT_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
PROJECT_ROLES = {"primary", "secondary", "active", "exploring", "paused", "example"}
PROJECT_FIELDS = ("path", "title", "role", "description")


class RegistryError(ValueError):
    """The public/local registry pair is missing, malformed, or ambiguous."""


def _read_registry(path: Path, *, required: bool) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise RegistryError(f"project registry does not exist: {path}")
        return {"schema_version": SCHEMA_VERSION, "projects": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"cannot read project registry {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise RegistryError(f"invalid project registry schema: {path}")
    if not isinstance(data.get("projects"), list):
        raise RegistryError(f"project registry has no projects list: {path}")
    return data


def normalize_project_record(record: Any, *, source: str = "registry") -> dict[str, str]:
    if not isinstance(record, dict):
        raise RegistryError(f"project record must be an object: {source}")
    missing = [field for field in PROJECT_FIELDS if field not in record]
    if missing:
        raise RegistryError(f"project record is missing {', '.join(missing)}: {source}")
    path = record.get("path")
    title = record.get("title")
    role = record.get("role")
    description = record.get("description")
    if not isinstance(path, str) or not PROJECT_NAME_RE.fullmatch(path):
        raise RegistryError(f"project path is not a safe ASCII slug: {source}")
    if (
        not isinstance(title, str)
        or not title.strip()
        or "\n" in title
        or "\r" in title
    ):
        raise RegistryError(f"project title must be one non-empty line: {source}")
    if role not in PROJECT_ROLES:
        raise RegistryError(f"unsupported project role {role!r}: {source}")
    if (
        not isinstance(description, str)
        or "\n" in description
        or "\r" in description
    ):
        raise RegistryError(f"project description must be one line: {source}")
    return {
        "path": path,
        "title": title.strip(),
        "role": role,
        "description": description.strip(),
    }


def load_registry(repo_root: Path, *, include_local: bool = True) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    sources = [(repo_root / PUBLIC_REGISTRY_NAME, True)]
    if include_local:
        sources.append((repo_root / LOCAL_REGISTRY_NAME, False))

    projects: list[dict[str, str]] = []
    seen: dict[str, str] = {}
    for path, required in sources:
        data = _read_registry(path, required=required)
        for index, raw in enumerate(data["projects"]):
            record = normalize_project_record(raw, source=f"{path.name}:projects[{index}]")
            slug = record["path"]
            if slug in seen:
                raise RegistryError(
                    f"project {slug!r} occurs in both {seen[slug]} and {path.name}"
                )
            seen[slug] = path.name
            projects.append(record)
    return {"schema_version": SCHEMA_VERSION, "projects": projects}


def project_record(repo_root: Path, slug: str) -> dict[str, str]:
    if not PROJECT_NAME_RE.fullmatch(slug):
        raise RegistryError(f"unsafe project slug: {slug}")
    for record in load_registry(repo_root)["projects"]:
        if record["path"] == slug:
            return record
    raise RegistryError(f"project is not registered: {slug}")


def find_project(repo_root: Path, slug: str) -> dict[str, str] | None:
    if not PROJECT_NAME_RE.fullmatch(slug):
        raise RegistryError(f"unsafe project slug: {slug}")
    for record in load_registry(repo_root)["projects"]:
        if record["path"] == slug:
            return record
    return None


def add_local_project(repo_root: Path, record: Any) -> bool:
    """Add one exact record to the ignored local overlay; return False if identical."""

    repo_root = repo_root.resolve()
    normalized = normalize_project_record(record, source="new local project")
    public = load_registry(repo_root, include_local=False)
    for existing in public["projects"]:
        if existing["path"] == normalized["path"]:
            if existing == normalized:
                return False
            raise RegistryError(
                f"project conflicts with public registry: {normalized['path']}"
            )

    local_path = repo_root / LOCAL_REGISTRY_NAME
    local = _read_registry(local_path, required=False)
    normalized_local = [
        normalize_project_record(item, source=f"{LOCAL_REGISTRY_NAME}:projects[{index}]")
        for index, item in enumerate(local["projects"])
    ]
    for existing in normalized_local:
        if existing["path"] == normalized["path"]:
            if existing == normalized:
                return False
            raise RegistryError(
                f"project conflicts with local registry: {normalized['path']}"
            )

    normalized_local.append(normalized)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "projects": normalized_local,
    }
    local_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{LOCAL_REGISTRY_NAME}-",
        suffix=".tmp",
        dir=local_path.parent,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, local_path)
    finally:
        Path(temporary_name).unlink(missing_ok=True)
    return True
