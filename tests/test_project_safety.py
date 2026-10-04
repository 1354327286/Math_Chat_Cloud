import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_public_scope import (
    find_violations,
    public_registry_violations,
    violation_reason,
)
from scripts.create_math_project import create_project, register_project


class PublicScopeTests(unittest.TestCase):
    def test_blocks_private_research_paths(self):
        blocked = {
            "problem/research_state.md",
            "problem/2026-08-01.md",
            "problem/memory/proof.md",
            "problem/refs/paper.pdf",
            "problem/downloads/source.tar",
            "inbox/imported_report.md",
            "problem/handoff/requests/task.md",
            "problem/handoff/responses/answer.md",
            "problem/handoff/manifest.json",
            "problem/README.md",
            "projects.local.json",
            "private_notes.txt",
        }
        for path in blocked:
            with self.subTest(path=path):
                self.assertIsNotNone(violation_reason(path))

    def test_allows_framework_paths(self):
        allowed = {
            "AGENTS.md",
            "README.md",
            "templates/research_state.md",
            "example_math_problem/README.md",
            "example_math_problem/memory/.gitkeep",
            "scripts/check_public_scope.py",
            "example_math_problem/handoff/.gitkeep",
            "lean/AGENTS.md",
            "lean/MathDailyLean/Common/Basic.lean",
        }
        self.assertEqual(find_violations(allowed), [])

    def test_public_registry_allows_only_the_example(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "projects.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "projects": [
                            {
                                "path": "private_problem",
                                "title": "Private",
                                "role": "active",
                                "description": "Should not be public",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            self.assertTrue(public_registry_violations(str(root)))

    def test_public_registry_rejects_private_text_hidden_in_example_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "projects.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "projects": [
                            {
                                "path": "example_math_problem",
                                "title": "Private theorem name",
                                "role": "example",
                                "description": "Private project description",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            self.assertTrue(public_registry_violations(str(root)))


class CreateProjectTests(unittest.TestCase):
    def test_creates_standard_layout(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template_dir = root / "templates"
            template_dir.mkdir()
            (template_dir / "research_state.md").write_text(
                "# Problem: <short descriptive title>\n\n## Research State\n",
                encoding="utf-8",
            )
            (template_dir / "subgoal_plan.md").write_text(
                "# Subgoals: <short descriptive title>\n\n## Exact Active Target\n",
                encoding="utf-8",
            )

            project = create_project(root, "sample_problem", "Sample Problem")

            self.assertTrue((project / "research_state.md").is_file())
            self.assertTrue((project / "goal.md").is_file())
            self.assertTrue((project / "memory" / "failed_paths.md").is_file())
            self.assertTrue((project / "refs" / ".gitkeep").is_file())
            self.assertTrue((project / "handoff" / ".gitkeep").is_file())
            for filename in ("README.md", "contacts.md", "index.md"):
                self.assertTrue((project / "email" / filename).is_file())
            self.assertTrue((project / "email" / "attachments").is_dir())
            self.assertIn(
                "# Subgoals: Sample Problem",
                (project / "subgoal.md").read_text(encoding="utf-8"),
            )
            email_index = (project / "email" / "index.md").read_text(encoding="utf-8")
            self.assertIn("No correspondence recorded yet", email_index)
            self.assertIn("Artifact/version", email_index)
            self.assertIn("Message status and evidence", email_index)
            self.assertIn("Obligation/condition", email_index)
            self.assertIn("exact trigger", email_index)
            self.assertFalse((root / "projects.json").exists())
            self.assertFalse((root / "projects.local.json").exists())
            self.assertIn(
                "Sample Problem",
                (project / "research_state.md").read_text(encoding="utf-8"),
            )

    def test_rejects_unsafe_or_existing_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template_dir = root / "templates"
            template_dir.mkdir()
            (template_dir / "research_state.md").write_text("template", encoding="utf-8")
            (template_dir / "subgoal_plan.md").write_text("subgoals", encoding="utf-8")

            with self.assertRaises(ValueError):
                create_project(root, "../escape", "Escape")

            (root / "existing").mkdir()
            with self.assertRaises(FileExistsError):
                create_project(root, "existing", "Existing")

    def test_missing_or_invalid_subgoal_template_leaves_no_partial_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template_dir = root / "templates"
            template_dir.mkdir()
            (template_dir / "research_state.md").write_text("state", encoding="utf-8")
            with self.assertRaisesRegex(FileNotFoundError, "subgoal_plan.md"):
                create_project(root, "missing_template", "Missing")
            self.assertFalse((root / "missing_template").exists())
            (template_dir / "subgoal_plan.md").write_bytes(b"\xff")
            with self.assertRaises(UnicodeDecodeError):
                create_project(root, "invalid_template", "Invalid")
            self.assertFalse((root / "invalid_template").exists())

    def test_registers_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "projects.json").write_text(
                '{"schema_version": 1, "projects": []}\n', encoding="utf-8"
            )
            public_registry_bytes = (root / "projects.json").read_bytes()

            register_project(root, "sample_problem", "Sample", "active", "Description")

            registry = json.loads(
                (root / "projects.local.json").read_text(encoding="utf-8")
            )
            self.assertEqual(registry["projects"][0]["path"], "sample_problem")
            self.assertEqual((root / "projects.json").read_bytes(), public_registry_bytes)
            with self.assertRaises(ValueError):
                register_project(root, "sample_problem", "Sample", "active", "Description")


if __name__ == "__main__":
    unittest.main()
