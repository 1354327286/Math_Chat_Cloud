#!/usr/bin/env python3
"""Create and verify controlled research-to-Lean formalization handoffs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Any, Iterable, Sequence

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.project_registry import RegistryError, project_record


SCHEMA_VERSION = 1
TASK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
PROJECT_RE = re.compile(r"^[a-z][a-z0-9_]*$")
DEFAULT_CONTEXT_FILES = ("research_state.md", "goal.md", "progress.md", "subgoal.md")
PACKET_FILENAMES = (
    "request.md",
    "context.md",
    "lemma_ledger.md",
    "source_map.md",
    "return_contract.md",
    "result_report.template.md",
    "source_query.template.md",
)
RESULT_KINDS = {"verification_result", "source_query"}
EXTERNAL_RESULTS_POLICIES = {"sorry-free", "documented-external-results"}


class HandoffError(ValueError):
    """Raised when a handoff violates its validation or scope contract."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _file_record(path: Path) -> dict[str, Any]:
    return {"size": path.stat().st_size, "sha256": _sha256(path)}


def _write_hash_receipt(path: Path, target: Path) -> None:
    path.write_text(f"{_sha256(target)}  {target.name}\n", encoding="ascii")


def _verify_hash_receipt(path: Path, target: Path) -> None:
    try:
        fields = path.read_text(encoding="ascii").strip().split()
    except (OSError, UnicodeDecodeError) as exc:
        raise HandoffError(f"cannot read hash receipt {path}: {exc}") from exc
    if fields != [_sha256(target), target.name]:
        raise HandoffError(f"hash receipt does not match {target.name}: {path}")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HandoffError(f"cannot read JSON file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise HandoffError(f"JSON root must be an object: {path}")
    return data


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _read_nonempty_text(path: Path, label: str) -> str:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError) as exc:
        raise HandoffError(f"cannot read {label} as UTF-8 text: {path}: {exc}") from exc
    if not value:
        raise HandoffError(f"{label} must be non-empty: {path}")
    return value


def _validate_task_id(task_id: str) -> str:
    if not TASK_ID_RE.fullmatch(task_id):
        raise HandoffError(f"unsafe task id: {task_id!r}")
    return task_id


def _safe_relative_file(root: Path, value: str | Path, label: str) -> Path:
    root = root.resolve(strict=True)
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise HandoffError(f"{label} does not exist: {candidate}") from exc
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise HandoffError(f"{label} escapes allowed root {root}: {value}") from exc
    if not resolved.is_file():
        raise HandoffError(f"{label} is not a regular file: {resolved}")
    return resolved


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def _registered_project(repo_root: Path, project_name: str) -> tuple[Path, dict[str, Any]]:
    repo_root = repo_root.resolve(strict=True)
    if not PROJECT_RE.fullmatch(project_name):
        raise HandoffError(f"unsafe project name: {project_name!r}")
    try:
        project = project_record(repo_root, project_name)
    except RegistryError as exc:
        raise HandoffError(str(exc)) from exc
    project_dir = (repo_root / project_name).resolve(strict=True)
    try:
        project_dir.relative_to(repo_root)
    except ValueError as exc:
        raise HandoffError(f"registered project escapes repository: {project_name}") from exc
    if not project_dir.is_dir():
        raise HandoffError(f"registered project is not a directory: {project_dir}")
    return project_dir, project


def _latest_daily_note(project_dir: Path) -> Path | None:
    notes = sorted(
        path
        for path in project_dir.glob("20??-??-??.md")
        if path.is_file() and re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", path.name)
    )
    return notes[-1] if notes else None


def _asset_template(repo_root: Path, name: str) -> Template:
    path = repo_root / "skills" / "formalization-handoff" / "assets" / name
    if not path.is_file():
        raise HandoffError(f"formalization template is missing: {path}")
    return Template(path.read_text(encoding="utf-8"))


def _slug(value: str) -> str:
    ascii_value = value.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
    return slug[:48] or "proof"


def _timestamp(now: datetime | None) -> datetime:
    value = now or datetime.now().astimezone()
    return value if value.tzinfo is not None else value.astimezone()


def _source_records(
    project_dir: Path,
    sources: Sequence[tuple[Path, str]],
) -> list[dict[str, Any]]:
    ordered: dict[str, dict[str, Any]] = {}
    for path, role in sources:
        relative = _relative(path, project_dir)
        if relative not in ordered:
            ordered[relative] = {
                "path": relative,
                "roles": [],
                "size": path.stat().st_size,
                "sha256": _sha256(path),
            }
        if role not in ordered[relative]["roles"]:
            ordered[relative]["roles"].append(role)
    return list(ordered.values())


def _context_sections(project_dir: Path, records: Sequence[dict[str, Any]]) -> str:
    sections: list[str] = []
    for record in records:
        path = project_dir / record["path"]
        roles = ", ".join(record["roles"])
        content = path.read_text(encoding="utf-8").strip() or "<empty file>"
        sections.append(
            f"## Source: `{record['path']}`\n\n"
            f"- Roles: {roles}\n"
            f"- SHA-256: `{record['sha256']}`\n\n"
            f"{content}"
        )
    return "\n\n".join(sections)


def _source_rows(records: Sequence[dict[str, Any]]) -> str:
    rows = ["| Relative path | Roles | Bytes | SHA-256 |", "| --- | --- | ---: | --- |"]
    for record in records:
        roles = ", ".join(record["roles"])
        rows.append(
            f"| `{record['path']}` | {roles} | {record['size']} | `{record['sha256']}` |"
        )
    return "\n".join(rows)


def _request_root(project_dir: Path) -> Path:
    return project_dir / "handoff" / "formalization" / "requests"


def _result_root(project_dir: Path) -> Path:
    return project_dir / "handoff" / "formalization" / "results"


def export_task(
    repo_root: Path,
    project_name: str,
    *,
    theorem_file: str | Path,
    proof_files: Sequence[str | Path],
    ledger_file: str | Path,
    audit_file: str | Path,
    output_file: str | Path,
    references: Sequence[str | Path] = (),
    extra_context: Sequence[str | Path] = (),
    external_results_policy: str,
    user_authorized: bool,
    audit_no_known_gaps: bool,
    slug: str | None = None,
    now: datetime | None = None,
) -> tuple[str, Path]:
    """Export one eligible proof as an immutable, self-contained request directory."""

    repo_root = repo_root.resolve(strict=True)
    project_dir, _ = _registered_project(repo_root, project_name)
    if not user_authorized:
        raise HandoffError("export requires explicit user authorization")
    if not audit_no_known_gaps:
        raise HandoffError("export requires an internal audit reporting no known gap")
    if external_results_policy not in EXTERNAL_RESULTS_POLICIES:
        raise HandoffError(
            "external-results policy must be sorry-free or documented-external-results"
        )
    if not proof_files:
        raise HandoffError("at least one proof source file is required")

    theorem_path = _safe_relative_file(project_dir, theorem_file, "theorem file")
    ledger_path = _safe_relative_file(project_dir, ledger_file, "lemma ledger")
    audit_path = _safe_relative_file(project_dir, audit_file, "audit file")
    output_path = _safe_relative_file(project_dir, output_file, "output contract")
    proof_paths = [
        _safe_relative_file(project_dir, value, "proof source") for value in proof_files
    ]
    reference_paths = [
        _safe_relative_file(project_dir, value, "reference source") for value in references
    ]
    extra_paths = [
        _safe_relative_file(project_dir, value, "extra context") for value in extra_context
    ]

    theorem = _read_nonempty_text(theorem_path, "theorem file")
    ledger = _read_nonempty_text(ledger_path, "lemma ledger")
    audit = _read_nonempty_text(audit_path, "audit file")
    output_contract = _read_nonempty_text(output_path, "output contract")

    sources: list[tuple[Path, str]] = [
        (theorem_path, "exact theorem"),
        (output_path, "requested Lean output"),
        (audit_path, "internal audit"),
        (ledger_path, "lemma ledger"),
    ]
    sources.extend((path, "proof source") for path in proof_paths)
    sources.extend((path, "reference") for path in reference_paths)
    sources.extend((path, "extra context") for path in extra_paths)
    for name in DEFAULT_CONTEXT_FILES:
        path = project_dir / name
        if not path.is_file():
            raise HandoffError(f"registered problem is missing required state file: {path}")
        sources.append((path.resolve(strict=True), "project state"))
    latest_note = _latest_daily_note(project_dir)
    if latest_note is not None:
        sources.append((latest_note.resolve(strict=True), "latest dated note"))
    records = _source_records(project_dir, sources)

    timestamp = _timestamp(now)
    created_at = timestamp.isoformat(timespec="seconds")
    task_base = f"{timestamp:%Y%m%d-%H%M%S}-{_slug(slug or theorem)}"
    requests = _request_root(project_dir)
    requests.mkdir(parents=True, exist_ok=True)
    task_id = task_base
    suffix = 2
    while (requests / task_id).exists():
        task_id = f"{task_base}-{suffix}"
        suffix += 1
    _validate_task_id(task_id)

    temporary = Path(tempfile.mkdtemp(prefix=".tmp-formalization-", dir=requests))
    destination = requests / task_id
    try:
        rendered: dict[str, str] = {
            "request.md": _asset_template(repo_root, "request.md").substitute(
                task_id=task_id,
                project_name=project_name,
                created_at=created_at,
                external_results_policy=external_results_policy,
                theorem=theorem,
                output_contract=output_contract,
                audit=audit,
            ),
            "context.md": _asset_template(repo_root, "context.md").substitute(
                context_sections=_context_sections(project_dir, records)
            ),
            "lemma_ledger.md": _asset_template(repo_root, "lemma_ledger.md").substitute(
                source_path=_relative(ledger_path, project_dir),
                source_sha256=_sha256(ledger_path),
                ledger=ledger,
            ),
            "source_map.md": _asset_template(repo_root, "source_map.md").substitute(
                source_root=str(repo_root),
                project_name=project_name,
                created_at=created_at,
                source_rows=_source_rows(records),
            ),
            "return_contract.md": _asset_template(repo_root, "return_contract.md").substitute(
                task_id=task_id
            ),
            "result_report.template.md": _asset_template(
                repo_root, "result_report.md"
            ).substitute(task_id=task_id),
            "source_query.template.md": _asset_template(repo_root, "source_query.md").substitute(
                task_id=task_id
            ),
        }
        for name, content in rendered.items():
            (temporary / name).write_text(content.rstrip() + "\n", encoding="utf-8")

        packet_files = {name: _file_record(temporary / name) for name in PACKET_FILENAMES}
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "task_id": task_id,
            "project": project_name,
            "created_at": created_at,
            "status": "exported",
            "external_results_policy": external_results_policy,
            "source_repository": str(repo_root),
            "source_files": records,
            "packet_files": packet_files,
        }
        _write_json(temporary / "manifest.json", manifest)
        _write_hash_receipt(temporary / "manifest.sha256", temporary / "manifest.json")
        temporary.replace(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return task_id, destination


def _load_packet_manifest(packet_dir: Path, expected_task_id: str) -> dict[str, Any]:
    _verify_hash_receipt(packet_dir / "manifest.sha256", packet_dir / "manifest.json")
    manifest = _read_json(packet_dir / "manifest.json")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise HandoffError("unsupported request manifest schema")
    if manifest.get("task_id") != expected_task_id:
        raise HandoffError("request manifest task id does not match its directory")
    if manifest.get("status") != "exported":
        raise HandoffError("request manifest status must remain exported")
    packet_files = manifest.get("packet_files")
    if not isinstance(packet_files, dict) or set(packet_files) != set(PACKET_FILENAMES):
        raise HandoffError("request manifest has an unexpected packet file set")
    actual_files = {
        path.relative_to(packet_dir).as_posix()
        for path in packet_dir.rglob("*")
        if path.is_file() and path.name not in {"manifest.json", "manifest.sha256"}
    }
    if actual_files != set(PACKET_FILENAMES):
        raise HandoffError("request directory contains missing or unexpected files")
    for name, expected in packet_files.items():
        path = packet_dir / name
        if not isinstance(expected, dict) or _file_record(path) != expected:
            raise HandoffError(f"request packet file changed after export: {name}")
    return manifest


def _verify_live_sources(project_dir: Path, manifest: dict[str, Any]) -> None:
    source_files = manifest.get("source_files")
    if not isinstance(source_files, list) or not source_files:
        raise HandoffError("request manifest has no source files")
    for record in source_files:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise HandoffError("request manifest has an invalid source record")
        path = _safe_relative_file(project_dir, record["path"], "manifest source")
        current = _file_record(path)
        expected = {"size": record.get("size"), "sha256": record.get("sha256")}
        if current != expected:
            raise HandoffError(f"source drift detected: {record['path']}")


def _verify_manifest_live_source(manifest: dict[str, Any]) -> None:
    source_root = manifest.get("source_repository")
    project_name = manifest.get("project")
    if not isinstance(source_root, str) or not isinstance(project_name, str):
        raise HandoffError("request manifest has no valid source location")
    try:
        repo_root = Path(source_root).resolve(strict=True)
    except OSError as exc:
        raise HandoffError(f"source repository is unavailable: {source_root}") from exc
    project_dir, _ = _registered_project(repo_root, project_name)
    _verify_live_sources(project_dir, manifest)


def verify_task(
    repo_root: Path,
    project_name: str,
    task_id: str,
    *,
    check_sources: bool = True,
) -> tuple[Path, dict[str, Any]]:
    repo_root = repo_root.resolve(strict=True)
    project_dir, _ = _registered_project(repo_root, project_name)
    task_id = _validate_task_id(task_id)
    packet_dir = _request_root(project_dir) / task_id
    if not packet_dir.is_dir():
        raise HandoffError(f"formalization request does not exist: {packet_dir}")
    manifest = _load_packet_manifest(packet_dir, task_id)
    if manifest.get("project") != project_name:
        raise HandoffError("request belongs to a different registered problem")
    if check_sources:
        _verify_live_sources(project_dir, manifest)
    return packet_dir, manifest


def _validate_lean_root(lean_root: Path) -> Path:
    try:
        root = lean_root.resolve(strict=True)
    except OSError as exc:
        raise HandoffError(f"Lean repository does not exist: {lean_root}") from exc
    if not root.is_dir():
        raise HandoffError(f"Lean root is not a directory: {root}")
    required = ("AGENTS.md", "lean-toolchain", ".archon", ".git")
    missing = [name for name in required if not (root / name).exists()]
    if not (root / "lakefile.toml").is_file() and not (root / "lakefile.lean").is_file():
        missing.append("lakefile.toml or lakefile.lean")
    if missing:
        raise HandoffError(f"Lean root is missing required markers: {', '.join(missing)}")
    return root


def stage_task(
    repo_root: Path,
    project_name: str,
    task_id: str,
    lean_root: Path,
) -> Path:
    packet_dir, _ = verify_task(repo_root, project_name, task_id, check_sources=True)
    root = _validate_lean_root(lean_root)
    inbox = root / ".archon" / "formalization_inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    destination = inbox / _validate_task_id(task_id)
    if destination.exists():
        raise HandoffError(f"staged task already exists; refusing overwrite: {destination}")
    temporary = Path(tempfile.mkdtemp(prefix=".tmp-stage-", dir=inbox))
    try:
        shutil.copytree(packet_dir, temporary, dirs_exist_ok=True)
        _load_packet_manifest(temporary, task_id)
        temporary.replace(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return destination


def _safe_lean_input(root: Path, value: str | Path, label: str) -> Path:
    path = _safe_relative_file(root, value, label)
    relative = path.relative_to(root)
    if relative.parts and relative.parts[0] in {".git", ".lake"}:
        raise HandoffError(f"{label} may not come from generated or Git internals: {path}")
    if len(relative.parts) >= 2 and relative.parts[:2] in {
        (".archon", "formalization_inbox"),
        (".archon", "formalization_outbox"),
    }:
        raise HandoffError(f"{label} may not be copied from an inbox or outbox: {path}")
    return path


def prepare_result(
    lean_root: Path,
    task_id: str,
    *,
    kind: str,
    report_file: str | Path,
    lean_files: Sequence[str | Path] = (),
    source_query_file: str | Path | None = None,
    now: datetime | None = None,
) -> Path:
    root = _validate_lean_root(lean_root)
    task_id = _validate_task_id(task_id)
    if kind not in RESULT_KINDS:
        raise HandoffError(f"unsupported result kind: {kind}")
    inbox = root / ".archon" / "formalization_inbox" / task_id
    if not inbox.is_dir():
        raise HandoffError(f"staged request does not exist: {inbox}")
    request_manifest = _load_packet_manifest(inbox, task_id)
    request_manifest_hash = _sha256(inbox / "manifest.json")

    report = _safe_lean_input(root, report_file, "result report")
    _read_nonempty_text(report, "result report")
    lean_paths = [_safe_lean_input(root, value, "Lean evidence") for value in lean_files]
    for path in lean_paths:
        if path.suffix.lower() != ".lean":
            raise HandoffError(f"Lean evidence must have .lean suffix: {path}")
    query: Path | None = None
    if source_query_file is not None:
        query = _safe_lean_input(root, source_query_file, "source query")
        _read_nonempty_text(query, "source query")
    if kind == "verification_result" and not lean_paths:
        raise HandoffError("verification_result requires at least one Lean file")
    if kind == "source_query" and query is None:
        raise HandoffError("source_query result requires --source-query")

    source_status = "unchanged"
    try:
        _verify_manifest_live_source(request_manifest)
    except HandoffError as exc:
        source_status = str(exc)
        if kind == "verification_result":
            raise

    outbox = root / ".archon" / "formalization_outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    destination = outbox / task_id
    if destination.exists():
        raise HandoffError(f"return task already exists; refusing overwrite: {destination}")
    temporary = Path(tempfile.mkdtemp(prefix=".tmp-result-", dir=outbox))
    try:
        shutil.copyfile(report, temporary / "result_report.md")
        if query is not None:
            shutil.copyfile(query, temporary / "source_query.md")
        for path in lean_paths:
            relative = path.relative_to(root)
            target = temporary / "lean" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        files = {
            path.relative_to(temporary).as_posix(): _file_record(path)
            for path in sorted(temporary.rglob("*"))
            if path.is_file()
        }
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "task_id": task_id,
            "kind": kind,
            "created_at": _timestamp(now).isoformat(timespec="seconds"),
            "request_manifest_sha256": request_manifest_hash,
            "source_status": source_status,
            "files": files,
        }
        _write_json(temporary / "result_manifest.json", manifest)
        _write_hash_receipt(
            temporary / "result_manifest.sha256", temporary / "result_manifest.json"
        )
        temporary.replace(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return destination


def _load_result_manifest(result_dir: Path, task_id: str) -> dict[str, Any]:
    _verify_hash_receipt(
        result_dir / "result_manifest.sha256", result_dir / "result_manifest.json"
    )
    manifest = _read_json(result_dir / "result_manifest.json")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise HandoffError("unsupported result manifest schema")
    if manifest.get("task_id") != task_id:
        raise HandoffError("result manifest task id does not match its directory")
    if manifest.get("kind") not in RESULT_KINDS:
        raise HandoffError("result manifest has an unsupported kind")
    files = manifest.get("files")
    if not isinstance(files, dict) or "result_report.md" not in files:
        raise HandoffError("result manifest has no result report")
    if manifest.get("kind") == "source_query" and "source_query.md" not in files:
        raise HandoffError("source_query result has no source_query.md")
    if manifest.get("kind") == "verification_result" and not any(
        name.startswith("lean/") and name.endswith(".lean") for name in files
    ):
        raise HandoffError("verification_result has no Lean evidence")
    actual_files = {
        path.relative_to(result_dir).as_posix()
        for path in result_dir.rglob("*")
        if path.is_file()
        and path.name not in {"result_manifest.json", "result_manifest.sha256"}
    }
    if actual_files != set(files):
        raise HandoffError("result directory contains missing or unexpected files")
    for name, expected in files.items():
        path = result_dir / Path(name)
        if not isinstance(expected, dict) or _file_record(path) != expected:
            raise HandoffError(f"Lean return file changed after preparation: {name}")
    return manifest


def import_result(
    repo_root: Path,
    project_name: str,
    task_id: str,
    lean_root: Path,
    *,
    now: datetime | None = None,
) -> Path:
    repo_root = repo_root.resolve(strict=True)
    project_dir, _ = _registered_project(repo_root, project_name)
    packet_dir, request_manifest = verify_task(
        repo_root, project_name, task_id, check_sources=False
    )
    root = _validate_lean_root(lean_root)
    inbox = root / ".archon" / "formalization_inbox" / task_id
    if not inbox.is_dir():
        raise HandoffError(f"staged request does not exist: {inbox}")
    _load_packet_manifest(inbox, task_id)
    source_manifest_hash = _sha256(packet_dir / "manifest.json")
    if _sha256(inbox / "manifest.json") != source_manifest_hash:
        raise HandoffError("staged request differs from the source request")

    outbox = root / ".archon" / "formalization_outbox" / task_id
    if not outbox.is_dir():
        raise HandoffError(f"Lean return does not exist: {outbox}")
    result_manifest = _load_result_manifest(outbox, task_id)
    if result_manifest.get("request_manifest_sha256") != source_manifest_hash:
        raise HandoffError("Lean return belongs to a different request manifest")
    source_status = "unchanged"
    try:
        _verify_live_sources(project_dir, request_manifest)
    except HandoffError as exc:
        source_status = str(exc)
        if result_manifest["kind"] == "verification_result":
            raise

    results = _result_root(project_dir)
    results.mkdir(parents=True, exist_ok=True)
    destination = results / task_id
    if destination.exists():
        raise HandoffError(f"imported result already exists; refusing overwrite: {destination}")
    temporary = Path(tempfile.mkdtemp(prefix=".tmp-import-", dir=results))
    try:
        shutil.copytree(outbox, temporary / "raw")
        result_manifest_hash = _sha256(outbox / "result_manifest.json")
        review = _asset_template(repo_root, "review.md").substitute(
            task_id=task_id,
            project_name=project_name,
            imported_at=_timestamp(now).isoformat(timespec="seconds"),
            result_kind=result_manifest["kind"],
            source_status=source_status,
            request_manifest_sha256=source_manifest_hash,
            result_manifest_sha256=result_manifest_hash,
        )
        (temporary / "review.md").write_text(review.rstrip() + "\n", encoding="utf-8")
        temporary.replace(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return destination


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="export an eligible proof request")
    export_parser.add_argument("project")
    export_parser.add_argument("--theorem-file", required=True)
    export_parser.add_argument("--proof-file", action="append", required=True, dest="proof_files")
    export_parser.add_argument("--ledger-file", required=True)
    export_parser.add_argument("--audit-file", required=True)
    export_parser.add_argument("--output-file", required=True)
    export_parser.add_argument("--reference", action="append", default=[])
    export_parser.add_argument("--context", action="append", default=[])
    export_parser.add_argument(
        "--external-results-policy",
        choices=sorted(EXTERNAL_RESULTS_POLICIES),
        required=True,
    )
    export_parser.add_argument("--user-authorized", action="store_true", required=True)
    export_parser.add_argument("--audit-no-known-gaps", action="store_true", required=True)
    export_parser.add_argument("--slug")

    verify_parser = subparsers.add_parser("verify", help="verify a request and live sources")
    verify_parser.add_argument("project")
    verify_parser.add_argument("task_id")

    stage_parser = subparsers.add_parser("stage", help="stage a verified request to Lean")
    stage_parser.add_argument("project")
    stage_parser.add_argument("task_id")
    stage_parser.add_argument("--lean-root", type=Path, required=True)

    prepare_parser = subparsers.add_parser(
        "prepare-result", help="prepare a hashed Lean-side return"
    )
    prepare_parser.add_argument("task_id")
    prepare_parser.add_argument("--lean-root", type=Path, required=True)
    prepare_parser.add_argument("--kind", choices=sorted(RESULT_KINDS), required=True)
    prepare_parser.add_argument("--report", required=True)
    prepare_parser.add_argument("--source-query")
    prepare_parser.add_argument("--lean-file", action="append", default=[], dest="lean_files")

    import_parser = subparsers.add_parser("import", help="import raw Lean-side evidence")
    import_parser.add_argument("project")
    import_parser.add_argument("task_id")
    import_parser.add_argument("--lean-root", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    repo_root = _repo_root_from_script()
    try:
        if args.command == "export":
            task_id, destination = export_task(
                repo_root,
                args.project,
                theorem_file=args.theorem_file,
                proof_files=args.proof_files,
                ledger_file=args.ledger_file,
                audit_file=args.audit_file,
                output_file=args.output_file,
                references=args.reference,
                extra_context=args.context,
                external_results_policy=args.external_results_policy,
                user_authorized=args.user_authorized,
                audit_no_known_gaps=args.audit_no_known_gaps,
                slug=args.slug,
            )
            print(f"Exported {task_id}: {destination}")
        elif args.command == "verify":
            destination, _ = verify_task(repo_root, args.project, args.task_id)
            print(f"Verified request and live sources: {destination}")
        elif args.command == "stage":
            destination = stage_task(
                repo_root, args.project, args.task_id, args.lean_root
            )
            print(f"Staged immutable request: {destination}")
        elif args.command == "prepare-result":
            destination = prepare_result(
                args.lean_root,
                args.task_id,
                kind=args.kind,
                report_file=args.report,
                lean_files=args.lean_files,
                source_query_file=args.source_query,
            )
            print(f"Prepared Lean return: {destination}")
        elif args.command == "import":
            destination = import_result(
                repo_root, args.project, args.task_id, args.lean_root
            )
            print(f"Imported raw Lean evidence for audit: {destination}")
        else:  # pragma: no cover - argparse enforces the command set.
            raise AssertionError(args.command)
    except (HandoffError, OSError) as exc:
        print(f"formalization handoff failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
