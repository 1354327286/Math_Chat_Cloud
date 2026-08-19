---
name: lean-formalization
description: Prepare and carry out an explicitly requested Lean formalization of a named theorem, proof, or manuscript claim in this repository's lean/ subproject. Audit mathematical and referential closure, resolve notation and dependencies, decompose the proof into Lean-sized obligations, stop for user confirmation before installing a missing toolchain, then implement and verify in the same Git repository. Use only when the user explicitly asks to formalize something in Lean, verify it with Lean, or use Lean to review a specified theorem or manuscript. Do not invoke merely because Lean could be useful.
---

# Lean Formalization

Work directly with the mathematical sources and the tracked `lean/` subproject
inside this same repository. Do not create transport packets, request manifests,
inbox/outbox copies, or return bundles for this workflow. The mathematical plan
and Lean code are linked by an index, not transferred between repositories.

## Freeze one exact target

Resolve the selected research problem, exact theorem or manuscript claim,
assumptions, authoritative proof source, intended Lean result, and external
result policy. If a manuscript contains several reasonable targets, inventory
them briefly and ask the user which one to formalize. Do not silently choose a
different claim, weaken the conclusion, or add assumptions.

Use one of two modes:

- `theorem-verification`: formalize one exact theorem or a bounded,
  dependency-closed group of lemmas.
- `manuscript-review`: inspect the named manuscript for formalization readiness,
  classify its claims, and proceed only with the exact claim selected by the
  user or uniquely fixed by context.

## Audit before using Lean

Read the relevant mathematical source and test six closure conditions:

1. **Statement closure:** all variables, structures, maps, ambient categories,
   topologies, finiteness hypotheses, conventions, and quantifiers are explicit.
2. **Referential closure:** replace “above”, “similarly”, “the natural map”,
   local equation numbers, unnamed constructions, and vague citations with
   exact definitions or statements.
3. **Proof closure:** expose reductions, case splits, functoriality, equality
   transports, existence choices, and uses of classical logic. A known gap,
   circular step, or conditional argument is not ready for verification.
4. **Dependency closure:** arrange all required lemmas in an acyclic order and
   give each an exact mathematical statement and source location.
5. **Encoding readiness:** identify intended Lean objects, definitions, and
   likely library interfaces where known. Keep uncertain library alignment as
   an encoding question rather than a mathematical claim.
6. **Acceptance closure:** fix the final declaration, `sorry` policy, permitted
   external theorems, required checks, full build command, and axiom audit.

For manuscript review, classify each relevant claim as `ready`,
`blocked-mathematics`, `blocked-reference`, `blocked-scope`, or
`encoding-question`. Do not start formalizing a blocked claim merely to see what
happens.

## Produce the formalization plan

Use [assets/formalization_plan.md](assets/formalization_plan.md). Save a durable
plan as `<problem_dir>/memory/formalization/<slug>.md` when the request is part
of persistent research work; otherwise return it directly in the chat.

The plan must contain:

- a self-contained theorem statement and notation table;
- the authoritative source locations;
- an environment layer: imports, namespace, variables, structures, and local
  definitions;
- a dependency-ordered lemma ledger, with one exact obligation per item;
- for each item, the intended Lean role and one of `local-proof`,
  `library-candidate`, `external-boundary`, or `encoding-question`;
- the final theorem assembly;
- required focused checks, project build, `sorry` search, and `#print axioms`;
- a readiness verdict and any blockers.

Keep obligations small enough that a failure identifies one mathematical or
encoding issue. Do not split so aggressively that every line becomes a lemma;
preserve natural mathematical interfaces and reusable constructions.

## Stop before infrastructure changes

If the Lean toolchain is not already available, present the plan, readiness
verdict, dependency count, expected final declaration, and unresolved encoding
questions, then stop. Do not download or install elan, Lean, Lake, Mathlib, or
other infrastructure until the user explicitly confirms setup. The tracked
`lean/` scaffold may be inspected read-only before confirmation; do not use its
existence as permission to run `scripts/bootstrap_lean.sh --install`. The
confirming instruction satisfies this checkpoint; do not ask twice.

## Implement after confirmation

Use `lean/` as a subproject in the current repository and shared Git history;
never initialize `lean/.git` and never register `lean/` as a mathematical project. Do
not assume a Windows drive or fixed cloud path. Before editing or running Lean,
read both root `AGENTS.md` and `lean/AGENTS.md`, then inspect `lean-toolchain`,
the Lake configuration and manifest, imports, namespace conventions, and
existing relevant declarations.

Implement the dependency plan in order. Reuse a library result only after
checking its exact hypotheses and conclusion. If Lean exposes a mathematical
gap or semantic ambiguity, stop that branch of implementation and update the
plan; do not repair it by changing the requested theorem or hiding an obligation
in a structure, typeclass, adapter, opaque declaration, or extra hypothesis.

Run focused checks after each coherent unit and the repository's required full
build at the end. Inspect remaining `sorry`, declarations introduced as axioms,
`#print axioms` for the final result, external boundaries, and exact
source-to-declaration correspondence.

Own this evidence and semantic audit as the agent performing the workflow. Do
not hand the default verification burden to the user or ask them to inspect Lean
code. Request a user decision only for a materially ambiguous mathematical
target, hypothesis change, or external-boundary policy, then complete the audit
yourself once that decision is fixed.

## Record the exact outcome

Classify the result as `verified`, `verified-with-documented-boundaries`,
`encoding-blocked`, `mathematically-blocked`, or `environment-blocked`.
Compilation alone does not establish that the requested theorem was verified.
Update the mathematical research state only after checking statement
correspondence and the complete Lean evidence. Keep code under `lean/`, update
`lean/FORMALIZATION_INDEX.md`, and preserve the repository's single Git history.
Publish or push only with the user's authorization.
