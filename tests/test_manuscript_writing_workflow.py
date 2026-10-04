"""Static contracts for the instruction-only manuscript writing workflow.

These tests protect routing, proof/review boundaries, and the runnable local
links agents follow. They do not claim to assess a mathematical argument.
"""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
WRITING = ROOT / "skills/write-self-contained-math-proof"
REVIEW = ROOT / "skills/review-latex-math-manuscript"
VERIFY = ROOT / "skills/verify-proof/SKILL.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def compact(text: str) -> str:
    return " ".join(text.split())


def section(text: str, title: str) -> str:
    """Extract a level-two section, so a contract cannot pass in the wrong path."""
    marker = f"## {title}\n"
    if marker not in text:
        raise AssertionError(f"Missing workflow section: {title}")
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def heading_anchors(text: str) -> set[str]:
    anchors = set()
    for heading in re.findall(r"^#{1,6}\s+(.+)$", text, flags=re.MULTILINE):
        plain = re.sub(r"[^\w\s-]", "", heading.lower())
        anchors.add(re.sub(r"\s", "-", plain))
    return anchors


class ManuscriptWritingWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.writing = read(WRITING / "SKILL.md")
        cls.assembly = read(WRITING / "references/manuscript-assembly.md")
        cls.plan = read(WRITING / "assets/paper-plan-template.md")
        cls.ledger = read(WRITING / "assets/theorem-ledger-template.md")
        cls.template = read(WRITING / "assets/review-proof-template.md")
        cls.review = read(REVIEW / "SKILL.md")
        cls.verify = read(VERIFY)

    def test_short_proof_and_local_edit_have_lightweight_paths(self):
        route = compact(section(self.writing, "Choose The Writing Path"))
        for contract in (
            "For a short standalone proof, use the eligibility check",
            "Do not create manuscript-management files for a small task",
            "local correction or style-only revision",
            "Reuse any existing ledger/plan",
            "do not require a retrospective inventory of the whole project",
            "Do not create a ledger or plan for every routine edit",
            "recheck the changed passage and its affected uses",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, route)
        self.assertIn("Do not apply the full process to a short proof", compact(self.assembly))
        self.assertIn("chat-only requests", self.writing)

    def test_assembly_has_exactly_five_ordered_stages(self):
        stages = re.findall(r"^## (\d+)\. (.+)$", self.assembly, re.MULTILINE)
        self.assertEqual(stages, [
            ("1", "Inventory the mathematics"),
            ("2", "Design the reader's route"),
            ("3", "Build the statement skeleton"),
            ("4", "Draft sections and review before repairing"),
            ("5", "Coordinate the whole manuscript and deliver"),
        ])
        self.assertIn(
            "<inventory / reader route / statement skeleton / section writing and review / global coordination>",
            self.plan,
        )
        self.assertIn("Do not ask for approval at each stage unless", self.writing)
        self.assertIn("If the user requested an outline checkpoint, show it and wait", self.assembly)

    def test_trial_paragraphs_belong_to_reader_route_in_the_actual_draft(self):
        route = compact(section(self.assembly, "2. Design the reader's route"))
        for required in (
            "trial paragraphs directly in the eventual manuscript draft",
            "main difficulty",
            "central proof mechanism",
            "hard transition",
            "not an extra file or stage",
            "never use the trial to bypass the eligibility gate",
        ):
            self.assertIn(required, route)
        skeleton = compact(section(self.assembly, "3. Build the statement skeleton"))
        self.assertIn("source containing the trial paragraphs", skeleton)
        self.assertIn("not a separate skeleton copy", skeleton)

    def test_records_are_manuscript_scoped_and_proportionate(self):
        authority = compact(section(self.assembly, "Artifacts and authority"))
        self.assertIn("<problem_dir>/notes/<manuscript>/", authority)
        self.assertIn("two manuscript-specific management files", authority)
        self.assertIn("THEOREM_LEDGER.md", authority)
        self.assertIn("PAPER_PLAN.md", authority)
        self.assertIn("Do not create a global theorem database", authority)
        self.assertIn("Reuse still-valid audit evidence", authority)
        self.assertIn("every wording edit need no ledger entry", authority)
        self.assertIn("Evidence: <canonical proof path and section; selected version/date>", self.ledger)
        self.assertIn("Assumptions and conventions:", self.ledger)
        self.assertIn("Dependencies:", self.ledger)
        self.assertIn("Unresolved obligations:", self.ledger)
        self.assertIn("Routine substantiated repairs proceed", self.plan)

    def test_eligibility_is_not_certified_by_a_ledger_or_compilable_skeleton(self):
        gate = compact(section(self.writing, "Enforce The Eligibility Gate"))
        for required in (
            "complete proof dependency chain",
            "every local lemma used in the argument has a closed proof",
            "verified statement, source, hypotheses, and applicability check",
            "Never promote an unproved local lemma to an assumption",
            "not a review proof",
            "Creating a ledger does not itself audit or certify any entry",
        ):
            self.assertIn(required, gate)
        self.assertIn("A compilable skeleton is still not a proof", self.assembly)
        self.assertIn("do not deliver the document with a caveat", self.writing)

    def test_reader_route_is_not_a_fixed_section_scheme(self):
        exposition = compact(section(self.writing, "Write The Document"))
        self.assertIn("not a fixed table of contents", exposition)
        self.assertIn("a separate final-proof section is optional", exposition)
        self.assertIn("candidate structure, not a fixed table of contents", self.template)
        self.assertIn("preliminaries / interfaces / final-proof", compact(self.template))
        self.assertNotRegex(self.template, r"(?m)^## [234]\. ")
        self.assertNotIn("Use this order unless", self.writing)

    def test_definitions_and_formal_statements_follow_the_reader(self):
        exposition = compact(section(self.writing, "Write The Document"))
        self.assertIn("formal theorem after the definitions needed", exposition)
        self.assertIn("honest conceptual preview", exposition)
        self.assertIn("shared conventions and heavily reused terminology early", exposition)
        self.assertIn("local definitions near their first substantive use", exposition)
        final_pass = compact(section(self.writing, "Perform The Final Language And Notation Pass"))
        self.assertIn("agreed target reader", final_pass)
        self.assertIn("adjacent-specialty reader may provide an optional stress test", final_pass)
        self.assertIn("do not silently change the target audience", final_pass)
        self.assertIn("no separate terminology or symbol ledger", final_pass)
        for reader_question in (
            "name the core difficulty",
            "explain why the key construction works",
            "see why the next step is needed",
        ):
            self.assertIn(reader_question, final_pass)

    def test_proof_explanation_and_appendices_keep_dependencies_visible(self):
        self.assertIn("Explanatory prose belongs inside proofs", self.writing)
        exposition = compact(section(self.writing, "Write The Document"))
        self.assertIn("including load-bearing proofs, may go in an appendix", exposition)
        self.assertIn("dependency links stay visible", exposition)
        self.assertIn("complete appendix proof is supplied", exposition)
        self.assertIn("an appendix cannot conceal an unresolved obligation", self.template)
        self.assertNotIn("not inside its final deductions", self.writing)
        self.assertNotIn("Do not move a load-bearing step out of the main proof", self.template)

    def test_substantive_changes_require_affected_independent_review(self):
        boundary = compact(section(self.writing, "Recheck Substantive Mathematical Changes"))
        for required in (
            "changed hypotheses or quantifiers",
            "changed construction",
            "obtain independent mathematical review",
            "affected downstream uses",
            "authoring agent is self-review, not independent review",
            "authorization is missing",
            "pause the affected delivery",
            "Do not silently substitute self-review",
            "A wording-only repair or consistent renaming is not a new mathematical claim",
        ):
            self.assertIn(required, boundary)
        self.assertIn("independent mathematical review", self.assembly)
        self.assertIn("Self-review is not independent review", self.plan)
        self.assertIn("Self-review is not independent review", compact(self.review))

    def test_latex_review_allows_later_proofs_but_not_invalid_dependencies(self):
        references = compact(section(self.review, "Audit Numbering And References"))
        self.assertIn("explicit references to complete later proofs are allowed", references)
        for error in ("circular reasoning", "undefined object", "unclosed proof dependency"):
            self.assertIn(error, references)
        self.assertNotIn("forward dependency remains", self.review)
        self.assertIn("diagnosis-only", self.review)
        self.assertIn("without editing", self.review)
        self.assertIn("Do not create management files", compact(self.review))

    def test_email_checks_are_finalization_only_and_reader_remains_opt_in(self):
        delivery = compact(section(self.writing, "Delivery And Persistence"))
        self.assertIn("At manuscript finalization", delivery)
        self.assertIn("not a new email-index obligation for each short proof or routine local edit", delivery)
        finalization = compact(section(self.review, "Manuscript Finalization"))
        self.assertIn("not to every short proof, compile check or routine local edit", finalization)
        self.assertIn("do not authorize sending email", finalization)
        self.assertIn("Do not create a reader companion merely because a TeX file exists", self.review)
        self.assertIn("never hand-edit it", self.review)
        self.assertIn("--check", self.review)

    def test_full_target_means_exact_agreed_deliverable_not_a_weaker_theorem(self):
        preconditions = compact(section(self.verify, "Preconditions"))
        self.assertIn('"Full target" is scoped to the agreed deliverable', preconditions)
        self.assertIn("explicitly selected self-contained intermediate theorem", preconditions)
        self.assertIn("precise theorem set of the agreed manuscript", preconditions)
        self.assertIn("Do not silently weaken the requested target", preconditions)
        self.assertIn("only part of the requested target", preconditions)
        self.assertIn("classify it as a partial result", preconditions)
        independent = compact(section(self.verify, "Independent Review Boundary"))
        self.assertIn("It is not independent review", independent)
        self.assertIn("An unavailable independent review is a blocker", independent)

    def test_resume_reconciles_selected_evidence_without_starting_over(self):
        resume = compact(section(self.assembly, "Changes and resumption"))
        self.assertIn("do not blindly restart all stages", resume)
        self.assertIn("withdrawn or erroneous selected premise blocks its downstream uses", resume)
        self.assertIn("Preserve the old evidence", resume)
        self.assertIn("need not replace a still-correct selected version", resume)

    def test_all_instruction_links_and_fragments_resolve_inside_checkout(self):
        paths = sorted(WRITING.rglob("*.md")) + [REVIEW / "SKILL.md", VERIFY]
        destinations = set()
        for source in paths:
            for href in re.findall(r"\[[^\]]+\]\(([^\s)]+)\)", read(source)):
                with self.subTest(source=source.relative_to(ROOT), href=href):
                    parsed = urlsplit(href)
                    if parsed.scheme or parsed.netloc:
                        continue
                    target = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source
                    self.assertTrue(target.is_relative_to(ROOT), href)
                    self.assertTrue(target.is_file(), f"Broken workflow link: {source}: {href}")
                    destinations.add(target.relative_to(ROOT).as_posix())
                    if parsed.fragment:
                        self.assertIn(unquote(parsed.fragment), heading_anchors(read(target)))
        self.assertTrue({
            "skills/write-self-contained-math-proof/references/manuscript-assembly.md",
            "skills/write-self-contained-math-proof/assets/paper-plan-template.md",
            "skills/write-self-contained-math-proof/assets/theorem-ledger-template.md",
            "skills/write-self-contained-math-proof/assets/review-proof-template.md",
            "skills/verify-proof/SKILL.md",
            "skills/review-latex-math-manuscript/SKILL.md",
            "docs/email_workflow.md",
        }.issubset(destinations))

    def test_skill_ui_prompts_match_paths_and_review_boundaries(self):
        writing_ui = read(WRITING / "agents/openai.yaml")
        review_ui = read(REVIEW / "agents/openai.yaml")
        self.assertIn("$write-self-contained-math-proof", writing_ui)
        self.assertIn("lightweight path", writing_ui)
        self.assertIn("global coordination", writing_ui)
        self.assertIn("independent mathematical review", writing_ui)
        self.assertIn("$review-latex-math-manuscript", review_ui)
        self.assertIn("target reader", review_ui)
        self.assertIn("legitimate previews and later proofs", review_ui)


if __name__ == "__main__":
    unittest.main()
