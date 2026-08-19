import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LeanScaffoldTests(unittest.TestCase):
    def test_same_repository_scaffold_is_complete(self):
        required = [
            "lean/AGENTS.md",
            "lean/README.md",
            "lean/FORMALIZATION_INDEX.md",
            "lean/lakefile.toml",
            "lean/MathDailyLean.lean",
            "lean/MathDailyLean/Common/Basic.lean",
            "scripts/bootstrap_lean.sh",
            "scripts/lean_proc_self_exe_shim.c",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)
        self.assertFalse((ROOT / "lean" / ".git").exists())

    def test_instruction_budget_keeps_room_for_nested_rules(self):
        total = sum(
            path.stat().st_size
            for path in [ROOT / "AGENTS.md", ROOT / "lean" / "AGENTS.md"]
        )
        self.assertLessEqual(total, 24 * 1024)

    def test_check_mode_needs_no_toolchain_or_network(self):
        result = subprocess.run(
            ["bash", "scripts/bootstrap_lean.sh", "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Lean scaffold is complete", result.stdout)

    def test_install_is_an_explicit_mode(self):
        script = (ROOT / "scripts" / "bootstrap_lean.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("--install)", script)
        self.assertIn('mode="${1:---check}"', script)


if __name__ == "__main__":
    unittest.main()
