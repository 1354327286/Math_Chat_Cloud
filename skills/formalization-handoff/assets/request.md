# Lean Formalization Request

- Task: `$task_id`
- Source problem: `$project_name`
- Created: `$created_at`
- External-results policy: `$external_results_policy`
- Explicit export authorization: yes
- Internal audit reports no known gap: yes

## Exact mathematical result

$theorem

## Requested Lean output

$output_contract

## Internal audit evidence

$audit

## Formalization constraints

- Preserve the exact theorem, hypotheses, scope, and definitions.
- Do not add assumptions or hide proof obligations in structures, typeclasses,
  adapters, or theorem inputs.
- Follow `lemma_ledger.md` and preserve source correspondence.
- If the packet is insufficient or inconsistent, use the source-recovery
  protocol and return a source query rather than guessing.
- A successful build is necessary evidence, not by itself acceptance.
