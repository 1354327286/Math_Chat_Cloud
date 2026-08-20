# Lean Subproject Instructions

These rules apply to every file under `lean/` and extend the repository-root
`AGENTS.md`. Read both files before any Lean work. If they conflict, this file
controls Lean implementation details while the root file controls project,
privacy, delegation, and Git safety.

## Activation and Setup Gate

Use this subproject only after the user explicitly requests Lean formalization,
Lean verification, or Lean review of a named result and the workflow in
`skills/lean-formalization/SKILL.md` has produced a ready plan.

Do not install or update elan, Lean, Lake, Mathlib, or other dependencies merely
because `lean/` exists. If the toolchain is absent, `scripts/bootstrap_lean.sh
--check` is read-only. Run `scripts/bootstrap_lean.sh --install` only after the
user explicitly authorizes setup. Do not guess a toolchain version or hand-edit
generated dependency pins to make a build appear reproducible.

## Mathematical Authority

The authoritative mathematical target and dependency plan live in
`<problem_dir>/memory/formalization/<slug>.md` or in the exact one-off plan
accepted by the user. Every Lean declaration must trace to an obligation in that
plan.

Never silently weaken a conclusion, strengthen a hypothesis, replace an object
by a more convenient surrogate, or hide an unproved obligation behind a
structure, typeclass, coercion, adapter, opaque definition, or namespace choice.
When Lean reveals a mathematical gap or ambiguous interface, stop that branch,
record the mismatch in the plan, and report it.

## Source Layout

```text
lean/
├── MathDailyLean.lean
├── MathDailyLean/Common/
├── MathDailyLean/Projects/<problem_name>/
└── FORMALIZATION_INDEX.md
```

Match `<problem_name>` to a path in the merged public/local project registry. Put
problem-specific definitions and theorems in that project's module directory.
Move code into `Common/` only after at least two formalizations genuinely share
the same mathematical interface. Keep the top-level `MathDailyLean.lean` import
surface small and intentional.

Everything below `MathDailyLean/Projects/` except its public `README.md` is
Git-ignored private research data. It travels with the matching problem bundle;
never force-add it to the public repository. Keep the mathematical plan, Lean
module, final declaration, status, and audit command in the matching
`<problem_dir>/memory/formalization/` record. `FORMALIZATION_INDEX.md` is only
for explicitly public examples and must not contain private problem names or
mappings. Never copy private mathematical notes into tracked Lean comments or
documentation.

## Implementation Discipline

Before editing:

1. inspect `lean-toolchain`, `lakefile.toml`, `lake-manifest.json` when present;
2. inspect existing imports, namespaces, and nearby declarations;
3. search Mathlib for an exact candidate before recreating it;
4. check the candidate's full type, hypotheses, universes, and relevant
   typeclass assumptions;
5. implement the accepted dependency DAG in order.

Keep proof obligations small enough to isolate one mathematical or encoding
failure, but preserve natural interfaces. Prefer explicit local definitions and
lemmas over automation whose behavior obscures the proof boundary.

No production declaration may contain `sorry` or `admit`. Do not introduce an
`axiom`, `opaque` stand-in, or unsafe escape hatch for a missing proof. A theorem
from Mathlib is an external dependency, not an unverified local boundary; record
its exact declaration. Any genuinely assumed external mathematical boundary
must be explicit in the accepted plan and visible in the final theorem's axiom
audit.

## Validation

After each coherent unit, run the narrowest relevant check, for example:

```bash
cd lean
lake env lean MathDailyLean/Projects/<problem_name>/<Module>.lean
```

Before reporting verification, run:

```bash
cd lean
lake build
rg -n '\b(sorry|admit|axiom)\b' MathDailyLean MathDailyLean.lean
```

Also add or run an appropriate `#print axioms <final_declaration>` audit and
inspect its output. Confirm all of the following:

- the compiled declaration is exactly the requested statement;
- definitions, coercions, and structures have the intended semantics;
- every planned dependency is proved locally or mapped to an exact library
  result;
- no hidden hypothesis or external boundary entered during encoding;
- focused checks and the full build succeeded in the pinned environment.

The agent carrying out the formalization owns this complete semantic audit. Do
not describe it as a human or manual verification step, and do not shift the
default burden of reading Lean code or checking the evidence to the user. Ask
the user only when a genuine mathematical choice remains, such as selecting
between non-equivalent statements, additional hypotheses, or external-boundary
policies; after that choice is fixed, perform the audit yourself.

Compilation alone is not mathematical verification.

## Outcomes and Persistence

Classify the result as `verified`, `verified-with-documented-boundaries`,
`encoding-blocked`, `mathematically-blocked`, or `environment-blocked`. Update
the mathematical problem state only after statement correspondence and the full
evidence audit succeed.

The Lean framework, `lean-toolchain`, and `lake-manifest.json` belong to this
same Git repository. Problem-specific source belongs to the private problem
bundle. Generated `.lake/` state belongs to neither. Never initialize a nested
Git repository under `lean/`, and do not commit or push unless authorized by
the root workflow and the user.
