---
name: formalization-handoff
description: Export an internally audited mathematical proof from a registered research problem for controlled Lean verification in a separately provided repository, stage and verify immutable packets, prepare or import Lean-side results, and audit source recovery or source drift. Use when the user explicitly asks to export a specific result for Lean formalization, stage an existing packet to an authorized Lean repository available in the current workspace, inspect a formalization source query, or import returned Lean evidence. Do not use for ordinary proof discussion or merely because a proof might eventually benefit from Lean.
---

# Formalization Handoff

Keep the research problem and Lean repository independent. Exchange one
immutable, source-traceable task packet; never register the Lean repository in
the mathematical project registry, copy it into this repository, or treat compilation alone as a
mathematical review.

## Apply the export gate

Export only when all conditions hold:

1. The user explicitly asks to export a proof for Lean verification.
2. The exact mathematical conclusion and its hypotheses are identified.
3. The user specifies the intended output result. Also determine whether the
   result must be sorry-free or may cite documented external results.
4. An internal audit of the supplied proof reports no known mathematical gap.
5. A dependency-ordered, source-traceable lemma ledger is available.

If the user asks to export but any output detail is unclear, ask what exact
result should be produced. Do not create a draft packet, infer a weaker target,
or silently choose an external-results policy while waiting for clarification.

The `--user-authorized` and `--audit-no-known-gaps` flags record an already-made
decision. They do not allow the script to decide mathematical eligibility.

## Read the contract

Before exporting, staging, recovering source context, preparing a result, or
importing one, read [references/packet-contract.md](references/packet-contract.md).
Follow its file roles, source-recovery order, defect boundary, and acceptance
criteria.

## Export from one registered problem

Use project-relative source files. Keep preparatory proof, audit, output, and
ledger material in the selected private problem directory. Run:

```bash
python scripts/formalization_handoff.py export <problem_dir> \
  --theorem-file <relative-file> \
  --proof-file <relative-file> \
  --ledger-file <relative-file> \
  --audit-file <relative-file> \
  --output-file <relative-file> \
  --external-results-policy sorry-free \
  --user-authorized --audit-no-known-gaps
```

Add repeated `--reference` and `--context` arguments only for relevant files
inside the selected problem. The command writes one directory under
`<problem_dir>/handoff/formalization/requests/`; it does not update research
state or create a repository-wide claim index.

Run `verify` before transfer. A changed source hash is source drift and stops
the handoff:

```bash
python scripts/formalization_handoff.py verify <problem_dir> <task_id>
```

## Stage to Lean explicitly

Stage only after export and verification, and only when the user has made the
separate Lean repository available in the current workspace and authorized the
cross-repository write:

```bash
python scripts/formalization_handoff.py stage <problem_dir> <task_id> \
  --lean-root /workspace/lean-repo
```

The destination is limited to
`<lean-root>/.archon/formalization_inbox/<task_id>`. Do not edit Lean source
from the research task. Continue formalization in a task rooted at the Lean
repository and follow its `AGENTS.md`.

## Prepare and import a Lean-side return

From the Lean task, prepare either a verification result or a source query:

```bash
python /workspace/research-repo/scripts/formalization_handoff.py prepare-result <task_id> \
  --lean-root /workspace/lean-repo \
  --kind verification_result \
  --report .archon/task_results/<report>.md \
  --lean-file MyProject/<file>.lean
```

For a semantic ambiguity or missing source, use `--kind source_query` and
provide `--source-query <file>`. Never resolve such a problem by changing the
theorem, adding assumptions, or hiding the desired conclusion in an interface.

Import from the research repository:

```bash
python scripts/formalization_handoff.py import <problem_dir> <task_id> \
  --lean-root /workspace/lean-repo
```

Import preserves raw evidence and generates a review checklist. It never
changes `research_state.md`, other detailed records, or statement labels.

## Audit the return

Treat a returned task as external Lean review evidence only after checking:

- exact source-to-Lean statement and proof-step correspondence;
- successful focused and project builds where applicable;
- all remaining `sorry` and declared axioms;
- hidden assumptions in structures, typeclasses, adapters, and theorem inputs;
- external-result citations and their exact hypotheses;
- final-package fields and dependency closure;
- unchanged packet and source hashes.

Record factual results in the generated review. Do not call a result fully
verified merely because it compiles, has no textual `sorry`, or reports only
standard kernel axioms.
