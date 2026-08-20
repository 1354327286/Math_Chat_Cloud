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
        lean_project = (
            self.source_repo
            / "lean"
            / "MathDailyLean"
            / "Projects"
            / "sample_problem"
        )
        lean_project.mkdir(parents=True)
        (lean_project / "Main.lean").write_text(
            "theorem bundled_example : True := by trivial\n",
            encoding="utf-8",
        )
        (lean_project / "Main.olean").write_bytes(b"generated")
        (lean_project / "private_notes.md").write_text(
            "private Lean notes belong in the problem memory instead",
            encoding="utf-8",
        )
        (lean_project / ".lake").mkdir()
        (lean_project / ".lake" / "Generated.lean").write_text(
            "theorem generated_cache : True := by trivial\n",
            encoding="utf-8",
        )
        other_lean_project = (
            self.source_repo
            / "lean"
            / "MathDailyLean"
            / "Projects"
            / "other_problem"
        )
        other_lean_project.mkdir(parents=True)
        (other_lean_project / "Other.lean").write_text(
            "theorem unrelated : True := by trivial\n",
            encoding="utf-8",
        )
        self.bundle = self.root / "sample.zip"

    def tearDown(self):
        self.tempdir.cleanup()

    @staticmethod
    def _make_public_checkout(root: Path) -> None:
        root.mkdir(parents=True)
        (root / "inbox").mkdir()
        (root / "lean" / "MathDailyLean" / "Projects").mkdir(parents=True)
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

    def test_round_trip_preserves_private_files_and_referenced_inbox(self):
        manifest = self._export()
        paths = {entry["path"] for entry in manifest["files"]}
        self.assertIn("sample_problem/research_state.md", paths)
        self.assertIn("sample_problem/notes/proof.tex", paths)
        self.assertIn("sample_problem/refs/papers/paper.pdf", paths)
        self.assertIn("sample_problem/downloads/source.tar.gz", paths)
        self.assertIn("inbox/related.md", paths)
        self.assertIn("sample_problem/README.md", paths)
        self.assertIn(
            "lean/MathDailyLean/Projects/sample_problem/Main.lean",
            paths,
        )
        self.assertNotIn("sample_problem/notes/proof.reader.md", paths)
        self.assertNotIn("sample_problem/notes/proof.aux", paths)
        self.assertNotIn("sample_problem/refs/.lancedb/index.bin", paths)
        self.assertNotIn("inbox/unrelated.md", paths)
        self.assertNotIn("inbox/extra.md", paths)
        self.assertNotIn(
            "lean/MathDailyLean/Projects/sample_problem/Main.olean",
            paths,
        )
        self.assertNotIn(
            "lean/MathDailyLean/Projects/sample_problem/private_notes.md",
            paths,
        )
        self.assertNotIn(
            "lean/MathDailyLean/Projects/sample_problem/.lake/Generated.lean",
            paths,
        )
        self.assertNotIn(
            "lean/MathDailyLean/Projects/other_problem/Other.lean",
            paths,
        )

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
        self.assertEqual(
            (
                self.restore_repo
                / "lean"
                / "MathDailyLean"
                / "Projects"
                / "sample_problem"
                / "Main.lean"
            ).read_text(encoding="utf-8"),
            "theorem bundled_example : True := by trivial\n",
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
            "lean/MathDailyLean/Projects/other_problem/Main.lean",
            "lean/MathDailyLean/Projects/sample_problem/Main.olean",
            "lean/MathDailyLean/Projects/sample_problem/.lake/Evil.lean",
            "lean/lean-toolchain",
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
