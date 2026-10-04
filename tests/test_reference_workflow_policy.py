"""Contracts for source-cache reuse without weakening evidence or cloud boundaries."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return " ".join((ROOT / path).read_text(encoding="utf-8").split())


class ReferenceWorkflowPolicyTests(unittest.TestCase):
    def test_reuse_requires_readable_version_matched_sources_and_actual_math(self):
        workflow = read("docs/reference_workflow.md")
        self.assertIn("readable, version-matched canonical files", workflow)
        self.assertIn("Still read the actual mathematics", workflow)
        self.assertIn("hypotheses", workflow)
        self.assertIn("applicability for the current use", workflow)
        self.assertIn("download only missing or invalid parts", workflow)
        self.assertIn("does not waive the source requirement", workflow)

    def test_reacquisition_has_concrete_reasons_and_does_not_limit_search(self):
        workflow = read("docs/reference_workflow.md")
        for marker in ("missing or unreadable", "version or numbering conflict",
                       "suspected corruption", "new-source/latest-version",
                       "novelty", "still continue externally"):
            self.assertIn(marker, workflow)

    def test_reuse_does_not_bypass_other_integrity_checks(self):
        workflow = read("docs/reference_workflow.md")
        self.assertIn("does not waive transport-integrity hashing", workflow)
        self.assertIn("`--check-files` validation", workflow)
        self.assertIn("edited manuscript", workflow)
        skill = read("skills/search-math-results/SKILL.md")
        self.assertIn("reuse the catalog's canonical files", skill)
        self.assertIn("transport integrity hashing", skill)
        self.assertIn("still require external search", skill)

    def test_optional_semantic_services_remain_explicit_opt_in(self):
        workflow = read("docs/reference_workflow.md")
        self.assertIn("local-compatibility opt-in", workflow)
        self.assertIn("unless the user explicitly requests semantic search", workflow)
        skill = read("skills/search-math-results/SKILL.md")
        self.assertIn("unless the user explicitly requests it", skill)

    def test_workflow_documents_have_lf_and_resolvable_relative_links(self):
        paths = [ROOT / "AGENTS.md", ROOT / "README.md"]
        paths.extend((ROOT / "docs").glob("*.md"))
        for path in paths:
            raw = path.read_bytes()
            self.assertNotIn(b"\r\n", raw, str(path))
            text = raw.decode("utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                target = target.split("#", 1)[0]
                if not target or "<" in target or ">" in target:
                    continue
                self.assertTrue((path.parent / target).exists(), f"{path}: {target}")


if __name__ == "__main__":
    unittest.main()
