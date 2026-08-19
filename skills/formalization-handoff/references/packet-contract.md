# Formalization packet contract

## Contents

1. Export eligibility
2. Request packet
3. Source recovery
4. Return packet
5. Acceptance boundary

## Export eligibility

An export represents an exact proof selected by the user, not a request to find
or repair a proof. Require:

- an explicit user request to export;
- an exact theorem with assumptions;
- an exact requested Lean result;
- a declared policy of `sorry-free` or `documented-external-results`;
- an internal audit with no known mathematical gap;
- a dependency-complete lemma ledger;
- precise source files for the proof and any external references.

If the user requests export but the result is ambiguous, ask for the missing
result, scope, assumptions, or external-results policy. Make zero export writes
until the answer is sufficient.

## Request packet

Each request is a directory containing:

| File | Role |
| --- | --- |
| `request.md` | Exact theorem, output contract, eligibility evidence, and policy |
| `context.md` | Human-readable snapshot of the relevant research state and proof sources |
| `lemma_ledger.md` | Dependency-ordered Lean-ready obligations with source correspondence |
| `source_map.md` | Human-readable paths, roles, sizes, and SHA-256 values |
| `return_contract.md` | Required Lean-side result and diagnostic evidence |
| `result_report.template.md` | Result report scaffold |
| `source_query.template.md` | Source-recovery question scaffold |
| `manifest.json` | Machine-readable schema, source hashes, and packet hashes |
| `manifest.sha256` | Accidental-change receipt for the request manifest |

Markdown is authoritative for mathematical meaning. JSON is only a validation
surface and must not become a parallel claim-status database.

SHA-256 receipts detect accidental change and inconsistent copies; they are not
cryptographic signatures and do not establish authorship or trust.

The packet is immutable after export. Re-export a new task instead of editing a
staged packet. A mismatch between the live source and `source_map.md` is source
drift; do not mix the old packet with new source state.

## Source recovery

The Lean task must inspect the packet before reading the source repository. If
the packet is incomplete, inconsistent, or appears to require a semantic
change, return to Plan Mode and use this read-only order:

1. The source repository's `AGENTS.md`.
2. The selected problem's `research_state.md`.
3. Files precisely named in `source_map.md`.
4. `goal.md` and `subgoal.md`.
5. Only when still necessary, `progress.md`, the latest dated note, and relevant
   files under `memory/`.

Do not scan other registered problems. Do not edit the source repository from
the Lean task.

Classify the incident in the return report as one of:

- `transfer_defect`: transcription, truncation, symbol, path, or ordering error;
- `mathematical_gap`: a false step, missing lemma, missing hypothesis, or
  circular dependency in the source proof;
- `lean_encoding_gap`: the mathematics is plausible but the chosen Lean
  definitions, interfaces, or Mathlib alignment are inadequate;
- `environment_gap`: toolchain, dependency, import, or build mismatch;
- `unresolved`: the available evidence does not distinguish the cases.

These are handoff incident types, not research claim-status labels.

A mechanical error may be corrected in a Lean-side working copy only when the
exact source makes the correction unique and no mathematical meaning changes.
Record the correction. Return a `source_query` instead of proceeding whenever a
fix would add or remove an assumption, alter the conclusion, change scope,
select among competing interpretations, or weaken the requested theorem.

## Return packet

A return lives under
`.archon/formalization_outbox/<task_id>/` and contains a manifest plus copied
evidence. Its `result_manifest.sha256` checks the result manifest for accidental
change. Use `prepare-result` so paths and hashes are deterministic.

For `verification_result`, include:

- a completed result report;
- every relevant changed or created `.lean` file;
- exact verification commands and outcomes;
- remaining `sorry`, axioms, external results, and blockers;
- source-to-declaration and lemma-to-declaration correspondence;
- hidden-interface and final-package-field audit findings.

For `source_query`, include a precise affected claim, evidence inspected,
failure classification, reason work cannot safely proceed, and the exact
clarification or source correction required. Lean files are optional.

## Acceptance boundary

Import is archival, not acceptance. The research side must audit the raw return
before recording external Lean review evidence. Compilation alone does not show
that the formalized theorem is the requested theorem. Absence of `sorry` or new
axiom declarations does not show that project-specific assumptions were not
moved into records, typeclasses, adapters, or theorem hypotheses.

Only report completed external Lean verification when the requested statement,
proof correspondence, build results, dependency closure, external-result
policy, and hidden-interface audit all pass. Otherwise record the exact weaker
fact, such as compilation with documented external results or an unresolved
formalization blocker.
