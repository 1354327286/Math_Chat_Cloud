"""Privacy behavior and the human-facing correspondence contract."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.check_public_scope import EXPECTED_PUBLIC_REGISTRY, violation_reason


ROOT = Path(__file__).resolve().parents[1]


class EmailPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.repo = Path(self.tempdir.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        shutil.copyfile(ROOT / ".gitignore", self.repo / ".gitignore")
        (self.repo / "projects.json").write_text(
            json.dumps(EXPECTED_PUBLIC_REGISTRY), encoding="utf-8"
        )

    def _write(self, relative):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Private correspondence fixture\n", encoding="utf-8")

    def _git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.repo, check=True, capture_output=True, text=True
        ).stdout

    def test_email_files_are_ignored_in_real_and_example_projects(self):
        paths = [
            f"{project}/email/{filename}"
            for project in ("sample_problem", "example_math_problem")
            for filename in (
                "README.md",
                "contacts.md",
                "index.md",
                "2026-10-04_correspondent_topic.md",
                "attachments/thread/original.eml",
                "attachments/thread/claims.tex",
                "attachments/thread/screenshot.png",
            )
        ]
        for relative in paths:
            self._write(relative)
            with self.subTest(path=relative):
                self.assertEqual(self._git("check-ignore", relative).strip(), relative)
                self.assertIsNotNone(violation_reason(relative))

        self._git("add", "--all")
        staged = self._git("diff", "--cached", "--name-only").splitlines()
        self.assertEqual(set(staged), {".gitignore", "projects.json"})

    def test_forced_email_staging_is_rejected_by_real_scope_cli(self):
        paths = [
            "example_math_problem/email/contacts.md",
            "example_math_problem/email/attachments/thread/original.eml",
            "example_math_problem/email/attachments/thread/README.md",
        ]
        for relative in paths:
            self._write(relative)
        self._git("add", "--force", *paths)
        for mode in ([], ["--tracked"]):
            with self.subTest(mode=mode):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts" / "check_public_scope.py"),
                        "--repo",
                        str(self.repo),
                        *mode,
                    ],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 1, result.stderr)
                for relative in paths:
                    self.assertIn(relative, result.stdout)
                self.assertIn("content under project email/ must remain local", result.stdout)

    def test_generic_email_workflow_remains_publishable(self):
        relative = "docs/email_workflow.md"
        self._write(relative)
        result = subprocess.run(
            ["git", "check-ignore", relative], cwd=self.repo, capture_output=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertIsNone(violation_reason(relative))
        self._git("add", relative)
        self.assertIn(relative, self._git("diff", "--cached", "--name-only"))


class EmailWorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (ROOT / "docs" / "email_workflow.md").read_text(encoding="utf-8")
        cls.compact = " ".join(cls.workflow.split())

    def test_provenance_and_agreement_states_remain_explicit(self):
        for phrase in (
            "Before the contribution",
            "During the exchange",
            "After the contribution",
            "AI-assisted analysis",
            "artifact/version, triggering condition",
            "a **draft** has not been sent",
            "**proposal** or **unilateral commitment** is not **mutual agreement**",
            "the correspondent's agreement must not be inferred from silence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.compact)

    def test_finalization_check_is_version_scoped_not_compile_scoped(self):
        for phrase in (
            "Before finalizing or releasing a manuscript revision",
            "`email/index.md`",
            "not by every local LaTeX compile",
            "Recheck each condition against the actual manuscript and authorship state",
            "If the index is missing or incomplete",
            "do not send any message without the user's explicit approval",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.compact)

    def test_imported_guidance_preserves_checked_date_and_limits(self):
        for phrase in (
            "Checked 2026-09-26",
            "sources support principles, not a ruling",
            "direct retrieval of this PDF and the current policy landing page failed",
            "not mathematical authorship rules",
            "not a universal permission gate",
            "Mere grammar edits do not require a new search",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.compact)
        for source in (
            "https://www.ams.org/about-us/governance/council-meetings/council-minutes0115.pdf",
            "https://ukrio.org/wp-content/uploads/Good-Authorship-Practice.pdf",
            "https://members.publicationethics.org/sites/default/files/2003pdf12_0.pdf",
        ):
            self.assertIn(source, self.workflow)


if __name__ == "__main__":
    unittest.main()
