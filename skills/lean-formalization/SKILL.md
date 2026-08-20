---
name: lean-formalization
description: Prepare and carry out an explicitly requested Lean formalization of a named theorem, proof, or manuscript claim in this repository's lean/ subproject. First resolve a mandatory execution contract covering the exact target, acceptance and literature-provenance standard, persistent-goal choice, subagent authorization/model/reasoning limits, and toolchain setup. Then audit mathematical and referential closure, decompose the proof into Lean-sized obligations, implement, and verify in the same Git repository. Use only when the user explicitly asks to formalize something in Lean, verify it with Lean, or use Lean to review a specified theorem or manuscript. Do not invoke merely because Lean could be useful.
---

# Lean Formalization

Work directly with the mathematical sources and the tracked `lean/` subproject
inside this same repository. Do not create transport packets, request manifests,
inbox/outbox copies, or return bundles for this workflow. The mathematical plan
and Lean code are linked by the selected problem's private formalization record,
not transferred between repositories.

## Resolve the pre-run contract

Treat one **run** as one bounded formalization campaign under a frozen contract,
not as each individual `lake` or `lean` command. Resolve the contract again for
a new target, a materially changed contract, or a completed or abandoned
campaign that is being restarted. Within one active campaign, reuse the accepted
contract without repeatedly interrupting compilation.

Before the first persistent plan write, goal activation, Lean source edit,
toolchain installation or update, Lean/Lake command, or subagent delegation,
ask for and record all of the following:

1. **Target:** selected problem or one-off source, exact theorem or manuscript
   claim, authoritative source version/location, mode, assumptions, intended
   final Lean declaration, and bounded deliverable.
2. **Acceptance profile:** exactly one of `sorry-free`,
   `provenance-complete`, or `internally-closed`, plus any permitted deviations.
3. **Goal mode:** `ordinary-work` or `persistent-goal`. For a persistent goal,
   record its outcome, constraints, verifiable completion criteria, and what to
   do if the current client has no native goal control; never claim that a goal
   was activated when it was only written into the plan.
4. **Subagents:** `forbidden` or `allowed`. If allowed, record the exposed model
   and reasoning effort for every role, role/task, read/write boundary, maximum
   total and concurrent agents, follow-up-round cap, integration and final-audit
   owner, and termination conditions. Use only models actually exposed in the
   current environment. An ordinary subagent is not Pro. Do not spawn anything
   until every field is fixed.
5. **Environment:** whether the existing pinned toolchain may be run and,
   separately, whether missing or stale infrastructure may be installed or
   updated.

Do not infer permission from silence, a previous campaign, or a generic
instruction such as “continue” or “formalize this.” If the user's request already
supplies every field, restate the frozen contract compactly and proceed without
a redundant confirmation. Otherwise ask focused questions and wait. Read-only
orientation may continue while waiting, but do not perform any action named
above.

The acceptance profiles mean:

- `sorry-free`: the target and local obligations compile without `sorry`,
  `admit`, a new global `axiom`, an unsafe escape hatch, or an opaque stand-in
  for a missing proof. Every remaining external boundary is explicit in the
  theorem signature and dependency ledger, and every reused library result is
  identified by its exact declaration. This is a syntactic and dependency-
  visibility bar; it does **not** by itself establish complete literature
  provenance or internal mathematical closure.
- `provenance-complete`: includes `sorry-free`. Every mathematical input not
  proved locally or supplied by an exact library declaration also has a precise
  citation: authors, title, version or edition, theorem/definition/proposition
  number, and section/page or another stable exact locator. A concept not yet
  formalized in the library, such as a prismatic notion, requires the precise
  source location of its definition and an explicit account of the Lean
  interface used for it. If a used property is a combination of literature
  results, cite the original component theorems and formalize the combination
  as a local lemma; citing only the derived consequence is insufficient.
- `internally-closed`: includes `provenance-complete`, and no literature result
  remains merely assumed. Each dependency is an exact accepted library theorem
  or is proved locally from the encoded definitions. Record any agreed standard
  logical axioms or noncomputable principles separately.

A missing exact source blocks `provenance-complete` or `internally-closed` with
`blocked-reference`; it is not silently downgraded to `sorry-free`. A
`provenance-complete` result with explicit unformalized boundaries is
`verified-with-documented-boundaries`, not `verified`.

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
6. **Acceptance closure:** confirm that the pre-run acceptance profile is
   achievable; fix the final declaration, permitted external inputs, precise
   source obligations, required checks, full build command, signature audit,
   and axiom audit.

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
- an external-input ledger containing every library result, literature theorem,
  imported definition, and encoding boundary, with the exact statement, Lean
  representation, source locator, and acceptance status;
- for every derived literature input, its original component theorems and the
  local Lean lemma that formalizes their combination;
- the final theorem assembly;
- required focused checks, project build, placeholder search, final-signature
  inspection, and `#print axioms`;
- a readiness verdict and any blockers.

Keep obligations small enough that a failure identifies one mathematical or
encoding issue. Do not split so aggressively that every line becomes a lemma;
preserve natural mathematical interfaces and reusable constructions.

## Stop before infrastructure changes

If the Lean toolchain is not already available, present the plan, readiness
verdict, dependency count, expected final declaration, and unresolved encoding
questions, then stop unless the accepted pre-run contract already authorized
installation. Do not download or install elan, Lean, Lake, Mathlib, or other
infrastructure without that explicit field. The tracked `lean/` scaffold may be
inspected read-only before confirmation; do not use its existence as permission
to run `scripts/bootstrap_lean.sh --install`. The accepted contract satisfies
this checkpoint; do not ask twice.

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
unsafe or opaque stand-ins, `#print axioms` for the final result, the full final
signature, external boundaries, and exact source-to-declaration correspondence.
For `provenance-complete` and `internally-closed`, audit every external-input
ledger row against the cited source. Verify locally formalized combinations
against their original component theorems rather than accepting a secondary
summary.

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
correspondence and the complete Lean evidence. Keep private plans, code mappings,
and audit results in `<problem_dir>/memory/formalization/`; update
`lean/FORMALIZATION_INDEX.md` only for an explicitly public example. Preserve
the repository's single Git history. Publish or push only with the user's
authorization.
