# Assemble a mathematical manuscript

Use this workflow for a multi-result article or substantial reorganization.
Do not apply the full process to a short proof, isolated correction or
diagnosis-only request. Keep the mathematical eligibility and deliverable
boundaries in SKILL.md.

## Artifacts and authority

For this full assembly path, keep two manuscript-specific management files
beside the editable source; reuse existing records rather than duplicating them:

- THEOREM_LEDGER.md, from [the result template](../assets/theorem-ledger-template.md):
  the precise results, dependencies and evidence selected for this paper.
- PAPER_PLAN.md, from [the plan template](../assets/paper-plan-template.md):
  scope, section architecture, notation, current stage and review issues.

Default location: <problem_dir>/notes/<manuscript>/. Reuse an existing manuscript
location when specified. Keep these records private under the project's existing
rules. Do not create a global theorem database, a new research project, mandatory
proof packets or a separate mode-state file. This ledger is distinct from any
formalization-unit ledger used in the Lean workflow.

Detailed research records remain authoritative evidence; research_state.md is
navigation. The paper ledger selects the exact versions used here, while the
plan governs exposition. Neither can make a false or withdrawn premise valid.
The manuscript is the editable exposition; a generated reader is not another
editable source. Link existing proofs instead of copying a second proof library.
Keep records proportionate: important inputs and editorial decisions need traceability;
routine algebra, every local definition, and every wording edit need no ledger
entry. Reuse still-valid audit evidence rather than rerunning an unchanged audit.

## 1. Inventory the mathematics

Resolve the exact target, assumptions, audience, form and destination first.
Retrieve relevant complete proof sections and sources using project navigation.
For each important local result and material external input, record:

- a stable ID, exact statement, assumptions and conventions;
- local/external dependencies and its role in the main argument;
- canonical proof/source paths and section locators, with the version/date used;
- actual review evidence, limitations and unresolved obligations;
- whether it is included, blocked or excluded from this manuscript.

Locate and read the evidence behind a summary's status label. For external
inputs, retain exact bibliographic/version data, theorem/page locators and
the applicability bridge. Keep original statements distinct from specialized
consequences. Record enough of the selected statement to compare it with the
manuscript; a title and a "proved" label are insufficient.

For a stable canonical external statement, an exact version and locator plus
the fully specified consequence and hypotheses used here can avoid duplicating
its general formulation. Keep the original and specialization distinguishable;
copy the full statement when ambiguity or version comparison requires it.

Inventory may contain blocked candidates, but proof prose uses only entries
that meet the eligibility gate. Check dependency closure, hidden extra
hypotheses and cycles. A closed conditional theorem with its agreed assumptions
is valid; an unproved local lemma cannot be promoted to a hypothesis to pass.

Exit condition: the selected mathematical inputs and remaining blockers are
explicit, traceable and correctly scoped. Inventory is not itself a new audit.

## 2. Design the reader's route

Before polished prose, write PAPER_PLAN.md: exact paper goal, logical spine,
section purposes, input/output results, reader prerequisites, notation, omitted
material and open structural decisions. Organize by mathematical dependencies
and explanation, not the chronology of research.

Translate the ledger into a reader's route rather than copying its dependency
headings. Several technical inputs may serve one section-level question;
one construction may need separate sections for its setup and its use. Titles
should identify the task or output, while opening paragraphs explain why it
is needed. Compare both the resulting contents and the prose roadmap with
the ledger to check that this presentation still preserves every dependency.

Check that every included result has a purpose and that every section can be
understood from its setup and stated inputs. Prefer a user-approved earlier
manuscript's useful architecture when it fits the current mathematics.
An introductory main theorem may precede its proof if its needed definitions
are already available; otherwise give an honest conceptual preview and place
the formal statement after its setup. Forbid circular reasoning and undefined
objects, not all forward references. Introduce shared conventions early and
local definitions near their use.

Treat the proposed structure as a candidate, not a fixed preliminaries /
interfaces / final-proof template. Test it with short trial paragraphs directly
in the eventual manuscript draft: explain the main difficulty, the central proof
mechanism, and a hard transition between sections or arguments. This is part of
the reader-route stage, not an extra file or stage. Check whether the agreed
reader can follow the route; revise the architecture when the trial exposes
missing setup or an unmotivated transition. These paragraphs test exposition,
not a speculative proof: mark unresolved claims as internal planning material
and never use the trial to bypass the eligibility gate.

When coherent, mark the architecture settled for drafting and record the
decision and next action. This is a working baseline, not an approval claim.
If the user requested an outline checkpoint, show it and wait. Otherwise perform
the check and continue within the existing full-writing authorization.

## 3. Build the statement skeleton

Continue in the eventual manuscript source containing the trial paragraphs,
not a separate skeleton copy. Place definitions, exact result statements,
labels and proof locations before filling in proofs. Maintain the mapping between paper IDs and manuscript labels.
Keep source/dependency pointers in the ledger or internal comments.

Check types, hypotheses, dependency order, notation and whether the statement
sequence supports the main theorem. Mark an incomplete skeleton clearly as
internal planning material; do not represent an unresolved candidate as an
established theorem. A compilable skeleton is still not a proof.

Exit condition for proof drafting: the statement sequence is coherent and all
mathematical inputs needed for the requested proof pass the eligibility gate.
If not, report the exact blocker and return that issue to research. Do not
silently narrow the paper, manufacture a research task or start an autonomous run.

## 4. Draft sections and review before repairing

Work with the plan, relevant ledger entries, their complete proof/source sections,
global notation and neighboring section interfaces. Retrieve additional material
when a real dependency requires it; do not substitute a ledger summary for a proof.

Write one coherent section at a time. Preserve statements and hypotheses while
explaining the existing argument. Expanding established reasoning, changing
notation consistently or splitting proof steps is exposition. A new load-bearing
lemma, assumption or quantifier change, new mathematical input, changed
construction, or materially different argument requires source reconciliation
and independent mathematical review of the affected argument and downstream
uses before delivery as closed. Use the review boundary in
[the writing skill](../SKILL.md#recheck-substantive-mathematical-changes). A
self-review cannot supply this independent review; if an authorized distinct
reviewer or review route is unavailable, report the blocker and pause the
affected delivery.

Review the section for the agreed target reader without rewriting it first.
Record substantive actionable issues with location, severity, reason/evidence
and affected result IDs in PAPER_PLAN.md.
Check fidelity to the ledger, assumptions, notation, dependencies, transitions,
citations, overstatement and repetition. Then repair the substantiated issues
within scope; do not use the repair pass for unrelated whole-paper rewriting.
Mark an issue resolved only with a repair location and a recheck.

The same agent may perform these separate editorial passes; call this
self-review, not independent review. That does not replace the independent
mathematical review required after substantive mathematical edits. Use only
review routes within the user's authorization; request missing authorization
rather than claiming an unavailable review was done.
Continue until material issues are resolved; avoid repeated stylistic polishing
with no identified problem. Persist the next action for interrupted work.

## 5. Coordinate the whole manuscript and deliver

Compare all formal statements and actual uses with the ledger, including the
abstract and introduction. Check dependency closure, changes of scope, notation
across sections, repeated definitions/results, omitted proof steps and citations.
Verify that the roadmap describes the proof actually written. Finalize the
abstract/introduction from the stabilized body, then complete the language and
notation pass for the agreed target reader. Explanatory prose may stay inside
proofs where it clarifies a deduction or difficult transition. Technical proofs
may sit in appendices, including load-bearing proofs, if the main text exposes
their statements, role and dependency links and the full proofs are supplied.

Use verify-proof for the complete mathematical self-review and the LaTeX review
skill for build, numbering and rendered-page checks when applicable, as routed
by SKILL.md. Perform the email-index and attribution checks only at manuscript
finalization, following [the email workflow](../../../docs/email_workflow.md).
Reuse valid source/audit evidence; recheck changed statements and their affected
uses. Internal issue lists and source paths do not belong in
reader-facing proof prose.

Delivery requires the exact requested theorem to be proved with no known
material gap, completed exposition checks and the requested artifact checks.
Keep current review records tied to the delivered revision; formatting or a
clean build cannot upgrade mathematical status.

## Changes and resumption

On resumption, read the plan's current stage, selected ledger entries, relevant
source changes/withdrawals and latest manuscript revision. Reconcile conflicts
before using affected inputs; do not blindly restart all stages.

- A stronger new research result need not replace a still-correct selected
  version. Adopt it only with an explicit reconciliation of the paper's scope,
  ledger, affected proofs and plan.
- A withdrawn or erroneous selected premise blocks its downstream uses even
  when the plan was settled. Preserve the old evidence, record the issue,
  and recheck affected arguments before continuing or delivering them.
- A structural change needs a reason, impact assessment and plan update.
  Routine within-scope repairs need no repeated permission; changes to the
  user's mathematical target or unresolved choices do.

Use the existing research memory for genuinely new mathematical findings or
failures, and the paper plan for editorial decisions. Rewriting correct
mathematics does not constitute new research progress.
