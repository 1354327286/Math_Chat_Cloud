import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class MathArtifactStandardTests(unittest.TestCase):
    def test_root_routes_exported_artifacts_to_the_standard(self):
        agents = read("AGENTS.md")
        compact = " ".join(agents.split())
        self.assertIn("docs/mathematical_artifact_standard.md", agents)
        self.assertIn("statement labels as navigation aids", compact)
        self.assertIn("state the exact consequence being used", compact)

    def test_standard_requires_closure_before_drafting(self):
        standard = read("docs/mathematical_artifact_standard.md")
        compact = " ".join(standard.split())
        self.assertIn("## Eligibility gate before drafting", standard)
        self.assertIn("only after the requested mathematical result is closed", compact)
        self.assertIn("### Terminology and reader-confusion audit", standard)
        self.assertIn("## Cold-read audit before delivery", standard)
        self.assertIn("templates/math_article.tex", standard)
        self.assertIn("Do not invent a noun phrase", compact)
        self.assertIn("two plausible mathematical readings", standard)
        self.assertIn("Do not maintain a generated Markdown copy", standard)

    def test_skills_use_one_article_template_and_no_reader_copy(self):
        proof = read("skills/write-self-contained-math-proof/SKILL.md")
        review = read("skills/review-latex-math-manuscript/SKILL.md")
        self.assertIn("templates/math_article.tex", proof)
        self.assertIn("templates/math_article.tex", review)
        self.assertIn("terminology and reader-confusion audit", proof)
        self.assertIn("## Audit Human Readability", review)
        self.assertIn("python scripts/build_tex.py", proof)
        self.assertIn("python scripts/build_tex.py", review)
        self.assertNotIn("reader.md", proof)
        self.assertNotIn("reader.md", review)

    def test_single_template_has_draft_switch_without_workflow_ids(self):
        template = read("templates/math_article.tex")
        self.assertIn("math-article-template: 1", template)
        self.assertIn("\\newif\\ifdraftpaper", template)
        self.assertIn("\\draftpapertrue", template)
        self.assertIn("\\linenumbers", template)
        self.assertIn("\\section{Introduction}", template)
        self.assertIn("\\begin{theorem}[Main theorem]", template)
        self.assertNotIn("THM-main", template)
        self.assertNotIn("ISSUE-", template)
        self.assertNotIn("Dependency and citation audit", template)
        self.assertNotIn("Verification status", template)
        self.assertNotIn("Revision log", template)


if __name__ == "__main__":
    unittest.main()
