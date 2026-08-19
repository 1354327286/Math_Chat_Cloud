# Imported Lean Review

- Task: `$task_id`
- Source problem: `$project_name`
- Imported: `$imported_at`
- Return kind: `$result_kind`
- Live source at import: `$source_status`
- Request manifest SHA-256: `$request_manifest_sha256`
- Result manifest SHA-256: `$result_manifest_sha256`
- Status: needs semantic audit

## Raw evidence

The unmodified Lean-side return is under `raw/`. Do not edit it while auditing.

## Audit checklist

- [ ] Exact requested theorem and hypotheses match the Lean declaration.
- [ ] Every lemma-ledger item maps to verified Lean code or an explicit blocker.
- [ ] Focused checks and `lake build` were run where applicable.
- [ ] Remaining `sorry`, axioms, and external results are fully enumerated.
- [ ] External results match their cited hypotheses and conclusions.
- [ ] No mathematical obligation is hidden in a structure, typeclass, adapter,
      theorem hypothesis, or preconstructed data package.
- [ ] Final-package fields trace to proved constructors or declared boundaries.
- [ ] Source and packet hashes are unchanged.
- [ ] Any source query has been resolved in the source project.

## Audited conclusion

TODO. Record the exact factual level reached. Import alone does not update
research state or establish external Lean verification.
