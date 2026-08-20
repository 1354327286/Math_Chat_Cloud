import unittest
from pathlib import Path


class CloudPortabilityTests(unittest.TestCase):
    def test_primary_instructions_have_no_windows_runtime_examples(self):
        root = Path(__file__).resolve().parents[1]
        files = [
            root / "AGENTS.md",
            root / "README.md",
            root / "docs" / "cloud_workflow.md",
            root / "docs" / "problem_bundle.md",
            root / "docs" / "reference_workflow.md",
            root / "docs" / "research_state_workflow.md",
            root / "lean" / "AGENTS.md",
            root / "lean" / "README.md",
            root / "skills" / "formalization-handoff" / "SKILL.md",
            root / "skills" / "lean-formalization" / "SKILL.md",
            root / "skills" / "long-autonomous-math-research" / "SKILL.md",
            root / "skills" / "pro-research-handoff" / "SKILL.md",
            root / "skills" / "review-latex-math-manuscript" / "SKILL.md",
        ]
        forbidden = [
            "```" + "powershell",
            ".venv/" + "Scripts",
            "D:" + "\\",
            "python ." + "\\scripts",
        ]
        for path in files:
            content = path.read_text(encoding="utf-8")
            for marker in forbidden:
                self.assertNotIn(marker, content, f"{path} still contains {marker!r}")

    def test_cloud_entrypoints_exist(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "scripts" / "bootstrap_cloud.sh").is_file())
        self.assertTrue((root / "scripts" / "cloud_research_report.py").is_file())
        self.assertTrue((root / "scripts" / "bootstrap_lean.sh").is_file())
        self.assertTrue((root / "scripts" / "run_lean.sh").is_file())
        self.assertTrue((root / "scripts" / "build_tex.py").is_file())
        self.assertTrue((root / "docs" / "cloud_workflow.md").is_file())
        self.assertTrue((root / "docs" / "research_state_workflow.md").is_file())

    def test_startup_reads_only_compact_state_and_one_dated_note(self):
        root = Path(__file__).resolve().parents[1]
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        startup = agents.split("## Session Startup", 1)[1].split("## Mathematical Standards", 1)[0]
        self.assertIn("research_state.md", startup)
        self.assertIn("today's", startup)
        self.assertIn("otherwise the most", startup)
        self.assertIn("Do not preload `goal.md`", startup)
        self.assertIn("whole `memory/` tree", startup)


if __name__ == "__main__":
    unittest.main()
