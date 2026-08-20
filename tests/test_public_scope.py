import subprocess
import unittest
from pathlib import Path

from scripts.check_public_scope import violation_reason


class PublicScopeTests(unittest.TestCase):
    def test_private_lean_source_is_blocked_even_if_force_added(self):
        reason = violation_reason(
            "lean/MathDailyLean/Projects/private_problem/Main.lean"
        )
        self.assertIsNotNone(reason)
        self.assertIn("problem-specific Lean source", reason)

    def test_public_projects_readme_remains_allowed(self):
        self.assertIsNone(
            violation_reason("lean/MathDailyLean/Projects/README.md")
        )

    def test_gitignore_covers_private_lean_projects(self):
        root = Path(__file__).resolve().parents[1]
        private = subprocess.run(
            [
                "git",
                "check-ignore",
                "--no-index",
                "--quiet",
                "lean/MathDailyLean/Projects/private_problem/Main.lean",
            ],
            cwd=root,
            check=False,
        )
        readme = subprocess.run(
            [
                "git",
                "check-ignore",
                "--no-index",
                "--quiet",
                "lean/MathDailyLean/Projects/README.md",
            ],
            cwd=root,
            check=False,
        )
        self.assertEqual(private.returncode, 0)
        self.assertEqual(readme.returncode, 1)


if __name__ == "__main__":
    unittest.main()
