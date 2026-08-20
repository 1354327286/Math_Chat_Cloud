import tempfile
import unittest
from pathlib import Path

from scripts.build_tex import FATAL_WARNING_RE, log_warnings


ROOT = Path(__file__).resolve().parents[1]


class BuildTexTests(unittest.TestCase):
    def test_builder_and_single_template_exist(self):
        self.assertTrue((ROOT / "scripts" / "build_tex.py").is_file())
        self.assertTrue((ROOT / "templates" / "math_article.tex").is_file())
        self.assertFalse((ROOT / "templates" / "self_contained_math_article.tex").exists())
        self.assertFalse((ROOT / "templates" / "formal_math_article.tex").exists())

    def test_final_log_warning_parser(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log = Path(temp_dir) / "paper.log"
            log.write_text(
                "LaTeX Warning: Reference `x' undefined.\n"
                "Overfull \\hbox (2.0pt too wide)\n"
                "LaTeX Warning: Reference `x' undefined.\n",
                encoding="utf-8",
            )
            warnings = log_warnings(log)
            self.assertEqual(len(warnings), 2)
            self.assertTrue(any(FATAL_WARNING_RE.search(item) for item in warnings))


if __name__ == "__main__":
    unittest.main()
