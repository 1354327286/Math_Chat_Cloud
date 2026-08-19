import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.formalization_handoff import (
    HandoffError,
    export_task,
    import_result,
    prepare_result,
    stage_task,
    verify_task,
)


class FormalizationHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.project = self.root / "sample_problem"
        self.project.mkdir()
        (self.root / "projects.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "projects": [
                        {
                            "path": "sample_problem",
                            "title": "Sample Problem",
                            "role": "active",
                            "description": "Test problem",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        assets_source = (
            Path(__file__).resolve().parents[1]
            / "skills"
            / "formalization-handoff"
            / "assets"
        )
        assets_target = (
            self.root / "skills" / "formalization-handoff" / "assets"
        )
        assets_target.parent.mkdir(parents=True)
        shutil.copytree(assets_source, assets_target)

        source_text = {
            "research_state.md": "# Research State\nClosed proof candidate.\n",
            "goal.md": "# Goal\nProve the theorem.\n",
            "progress.md": "# Progress\nProof audited.\n",
            "subgoal.md": "# Subgoal\nNo open obligations.\n",
            "2026-08-18.md": "# Daily note\nExport discussed.\n",
            "theorem.md": "For every n, P n.",
            "proof.md": "Fix n and apply Lemma L.",
            "ledger.md": "L1. Exact hypotheses and conclusion; source: proof.md.",
            "audit.md": "Internal audit: no known mathematical gap.",
            "output.md": "Produce theorem sample_theorem with the exact statement.",
            "reference.md": "Reference theorem L with exact hypotheses.",
        }
        for name, content in source_text.items():
            (self.project / name).write_text(content, encoding="utf-8")

        self.lean_root = self.root / "lean_repo"
        self.lean_root.mkdir()
        for marker in (".git", ".archon"):
            (self.lean_root / marker).mkdir()
        (self.lean_root / "AGENTS.md").write_text("# Lean rules\n", encoding="utf-8")
        (self.lean_root / "lean-toolchain").write_text("leanprover/lean4:v4.30.0\n")
        (self.lean_root / "lakefile.toml").write_text("name = 'test'\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def export(self):
        return export_task(
            self.root,
            "sample_problem",
            theorem_file="theorem.md",
            proof_files=["proof.md"],
            ledger_file="ledger.md",
            audit_file="audit.md",
            output_file="output.md",
            references=["reference.md"],
            external_results_policy="sorry-free",
            user_authorized=True,
            audit_no_known_gaps=True,
            slug="sample-theorem",
            now=datetime(2026, 8, 18, 12, 0, tzinfo=timezone.utc),
        )

    def test_export_requires_both_human_gate_receipts(self):
        common = dict(
            theorem_file="theorem.md",
            proof_files=["proof.md"],
            ledger_file="ledger.md",
            audit_file="audit.md",
            output_file="output.md",
            external_results_policy="sorry-free",
        )
        with self.assertRaisesRegex(HandoffError, "user authorization"):
            export_task(
                self.root,
                "sample_problem",
                user_authorized=False,
                audit_no_known_gaps=True,
                **common,
            )
        with self.assertRaisesRegex(HandoffError, "internal audit"):
            export_task(
                self.root,
                "sample_problem",
                user_authorized=True,
                audit_no_known_gaps=False,
                **common,
            )

    def test_export_creates_human_packet_and_validation_manifest(self):
        task_id, packet = self.export()

        self.assertEqual(task_id, "20260818-120000-sample-theorem")
        self.assertIn("For every n, P n.", (packet / "request.md").read_text())
        self.assertIn("Closed proof candidate", (packet / "context.md").read_text())
        self.assertIn("proof.md", (packet / "source_map.md").read_text())
        manifest = json.loads((packet / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "exported")
        self.assertEqual(manifest["external_results_policy"], "sorry-free")
        self.assertNotIn("claims", manifest)
        verified, _ = verify_task(self.root, "sample_problem", task_id)
        self.assertEqual(verified, packet)

    def test_source_drift_stops_stage_before_destination_write(self):
        task_id, _ = self.export()
        (self.project / "proof.md").write_text("Changed proof.\n", encoding="utf-8")

        with self.assertRaisesRegex(HandoffError, "source drift"):
            stage_task(self.root, "sample_problem", task_id, self.lean_root)
        self.assertFalse(
            (self.lean_root / ".archon" / "formalization_inbox" / task_id).exists()
        )

    def test_stage_is_hash_checked_and_refuses_overwrite(self):
        task_id, packet = self.export()
        staged = stage_task(self.root, "sample_problem", task_id, self.lean_root)

        self.assertEqual(
            (staged / "manifest.json").read_bytes(),
            (packet / "manifest.json").read_bytes(),
        )
        with self.assertRaisesRegex(HandoffError, "refusing overwrite"):
            stage_task(self.root, "sample_problem", task_id, self.lean_root)

    def test_tampered_packet_is_rejected(self):
        task_id, packet = self.export()
        (packet / "context.md").write_text("tampered\n", encoding="utf-8")

        with self.assertRaisesRegex(HandoffError, "changed after export"):
            verify_task(self.root, "sample_problem", task_id)

    def test_tampered_manifest_is_rejected_by_receipt(self):
        task_id, packet = self.export()
        manifest_path = packet / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["status"] = "edited"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaisesRegex(HandoffError, "hash receipt"):
            verify_task(self.root, "sample_problem", task_id)

    def test_prepare_and_import_preserve_raw_evidence_without_state_update(self):
        task_id, _ = self.export()
        stage_task(self.root, "sample_problem", task_id, self.lean_root)
        result_dir = self.lean_root / ".archon" / "task_results"
        result_dir.mkdir()
        (result_dir / "report.md").write_text(
            "# Result\nBuild passed; correspondence remains for audit.\n",
            encoding="utf-8",
        )
        lean_file = self.lean_root / "MyProject" / "Sample.lean"
        lean_file.parent.mkdir()
        lean_file.write_text("theorem sample : True := by trivial\n", encoding="utf-8")
        state_before = (self.project / "research_state.md").read_bytes()

        outbox = prepare_result(
            self.lean_root,
            task_id,
            kind="verification_result",
            report_file=".archon/task_results/report.md",
            lean_files=["MyProject/Sample.lean"],
            now=datetime(2026, 8, 18, 13, 0, tzinfo=timezone.utc),
        )
        imported = import_result(
            self.root,
            "sample_problem",
            task_id,
            self.lean_root,
            now=datetime(2026, 8, 18, 14, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(
            (imported / "raw" / "result_manifest.json").read_bytes(),
            (outbox / "result_manifest.json").read_bytes(),
        )
        self.assertIn("needs semantic audit", (imported / "review.md").read_text())
        self.assertEqual((self.project / "research_state.md").read_bytes(), state_before)

    def test_source_query_does_not_require_lean_evidence(self):
        task_id, _ = self.export()
        stage_task(self.root, "sample_problem", task_id, self.lean_root)
        result_dir = self.lean_root / ".archon" / "task_results"
        result_dir.mkdir()
        report = result_dir / "report.md"
        query = result_dir / "query.md"
        report.write_text("# Blocked\nSemantic ambiguity.\n", encoding="utf-8")
        query.write_text("# Query\nWhich hypothesis is intended?\n", encoding="utf-8")

        outbox = prepare_result(
            self.lean_root,
            task_id,
            kind="source_query",
            report_file=report,
            source_query_file=query,
        )

        self.assertTrue((outbox / "source_query.md").is_file())
        self.assertFalse((outbox / "lean").exists())

    def test_source_drift_can_return_query_but_not_verification(self):
        task_id, _ = self.export()
        stage_task(self.root, "sample_problem", task_id, self.lean_root)
        result_dir = self.lean_root / ".archon" / "task_results"
        result_dir.mkdir()
        report = result_dir / "report.md"
        query = result_dir / "query.md"
        report.write_text("# Blocked\nSource drift detected.\n", encoding="utf-8")
        query.write_text("# Query\nPlease re-export the changed proof.\n", encoding="utf-8")
        lean_file = self.lean_root / "MyProject" / "Sample.lean"
        lean_file.parent.mkdir()
        lean_file.write_text("theorem sample : True := by trivial\n", encoding="utf-8")
        (self.project / "proof.md").write_text("Changed after staging.\n", encoding="utf-8")

        with self.assertRaisesRegex(HandoffError, "source drift"):
            prepare_result(
                self.lean_root,
                task_id,
                kind="verification_result",
                report_file=report,
                lean_files=[lean_file],
            )

        prepare_result(
            self.lean_root,
            task_id,
            kind="source_query",
            report_file=report,
            source_query_file=query,
        )
        imported = import_result(
            self.root, "sample_problem", task_id, self.lean_root
        )
        self.assertIn("source drift detected", (imported / "review.md").read_text())

    def test_rejects_source_outside_selected_problem(self):
        outside = self.root / "outside.md"
        outside.write_text("not authorized\n", encoding="utf-8")
        with self.assertRaisesRegex(HandoffError, "escapes allowed root"):
            export_task(
                self.root,
                "sample_problem",
                theorem_file=outside,
                proof_files=["proof.md"],
                ledger_file="ledger.md",
                audit_file="audit.md",
                output_file="output.md",
                external_results_policy="sorry-free",
                user_authorized=True,
                audit_no_known_gaps=True,
            )


if __name__ == "__main__":
    unittest.main()
