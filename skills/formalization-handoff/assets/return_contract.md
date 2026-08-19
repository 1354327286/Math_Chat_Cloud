# Lean Return Contract

Return either `verification_result` or `source_query` for task `$task_id`.

For a verification result, report exact commands and outcomes, Lean file paths,
statement correspondence, remaining `sorry` or axioms, documented external
results, hidden interfaces, final-package dependency closure, and blockers.

For a source query, identify the exact affected claim, inspected evidence,
incident type, why work cannot proceed without a semantic guess, and the exact
clarification or source correction required.

Use `formalization_handoff.py prepare-result` to build a hashed outbox. Do not
edit the staged request packet.
