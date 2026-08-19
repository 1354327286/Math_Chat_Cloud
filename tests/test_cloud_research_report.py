import json
import tempfile
import unittest
from pathlib import Path

from scripts.cloud_research_report import render_report


class CloudResearchReportTests(unittest.TestCase):
    def test_report_handles_loaded_and_skeleton_projects(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            loaded = root / "loaded_project"
            skeleton = root / "skeleton_project"
            loaded.mkdir()
            skeleton.mkdir()
            (root / "inbox").mkdir()
            (root / "projects.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "projects": [
                            {
                                "path": "loaded_project",
                                "title": "Loaded",
                                "role": "active",
                                "description": "Loaded state",
                            },
                            {
                                "path": "skeleton_project",
                                "title": "Skeleton",
                                "role": "exploring",
                                "description": "No state yet",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (loaded / "research_state.md").write_text(
                """# Loaded

## Research State
- Status: active
- Confidence: medium
- Last updated: 2026-08-19

## Known Theorems

## Open Problems
- [ ] Check the cloud report.

## Failed Attempts

## Current Goal
- **Target:** Produce a static overview.
- **Next action:** Review it.
- **Blocker:** none

## References
""",
                encoding="utf-8",
            )

            report = render_report(root)

            self.assertIn("数学研究项目云端概览", report)
            self.assertIn("Loaded", report)
            self.assertIn("Produce a static overview", report)
            self.assertIn("`skeleton_project`", report)
            self.assertIn("开放义务 1 项", report)


if __name__ == "__main__":
    unittest.main()
