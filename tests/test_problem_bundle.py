import json
import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.problem_bundle import (
    BundleError,
    MANIFEST_NAME,
    export_bundle,
    restore_bundle,
    verify_bundle,
)


class ProblemBundleTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.source_repo = self.root / "source"
        self.restore_repo = self.root / "restore"
        self._make_public_checkout(self.source_repo)
        self._make_public_checkout(self.restore_repo)

        project = self.source_repo / "sample_problem"
        project.mkdir()
        (project / "README.md").write_text("# Private project\n", encoding="utf-8")
        (self.source_repo / "projects.local.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "projects": [
                        {
                            "path": "sample_problem",
                            "title": "Sample Problem",
                            "role": "active",
                            "description": "Fixture",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (project / "research_state.md").write_text("# State\n", encoding="utf-8")
        (project / "goal.md").write_text(
            "# Goal\n\nSee [the source report](../inbox/related.md).\n",
            encoding="utf-8",
        )
        (project / "2026-08-07.md").write_text("# Daily\n", encoding="utf-8")
        (project / "memory").mkdir()
        (project / "memory" / "events.md").write_text("# Events\n", encoding="utf-8")
        (project / "notes").mkdir()
        (project / "notes" / "proof.tex").write_text("formal source", encoding="utf-8")
        (project / "notes" / "proof.reader.md").write_text("generated", encoding="utf-8")
        (project / "notes" / "proof.aux").write_text("generated", encoding="utf-8")
        (project / "refs" / "papers").mkdir(parents=True)
        (project / "refs" / "catalog.json").write_text('{"schema_version": 1}\n', encoding="utf-8")
        (project / "refs" / "papers" / "paper.pdf").write_bytes(b"%PDF fixture")
        (project / "refs" / ".lancedb").mkdir()
        (project / "refs" / ".lancedb" / "index.bin").write_bytes(b"index")
        (project / "downloads").mkdir()
        (project / "downloads" / "source.tar.gz").write_bytes(b"archive")
        (self.source_repo / "inbox" / "related.md").write_text("original report", encoding="utf-8")
        (self.source_repo / "inbox" / "extra.md").write_text("explicit supplement", encoding="utf-8")
        (self.source_repo / "inbox" / "unrelated.md").write_text("not selected", encoding="utf-8")
        self.bundle = self.root / "sample.zip"

    def tearDown(self):
        self.tempdir.cleanup()

    @staticmethod
    def _make_public_checkout(root: Path) -> None:
        root.mkdir(parents=True)
        (root / "inbox").mkdir()
        (root / "projects.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "projects": [
                        {
                            "path": "example_math_problem",
                            "title": "Example math problem",
                            "role": "example",
                            "description": "Public fixture",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def _export(self, inbox_values=()) -> dict:
        destination, manifest = export_bundle(
            self.source_repo,
            "sample_problem",
            inbox_values,
            self.bundle,
        )
        self.assertEqual(destination, self.bundle.resolve())
        return manifest

    def _add_email_fixture(self) -> dict[str, bytes]:
        files = {
            "sample_problem/email/README.md": b"# Private correspondence\n",
            "sample_problem/email/contacts.md": b"Synthetic contact; address not verified.\n",
            "sample_problem/email/index.md": (
                b"# Correspondence\n\n[Thread](2026-10-04_correspondent_topic.md)\n"
                b"Artifact: notes/manuscript/paper.tex, draft revision.\n"
                b"Status: reply draft; no sent proposal or mutual agreement.\n"
                b"Condition: check attribution before finalization; unresolved.\n"
            ),
            "sample_problem/email/2026-10-04_correspondent_topic.md": (
                b"# Contribution provenance\n\n"
                b"Before: original lemma. Received: suggested simplification.\n"
                b"After: AI-assisted analysis; needs verification.\n"
                b"Source: [raw message](attachments/thread/original.eml).\n"
                b"See [intake](../../inbox/email_intake/context.md) and "
                b"[source](../../inbox/email_intake/source.pdf).\n"
                b"Reply draft only; no sending evidence.\n"
            ),
            "sample_problem/email/attachments/thread/original.eml": (
                b"Subject: Synthetic contribution\r\n\r\nOriginal source text.\r\n"
            ),
            "sample_problem/email/attachments/thread/proof.pdf": b"%PDF-1.4\nfixture\x00\xff",
            "sample_problem/email/attachments/thread/screenshot.png": b"\x89PNG\r\n\x1a\nfixture",
            "inbox/email_intake/context.md": b"# Unprocessed original source\n",
            "inbox/email_intake/source.pdf": b"%PDF inbox fixture\x00",
        }
        for relative, content in files.items():
            path = self.source_repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        return files

    @staticmethod
    def _snapshot(root: Path) -> dict[str, bytes | None]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes() if path.is_file() else None
            for path in root.rglob("*")
        }

    def test_email_round_trip_preserves_provenance_attachments_and_inbox(self):
        files = self._add_email_fixture()
        manifest = self._export()
        entries = {entry["path"]: entry for entry in manifest["files"]}
        self.assertTrue(set(files).issubset(entries))
        for relative in files:
            expected_category = "project-email" if "/email/" in relative else "inbox-reference"
            self.assertEqual(entries[relative]["category"], expected_category)
        self.assertEqual(
            manifest["referenced_inbox"],
            ["inbox/email_intake/context.md", "inbox/email_intake/source.pdf", "inbox/related.md"],
        )
        self.assertNotIn("inbox/unrelated.md", entries)
        self.assertEqual(verify_bundle(self.bundle), manifest)

        restored = restore_bundle(self.bundle, self.restore_repo)
        self.assertEqual(restored["registry"], "create")
        for relative, content in files.items():
            with self.subTest(path=relative):
                self.assertEqual((self.restore_repo / relative).read_bytes(), content)
        self.assertEqual(
            json.loads((self.restore_repo / "projects.local.json").read_text()),
            json.loads((self.source_repo / "projects.local.json").read_text()),
        )
        snapshot = self._snapshot(self.restore_repo)
        repeated = restore_bundle(self.bundle, self.restore_repo)
        self.assertEqual(repeated["create"], 0)
        self.assertEqual(repeated["unchanged"], len(entries))
        self.assertEqual(repeated["registry"], "unchanged")
        self.assertEqual(self._snapshot(self.restore_repo), snapshot)

    def test_nested_manuscript_ledger_plan_and_tex_round_trip(self):
        files = {
            "THEOREM_LEDGER.md": b"# Theorem ledger\nCore result: needs verification.\n",
            "PAPER_PLAN.md": b"# Paper plan\nExact statement, proof, limitations.\n",
            "paper.tex": b"\\documentclass{article}\n\\begin{document}Draft\\end{document}\n",
        }
        manuscript = self.source_repo / "sample_problem" / "notes" / "manuscript"
        manuscript.mkdir()
        for name, content in files.items():
            (manuscript / name).write_bytes(content)
        manifest = self._export()
        paths = {entry["path"] for entry in manifest["files"]}
        restore_bundle(self.bundle, self.restore_repo)
        for name, content in files.items():
            relative = f"sample_problem/notes/manuscript/{name}"
            with self.subTest(path=relative):
                self.assertIn(relative, paths)
                self.assertEqual((self.restore_repo / relative).read_bytes(), content)

    def test_email_export_and_restore_dry_runs_write_nothing(self):
        self._add_email_fixture()
        output = self.root / "not-created" / "email.zip"
        source_before = self._snapshot(self.source_repo)
        destination, preview = export_bundle(
            self.source_repo, "sample_problem", (), output, dry_run=True
        )
        self.assertIsNone(destination)
        self.assertFalse(output.parent.exists())
        self.assertEqual(self._snapshot(self.source_repo), source_before)
        self.assertIn("project-email", {entry["category"] for entry in preview["files"]})
        self._export()
        restore_before = self._snapshot(self.restore_repo)
        summary = restore_bundle(self.bundle, self.restore_repo, dry_run=True)
        self.assertEqual(summary["registry"], "create")
        self.assertGreater(summary["create"], 0)
        self.assertEqual(self._snapshot(self.restore_repo), restore_before)

    def test_email_conflicts_preserve_every_file_and_registry(self):
        self._add_email_fixture()
        self._export()
        conflicts = [
            "sample_problem/email/index.md",
            "sample_problem/email/attachments/thread/original.eml",
        ]
        for relative in conflicts:
            path = self.restore_repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"Different local history; preserve me.\n")
        before = self._snapshot(self.restore_repo)
        with self.assertRaisesRegex(BundleError, "no files were written") as raised:
            restore_bundle(self.bundle, self.restore_repo)
        for relative in conflicts:
            self.assertIn(relative, str(raised.exception))
        self.assertEqual(self._snapshot(self.restore_repo), before)
        self.assertFalse((self.restore_repo / "projects.local.json").exists())

    def test_email_conflicts_respect_explicit_keep_and_overwrite(self):
        files = self._add_email_fixture()
        self._export()
        relative = "sample_problem/email/index.md"
        conflict = self.restore_repo / relative
        conflict.parent.mkdir(parents=True)
        conflict.write_bytes(b"Locally reconciled provenance.\n")
        summary = restore_bundle(self.bundle, self.restore_repo, keep_existing=True)
        self.assertEqual(summary["kept"], 1)
        self.assertEqual(summary["registry"], "create")
        self.assertEqual(conflict.read_bytes(), b"Locally reconciled provenance.\n")
        for path, content in files.items():
            if path != relative:
                self.assertEqual((self.restore_repo / path).read_bytes(), content)
        summary = restore_bundle(self.bundle, self.restore_repo, overwrite=True)
        self.assertEqual(summary["overwrite"], 1)
        self.assertEqual(conflict.read_bytes(), files[relative])

    def test_email_registry_conflict_blocks_all_conflict_modes(self):
        self._add_email_fixture()
        self._export()
        registry = json.loads((self.source_repo / "projects.local.json").read_text())
        registry["projects"][0]["description"] = "Incompatible project identity"
        (self.restore_repo / "projects.local.json").write_text(json.dumps(registry))
        before = self._snapshot(self.restore_repo)
        for mode in ({}, {"keep_existing": True}, {"overwrite": True}, {"dry_run": True}):
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(BundleError, "local registry; no files were written"):
                    restore_bundle(self.bundle, self.restore_repo, **mode)
                self.assertEqual(self._snapshot(self.restore_repo), before)

    def test_missing_email_inbox_reference_blocks_export(self):
        self._add_email_fixture()
        (self.source_repo / "inbox" / "email_intake" / "source.pdf").unlink()
        with self.assertRaisesRegex(BundleError, "references missing inbox path"):
            self._export()
        self.assertFalse(self.bundle.exists())

    def test_tampered_email_attachment_blocks_restore_before_writes(self):
        self._add_email_fixture()
        self._export()
        tampered = self.root / "tampered-email.zip"
        with zipfile.ZipFile(self.bundle) as source, zipfile.ZipFile(tampered, "w") as target:
            for name in source.namelist():
                data = source.read(name)
                if name.endswith("email/attachments/thread/original.eml"):
                    data = bytes([data[0] ^ 1]) + data[1:]
                target.writestr(name, data)
        before = self._snapshot(self.restore_repo)
        with self.assertRaisesRegex(BundleError, "SHA-256"):
            restore_bundle(tampered, self.restore_repo)
        self.assertEqual(self._snapshot(self.restore_repo), before)

    def test_email_export_rejects_symlinked_attachment(self):
        self._add_email_fixture()
        external = self.root / "outside.eml"
        external.write_bytes(b"Not part of this project")
        attachment = self.source_repo / "sample_problem" / "email" / "attachments" / "linked.eml"
        attachment.symlink_to(external)
        with self.assertRaisesRegex(BundleError, "Symbolic links are not allowed"):
            self._export()
        self.assertFalse(self.bundle.exists())

    def test_email_restore_rejects_symlinked_attachment_parent_before_writes(self):
        self._add_email_fixture()
        self._export()
        email = self.restore_repo / "sample_problem" / "email"
        email.mkdir(parents=True)
        public_target = self.restore_repo / "scripts"
        public_target.mkdir()
        (email / "attachments").symlink_to(public_target, target_is_directory=True)
        with self.assertRaisesRegex(BundleError, "symbolic-link parent"):
            restore_bundle(self.bundle, self.restore_repo)
        self.assertEqual(list(public_target.iterdir()), [])
        self.assertFalse((email / "README.md").exists())
        self.assertFalse((self.restore_repo / "projects.local.json").exists())

    def test_email_restore_rejects_file_as_attachment_parent_before_writes(self):
        self._add_email_fixture()
        self._export()
        email = self.restore_repo / "sample_problem" / "email"
        email.mkdir(parents=True)
        (email / "attachments").write_bytes(b"Existing file, not a directory.\n")
        before = self._snapshot(self.restore_repo)
        for mode in ({}, {"keep_existing": True}, {"overwrite": True}, {"dry_run": True}):
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(BundleError, "non-directory parent; no files were written"):
                    restore_bundle(self.bundle, self.restore_repo, **mode)
                self.assertEqual(self._snapshot(self.restore_repo), before)

    def test_round_trip_preserves_private_files_and_referenced_inbox(self):
        manifest = self._export()
        paths = {entry["path"] for entry in manifest["files"]}
        self.assertIn("sample_problem/research_state.md", paths)
        self.assertIn("sample_problem/notes/proof.tex", paths)
        self.assertIn("sample_problem/refs/papers/paper.pdf", paths)
        self.assertIn("sample_problem/downloads/source.tar.gz", paths)
        self.assertIn("inbox/related.md", paths)
        self.assertIn("sample_problem/README.md", paths)
        self.assertNotIn("sample_problem/notes/proof.reader.md", paths)
        self.assertNotIn("sample_problem/notes/proof.aux", paths)
        self.assertNotIn("sample_problem/refs/.lancedb/index.bin", paths)
        self.assertNotIn("inbox/unrelated.md", paths)
        self.assertNotIn("inbox/extra.md", paths)

        verified = verify_bundle(self.bundle)
        self.assertEqual(verified["totals"]["files"], len(paths))
        summary = restore_bundle(self.bundle, self.restore_repo)
        self.assertGreater(summary["create"], 0)
        self.assertEqual(summary["registry"], "create")
        restored_registry = json.loads(
            (self.restore_repo / "projects.local.json").read_text(encoding="utf-8")
        )
        self.assertEqual(restored_registry["projects"][0]["path"], "sample_problem")
        self.assertEqual(
            (self.restore_repo / "sample_problem" / "notes" / "proof.tex").read_text(encoding="utf-8"),
            "formal source",
        )
        self.assertEqual(
            (self.restore_repo / "inbox" / "related.md").read_text(encoding="utf-8"),
            "original report",
        )
        self.assertFalse((self.restore_repo / "inbox" / "unrelated.md").exists())

        second = restore_bundle(self.bundle, self.restore_repo)
        self.assertEqual(second["create"], 0)
        self.assertEqual(second["unchanged"], len(paths))
        self.assertEqual(second["registry"], "unchanged")

    def test_conflict_preflight_writes_nothing(self):
        self._export()
        conflict = self.restore_repo / "sample_problem" / "goal.md"
        conflict.parent.mkdir()
        conflict.write_text("different", encoding="utf-8")
        with self.assertRaisesRegex(BundleError, "no files were written"):
            restore_bundle(self.bundle, self.restore_repo)
        self.assertEqual(conflict.read_text(encoding="utf-8"), "different")
        self.assertFalse((self.restore_repo / "sample_problem" / "research_state.md").exists())

    def test_keep_and_overwrite_conflict_modes(self):
        self._export()
        conflict = self.restore_repo / "sample_problem" / "goal.md"
        conflict.parent.mkdir()
        conflict.write_text("different", encoding="utf-8")
        kept = restore_bundle(self.bundle, self.restore_repo, keep_existing=True)
        self.assertEqual(kept["kept"], 1)
        self.assertEqual(conflict.read_text(encoding="utf-8"), "different")
        overwritten = restore_bundle(self.bundle, self.restore_repo, overwrite=True)
        self.assertEqual(overwritten["overwrite"], 1)
        self.assertEqual(
            conflict.read_text(encoding="utf-8"),
            "# Goal\n\nSee [the source report](../inbox/related.md).\n",
        )

    def test_tampered_payload_is_rejected(self):
        self._export()
        tampered = self.root / "tampered.zip"
        with zipfile.ZipFile(self.bundle, "r") as source, zipfile.ZipFile(tampered, "w") as target:
            for name in source.namelist():
                data = source.read(name)
                if name.endswith("research_state.md"):
                    data += b"tampered"
                target.writestr(name, data)
        with self.assertRaisesRegex(BundleError, "size does not match|SHA-256"):
            verify_bundle(tampered)

    def test_manifest_and_payload_members_are_auditable(self):
        self._export()
        with zipfile.ZipFile(self.bundle, "r") as archive:
            self.assertIn(MANIFEST_NAME, archive.namelist())
            manifest = json.loads(archive.read(MANIFEST_NAME))
        self.assertEqual(manifest["bundle_type"], "math-research-problem")
        self.assertEqual(manifest["selected_inbox"], ["inbox/related.md"])
        self.assertEqual(manifest["referenced_inbox"], ["inbox/related.md"])
        self.assertEqual(manifest["explicit_inbox"], [])
        self.assertTrue(all(entry["sha256"] for entry in manifest["files"]))

    def test_explicit_inbox_supplements_markdown_references(self):
        manifest = self._export(["inbox/extra.md"])
        paths = {entry["path"] for entry in manifest["files"]}
        self.assertIn("inbox/related.md", paths)
        self.assertIn("inbox/extra.md", paths)
        self.assertNotIn("inbox/unrelated.md", paths)
        self.assertEqual(manifest["referenced_inbox"], ["inbox/related.md"])
        self.assertEqual(manifest["explicit_inbox"], ["inbox/extra.md"])

    def test_missing_markdown_inbox_reference_is_rejected(self):
        (self.source_repo / "sample_problem" / "goal.md").write_text(
            "[missing](../inbox/missing.md)\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(BundleError, "references missing inbox path"):
            self._export()

    def test_manifest_cannot_target_public_or_git_paths(self):
        for relative in (
            "projects.json",
            "inbox/README.md",
            "sample_problem/notes/.git/config",
            "sample_problem/email/.git/config",
            "another_problem/email/index.md",
        ):
            with self.subTest(relative=relative):
                malicious = self.root / f"malicious-{hashlib.sha256(relative.encode()).hexdigest()[:8]}.zip"
                data = b"overwrite"
                archive_path = f"payload/{relative}"
                manifest = {
                    "schema_version": 1,
                    "bundle_type": "math-research-problem",
                    "project": {
                        "path": "sample_problem",
                        "title": "Sample Problem",
                        "role": "active",
                        "description": "Fixture",
                    },
                    "files": [
                        {
                            "path": relative,
                            "archive_path": archive_path,
                            "category": "malicious",
                            "size": len(data),
                            "sha256": hashlib.sha256(data).hexdigest(),
                        }
                    ],
                }
                with zipfile.ZipFile(malicious, "w") as archive:
                    archive.writestr(archive_path, data)
                    archive.writestr(MANIFEST_NAME, json.dumps(manifest))
                with self.assertRaisesRegex(BundleError, "allowed private problem scope"):
                    verify_bundle(malicious)

    def test_restore_rejects_conflicting_local_registry_before_writes(self):
        self._export()
        (self.restore_repo / "projects.local.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "projects": [
                        {
                            "path": "sample_problem",
                            "title": "Different project",
                            "role": "active",
                            "description": "Conflict",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(BundleError, "no files were written"):
            restore_bundle(self.bundle, self.restore_repo)
        self.assertFalse(
            (self.restore_repo / "sample_problem" / "research_state.md").exists()
        )

    def test_restore_rejects_symlinked_parent_before_writes(self):
        self._export()
        project = self.restore_repo / "sample_problem"
        project.mkdir()
        public_target = self.restore_repo / "scripts"
        public_target.mkdir()
        (project / "notes").symlink_to(public_target, target_is_directory=True)

        with self.assertRaisesRegex(BundleError, "symbolic-link parent"):
            restore_bundle(self.bundle, self.restore_repo)
        self.assertFalse((public_target / "proof.tex").exists())
        self.assertFalse((project / "research_state.md").exists())


if __name__ == "__main__":
    unittest.main()
