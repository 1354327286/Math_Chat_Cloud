# Lean Formalization Plan

## Pre-run execution contract

- Contract status: `open` | `accepted`
- Campaign ID or slug:
- Mode: `theorem-verification` | `manuscript-review`
- Source problem or one-off source:
- Exact selected theorem or claim:
- Authoritative source version and locator:
- Intended final Lean declaration and bounded deliverable:
- Acceptance profile: `sorry-free` | `provenance-complete` | `internally-closed`
- Permitted deviations: none | list explicitly
- Goal mode: `ordinary-work` | `persistent-goal`
- Goal outcome, constraints, and verifiable completion criteria:
- If native goal control is unavailable: stop | use the recorded goal-equivalent contract
- Subagents: `forbidden` | `allowed`
- If allowed: role, exposed model, reasoning effort, task, read/write boundary,
  maximum total/concurrent agents, follow-up-round cap, integration/final-audit
  owner, and termination conditions
- Existing pinned toolchain may run: yes | no
- Missing or stale toolchain may be installed/updated: yes | no
- User instruction that fixed this contract:

Do not write implementation code, run Lean/Lake, install infrastructure, set a
goal, or delegate while any applicable field is open.

## Acceptance profile interpretation

Record what the selected profile permits and forbids. `sorry-free` is not a
claim of complete provenance or internal closure. For `provenance-complete`,
every external mathematical input needs an exact source locator. For
`internally-closed`, no literature result may remain merely assumed.

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

## External-input and provenance ledger

For every imported definition, library result, literature theorem, and encoding
boundary, record:

- ID and exact mathematical statement or definition;
- classification: `local-proof` | `exact-library-declaration` |
  `literature-boundary` | `unformalized-concept` | `encoding-assumption`;
- exact Lean declaration, theorem parameter, structure field, or local interface;
- authors, title, version/edition, theorem/definition/proposition number, and
  section/page or another stable exact locator;
- for an unformalized concept, the precise defining source and why the Lean
  interface faithfully represents the part being used;
- if the input is derived, every original component theorem and the ID of the
  local lemma formalizing their combination;
- acceptance status: `accepted` | `missing-source` | `needs-local-proof` |
  `encoding-question`.

Under `provenance-complete` or `internally-closed`, a `missing-source` row blocks
execution. A citation to a derived consequence does not replace citations to
identifiable original component theorems or the formalized combination step.

## Final assembly

Describe how the obligations produce the exact requested final declaration.

## Verification contract

Record the final declaration name and full signature, selected acceptance
profile, allowed external boundaries, focused checks, full build command,
placeholder/unsafe/opaque search, `#print axioms`, external-input ledger audit,
and required statement-correspondence audit.

## Infrastructure checkpoint

- `lean/` subproject scaffold available: yes | no
- Pinned toolchain and manifest available: yes | no
- User has authorized setup: yes | no
- Next permitted action:
