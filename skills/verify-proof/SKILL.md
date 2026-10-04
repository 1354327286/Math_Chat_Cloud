---
name: verify-proof
description: Perform a complete Codex self-review of an assembled proof draft and prepare it for human mathematical review. Use when a candidate proof of the full agreed target exists, including an explicitly selected self-contained intermediate theorem or manuscript target, not an exploratory fragment or a silently weakened substitute for the requested theorem.
---

# Verify Proof

Audit a complete proof draft using the repository's reasoning and reference-checking workflows.

This is a careful Codex self-review, not formal verification and not an independent verification service. The final report is intended for human reading and judgment.

## Preconditions

- The exact theorem statement, assumptions and agreed review scope are available.
- A coherent proof draft of the full agreed target has been identified in the
  current problem directory or conversation. The target may be the project's
  main theorem, an explicitly selected self-contained intermediate theorem, or
  the precise theorem set of the agreed manuscript.
- The selected scope matches the user's request. Do not silently weaken the
  requested target, add assumptions, or substitute an isolated solved subgoal.
- Known failures and unresolved subgoals have been read.

"Full target" is scoped to the agreed deliverable, not automatically to every
open goal in the research project. An explicitly requested intermediate theorem
can receive a complete audit when its own proof and dependencies are closed.
If the draft proves only part of the requested target, classify it as a partial
result and return to the relevant subgoal instead of treating it as a full proof.
Resolve a genuinely ambiguous scope before proceeding; do not silently narrow
it to what is easiest to audit.

## Procedure

1. Confirm that the proof's conclusion exactly matches the full agreed target and all its hypotheses and quantifiers.
2. Apply `$verify-sequential-statements` to the entire proof in order.
3. Apply `$check-referenced-statements` to every external result on which a material step depends.
4. Test central or fragile intermediate claims with examples or counterexamples when useful.
5. Recheck global consistency: notation, dependencies, circularity, limits, completions, descent, base change, and finiteness assumptions.
6. Apply `$synthesize-verification-report` to produce the final human-readable audit.
7. Classify material claims as `proved`, `conditional`, `plausible`, `needs verification`, or `false`.
8. Reuse valid earlier audit evidence for unchanged inputs, with its actual scope
   and revision identified. Recheck changed statements and affected downstream
   uses; an old success label cannot certify a new proof.
9. Do not rename a draft as verified merely because no issue was found. Say `no critical issue found in this review` and retain residual human-review points.

## Independent Review Boundary

This skill is a mathematical self-review. It is not independent review, even
when performed as a separate pass by the authoring agent. After substantive
mathematical edits during manuscript writing, obtain the affected independent
mathematical review required by
[the writing skill](../write-self-contained-math-proof/SKILL.md#recheck-substantive-mathematical-changes).
Keep its reviewer, scope, evidence and revision distinct from this self-review.
An unavailable independent review is a blocker where required, not permission
to relabel this audit. Formatting and compilation cannot upgrade proof status.

## Persistence

For persistent work, save the full audit in the current daily note or a clearly named file under `<problem_dir>/notes/`. Record reusable gaps and invalid routes in `memory/failed_paths.md`, established consequences in `memory/immediate_conclusions.md`, and source findings in `memory/search_results.md`. Update detailed files before refreshing `research_state.md`.
