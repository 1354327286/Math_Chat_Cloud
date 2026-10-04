import contextlib
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts.check_research_state import (
    BYTE_BUDGET,
    STATE_SECTIONS,
    check_navigation_file,
    main,
)
from scripts.create_math_project import create_project


ROOT = Path(__file__).resolve().parents[1]
STATE = "# Sample\n\n" + "\n\n".join(f"## {heading}\n\nContent." for heading in STATE_SECTIONS) + "\n"


class NavigationCheckerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name)
        self.state = self.project / "research_state.md"
        self.state.write_text(STATE, encoding="utf-8")

    def write_sized_state(self, size):
        raw = STATE.encode("utf-8")
        self.state.write_bytes(raw + b"x" * (size - len(raw)))

    def test_valid_six_section_state(self):
        result = check_navigation_file(self.project)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])
        self.assertEqual(result.size_bytes, len(STATE.encode("utf-8")))
        self.assertEqual(result.line_count, len(STATE.splitlines()))
        self.assertFalse(result.conditional_proposal)

    def test_threshold_is_strict_and_requires_milestone(self):
        for size, milestone, expected in (
            (BYTE_BUDGET - 1, "Recorded scoped lemma closure", False),
            (BYTE_BUDGET, "Recorded scoped lemma closure", False),
            (BYTE_BUDGET + 1, None, False),
            (BYTE_BUDGET + 1, "  ", False),
            (BYTE_BUDGET + 1, "Recorded scoped lemma closure", True),
        ):
            with self.subTest(size=size, milestone=milestone):
                self.write_sized_state(size)
                result = check_navigation_file(self.project, milestone=milestone)
                self.assertEqual(result.size_bytes, size)
                self.assertEqual(result.conditional_proposal, expected)
                self.assertEqual(bool(result.warnings), size > BYTE_BUDGET)

    def test_utf8_bytes_not_characters_determine_threshold(self):
        text = STATE + "数学" * 4_100
        self.assertLess(len(text), BYTE_BUDGET)
        self.assertGreater(len(text.encode("utf-8")), BYTE_BUDGET)
        self.state.write_bytes(text.encode("utf-8"))
        result = check_navigation_file(self.project, milestone="Audited counterexample")
        self.assertEqual(result.size_bytes, len(text.encode("utf-8")))
        self.assertTrue(result.conditional_proposal)
        self.assertEqual(result.errors, [])

    def test_bom_and_crlf_are_measured_without_normalizing_bytes(self):
        raw = b"\xef\xbb\xbf" + STATE.replace("\n", "\r\n").encode("utf-8")
        self.state.write_bytes(raw)
        result = check_navigation_file(self.project)
        self.assertEqual(result.size_bytes, len(raw))
        self.assertEqual(result.line_count, len(STATE.splitlines()))
        self.assertEqual(result.errors, [])
        self.assertEqual(self.state.read_bytes(), raw)

    def test_lines_are_advisory_and_do_not_trigger_proposal(self):
        self.state.write_text(STATE + "x\n" * 251, encoding="utf-8")
        result = check_navigation_file(self.project, milestone="Manuscript revision completed")
        self.assertLess(result.size_bytes, BYTE_BUDGET)
        self.assertTrue(any("line budget" in warning for warning in result.warnings))
        self.assertFalse(result.conditional_proposal)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.project)]), 0)

    def test_no_rigid_subgoal_schema_and_selection_is_per_file(self):
        self.write_sized_state(BYTE_BUDGET + 1)
        subgoal = self.project / "subgoal.md"
        subgoal.write_text("# Existing custom heading\nOld stable labels remain valid.\n", encoding="utf-8")
        result = check_navigation_file(self.project, "subgoal.md", milestone="Closed a route")
        self.assertEqual(result.errors, [])
        self.assertFalse(result.conditional_proposal)
        self.state.write_text(STATE, encoding="utf-8")
        subgoal.write_text("# Existing custom heading\n" + "x" * BYTE_BUDGET, encoding="utf-8")
        self.assertTrue(check_navigation_file(self.project, "subgoal.md", milestone="Closed a route").conditional_proposal)
        self.assertFalse(check_navigation_file(self.project, milestone="Closed a route").conditional_proposal)

    def test_missing_selected_file_and_directory_are_errors(self):
        self.state.unlink()
        for directory in (self.project, self.project / "missing"):
            with self.subTest(directory=directory):
                result = check_navigation_file(directory)
                self.assertTrue(any("cannot read selected" in error for error in result.errors))
                self.assertFalse(result.conditional_proposal)
                self.assertIsNone(result.size_bytes)
        self.state.mkdir()
        self.assertTrue(check_navigation_file(self.project).errors)

    def test_empty_invalid_utf8_and_missing_state_sections(self):
        self.state.write_bytes(b"")
        result = check_navigation_file(self.project)
        self.assertIn("selected navigation file is empty", result.errors)
        self.assertEqual(sum("missing required" in error for error in result.errors), 6)
        self.state.write_bytes(b"\xff" * (BYTE_BUDGET + 1))
        result = check_navigation_file(self.project, milestone="Reported milestone")
        self.assertTrue(any("not valid UTF-8" in error for error in result.errors))
        self.assertFalse(result.conditional_proposal)
        self.assertEqual(result.size_bytes, BYTE_BUDGET + 1)

    def test_fenced_headings_do_not_count_and_duplicates_are_reported(self):
        self.state.write_text("```markdown\n" + STATE + "```\n", encoding="utf-8")
        self.assertEqual(len(check_navigation_file(self.project).errors), 6)
        self.state.write_text(STATE + "\n## Research State\n", encoding="utf-8")
        self.assertEqual(check_navigation_file(self.project).errors, ["duplicate state section: Research State"])

    def test_markdown_closing_heading_marks_and_both_fence_kinds(self):
        text = STATE.replace("## References", "## References ###")
        self.state.write_text(text + "\n~~~markdown\n## Research State\n~~~\n", encoding="utf-8")
        self.assertEqual(check_navigation_file(self.project).errors, [])

    def test_local_link_check_is_optional_and_checks_files_and_directories(self):
        self.state.write_text(STATE + "\n[missing](missing.md)\n", encoding="utf-8")
        self.assertEqual(check_navigation_file(self.project).errors, [])
        result = check_navigation_file(self.project, check_links=True)
        self.assertEqual(result.errors, ["missing local link target: missing.md"])
        (self.project / "missing.md").write_text("evidence", encoding="utf-8")
        (self.project / "refs").mkdir()
        self.state.write_text(STATE + "\n[evidence](missing.md#some-heading) [sources](refs/)\n", encoding="utf-8")
        self.assertEqual(check_navigation_file(self.project, check_links=True).errors, [])

    def test_common_inline_images_and_reference_targets(self):
        for filename in ("paper with space.md", "proof(1).md", "image.png", "versioné.md"):
            (self.project / filename).write_text("evidence", encoding="utf-8")
        links = r'''
[space](<paper with space.md> "title")
[encoded](paper%20with%20space.md)
[unicode](version%C3%A9.md)
[balanced](proof(1).md)
[escaped](proof\(1\).md)
![image](image.png)
[reference][source]
[source]: <paper with space.md> "title"
[missing][absent]
[absent]: nonexistent.md#claim
'''
        self.state.write_text(STATE + links, encoding="utf-8")
        result = check_navigation_file(self.project, check_links=True)
        self.assertEqual(result.errors, ["missing local link target: nonexistent.md#claim"])

    def test_external_links_anchors_and_code_are_not_checked(self):
        links = '''
[web](https://example.invalid/missing.md) [mail](mailto:someone@example.invalid)
[network](//example.invalid/missing.md) [fragment](#does-not-exist)
`[inline code](missing-one.md)`
```markdown
[code](missing-two.md)
```
~~~markdown
[code](missing-three.md)
~~~
    [indented code](missing-four.md)
'''
        self.state.write_text(STATE + links, encoding="utf-8")
        self.assertEqual(check_navigation_file(self.project, check_links=True).errors, [])

    def test_unsafe_local_links_and_schemes_are_diagnostics(self):
        links = '''
[absolute](/etc/passwd)
[encoded absolute](%2Fetc%2Fpasswd)
[escape](../../outside.md)
[encoded escape](%2e%2e/%2e%2e/outside.md)
[file](file:///etc/passwd)
[script](javascript:alert(1))
[drive](C:/Windows/file.md)
[control](bad%00file.md)
[backslash](..%5C..%5Coutside.md)
'''
        self.state.write_text(STATE + links, encoding="utf-8")
        result = check_navigation_file(self.project, check_links=True)
        self.assertEqual(len(result.errors), 9)
        self.assertTrue(all("unsafe" in error for error in result.errors))

    def test_sibling_inbox_links_allowed_but_symlink_escape_rejected(self):
        project = self.project / "problem"
        project.mkdir()
        inbox = self.project / "inbox"
        inbox.mkdir()
        (inbox / "message.md").write_text("evidence", encoding="utf-8")
        with tempfile.TemporaryDirectory() as outside:
            (project / "outside").symlink_to(outside, target_is_directory=True)
            (Path(outside) / "private.md").write_text("outside", encoding="utf-8")
            state = project / "research_state.md"
            state.write_text(STATE + "\n[inbox](../inbox/message.md)\n[outside](outside/private.md)\n", encoding="utf-8")
            result = check_navigation_file(project, check_links=True)
            self.assertEqual(result.errors, ["unsafe local link target resolves outside repository: outside/private.md"])

    def test_symlink_before_parent_traversal_keeps_filesystem_meaning(self):
        project = self.project / "problem"
        project.mkdir()
        (project / "private.md").write_text("misleading local target", encoding="utf-8")
        with tempfile.TemporaryDirectory() as outside:
            outside = Path(outside)
            (outside / "child").mkdir()
            (outside / "private.md").write_text("outside target", encoding="utf-8")
            (project / "link").symlink_to(outside / "child", target_is_directory=True)
            (project / "research_state.md").write_text(
                STATE + "\n[escape](link/../private.md)\n", encoding="utf-8"
            )
            result = check_navigation_file(project, check_links=True)
            self.assertEqual(result.errors, ["unsafe local link target resolves outside repository: link/../private.md"])

    def test_nested_bullet_links_are_checked(self):
        self.state.write_text(STATE + "\n- Main obligation\n    - [nested](missing.md)\n", encoding="utf-8")
        self.assertEqual(check_navigation_file(self.project, check_links=True).errors, ["missing local link target: missing.md"])

    def test_wrapped_nested_list_links_are_checked(self):
        links = "\n- Main route:\n    - Complete proof:\n      [Proof](missing.md)\n"
        self.state.write_text(STATE + links, encoding="utf-8")
        self.assertEqual(check_navigation_file(self.project, check_links=True).errors, ["missing local link target: missing.md"])

    def test_indented_bullet_examples_are_code_without_a_list_context(self):
        self.state.write_text(STATE + "\n\n    - [literal Markdown example](missing.md)\n", encoding="utf-8")
        self.assertEqual(check_navigation_file(self.project, check_links=True).errors, [])

    def test_list_context_ends_at_unindented_new_paragraph(self):
        links = "\n- Route\n  Continuation\n\nOrdinary paragraph.\n\n    - [literal](missing.md)\n"
        self.state.write_text(STATE + links, encoding="utf-8")
        self.assertEqual(check_navigation_file(self.project, check_links=True).errors, [])

    def test_fenced_and_indented_code_nested_in_lists_is_not_checked(self):
        links = '''
- Main route:
    - Complete proof:
      ```markdown
      [literal](missing-one.md)
      ```
      Continuation paragraph.

          [indented code](missing-two.md)
-     [indented item code](missing-three.md)
'''
        self.state.write_text(STATE + links, encoding="utf-8")
        self.assertEqual(check_navigation_file(self.project, check_links=True).errors, [])

    def test_cli_proposal_is_explicitly_not_action_and_changes_no_files(self):
        self.write_sized_state(BYTE_BUDGET + 1)
        for filename in ("goal.md", "progress.md", "subgoal.md", "2026-10-04.md"):
            (self.project / filename).write_text("History must survive.\n", encoding="utf-8")
        (self.project / "memory").mkdir()
        (self.project / "memory" / "events.md").write_text("Existing proposal history.\n", encoding="utf-8")
        before = {p.relative_to(self.project): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.project.rglob("*") if p.is_file()}
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch.object(Path, "write_text", side_effect=AssertionError("write forbidden")), patch.object(Path, "write_bytes", side_effect=AssertionError("write forbidden")), patch.object(Path, "mkdir", side_effect=AssertionError("mkdir forbidden")):
            self.assertEqual(main([str(self.project), "--milestone", "Scoped lemma recorded in notes/proof.md", "--check-links"]), 0)
        after = {p.relative_to(self.project): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.project.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual({p.relative_to(self.project) for p in self.project.rglob("*") if p.is_dir()}, {Path("memory")})
        self.assertIn("CONDITIONAL PROPOSAL ONLY", output.getvalue())
        self.assertIn("milestone (not verified)", output.getvalue())
        self.assertIn("before drafting, archiving, or rewriting", output.getvalue())
        self.assertIn("no action or reminder was sent or recorded", output.getvalue())
        self.assertIn("no proof", output.getvalue())

    def test_cli_errors_and_historical_file_selection_rejected(self):
        self.state.unlink()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.project)]), 1)
        with contextlib.redirect_stderr(io.StringIO()):
            for arguments in (["--file", "progress.md"], ["--milestone", "   "], ["--compact"]):
                with self.subTest(arguments=arguments), self.assertRaises(SystemExit) as caught:
                    main([str(self.project), *arguments])
                self.assertEqual(caught.exception.code, 2)
        with self.assertRaises(ValueError):
            check_navigation_file(self.project, "memory/events.md")

    def test_actual_creator_templates_pass_navigation_checks(self):
        (self.project / "templates").mkdir()
        for filename in ("research_state.md", "subgoal_plan.md"):
            shutil.copyfile(ROOT / "templates" / filename, self.project / "templates" / filename)
        created = create_project(self.project, "new_problem", "Unicode 数学")
        for filename in ("research_state.md", "subgoal.md"):
            with self.subTest(filename=filename):
                result = check_navigation_file(created, filename, check_links=True)
                self.assertEqual(result.errors, [])
                self.assertIn("Unicode 数学", (created / filename).read_text(encoding="utf-8"))
        self.assertTrue((created / "email" / "index.md").is_file())
        self.assertTrue((created / "email" / "attachments").is_dir())


class CompactionPolicyTests(unittest.TestCase):
    def test_policy_preserves_consent_raw_archives_and_lossless_scope(self):
        text = (ROOT / "docs" / "state_compaction.md").read_text(encoding="utf-8")
        compact = " ".join(text.split())
        for required in (
            "only when both", "exceeds", "24,576 bytes", "substantive milestone",
            "Do not create an archive, draft a compressed file, or rewrite",
            "before agreement arrives", "original bytes", "SHA-256", "byte-preserving I/O",
            "Never overwrite an earlier archive", "mathematically lossless", "inbound links",
            "heading anchors", "user pauses", "withdrawn", "8–12 KiB", "existing `memory/events.md`",
            "Do not repeat an outstanding proposal", "progress.md, daily notes and memory logs preserve history",
        ):
            with self.subTest(required=required):
                self.assertIn(required, compact)
        self.assertNotIn("```powershell", text)


if __name__ == "__main__":
    unittest.main()
