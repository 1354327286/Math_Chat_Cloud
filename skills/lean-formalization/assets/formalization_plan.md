# Lean Formalization Plan

- Mode: `theorem-verification` | `manuscript-review`
- Source problem:
- Selected theorem or claim:
- Readiness: `ready` | `blocked-mathematics` | `blocked-reference` | `blocked-scope` | `encoding-question`

## Exact statement and assumptions

Write a self-contained mathematical statement with all ambient data and quantifiers.

## Notation and referential closure

Resolve notation, constructions, equation references, pronouns, and citations to exact meanings and source locations.

## Mathematical closure audit

Record the checked proof steps and every missing, circular, conditional, or ambiguous step. A `ready` verdict permits no known mathematical gap.

## Intended Lean environment

List likely imports, namespace, variables, structures, local definitions, coercions, universe choices, and known encoding questions.

## Dependency-ordered obligations

For each item record:

- ID and exact mathematical statement;
- dependencies;
- authoritative source location;
- intended Lean declaration or role;
- status: `local-proof` | `library-candidate` | `external-boundary` | `encoding-question`.

## Final assembly

Describe how the obligations produce the exact requested final declaration.

## Verification contract

Record the final declaration name or signature, `sorry` policy, allowed external boundaries, focused checks, full build command, `sorry` search, `#print axioms`, and required statement-correspondence audit.

## Infrastructure checkpoint

- `lean/` subproject scaffold available: yes | no
- Pinned toolchain and manifest available: yes | no
- User has authorized setup: yes | no
- Next permitted action:
