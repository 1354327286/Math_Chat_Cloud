---
name: check-referenced-statements
description: Check external mathematical statements cited by a proof against their primary sources, including exact hypotheses, definitions, versions, and downstream use. Use when a proof relies on papers, books, or named theorems.
---

# Check Referenced Statements

Audit both the cited result and the way the current proof applies it.

## Procedure

1. For each citation, record its use location, the statement attributed to the source, and the conclusion drawn from it.
2. Search existing project memory and local references first. If the result or exact context is missing, use external theorem search or web search.
3. Prefer primary and authoritative sources. Record the exact paper or book version, theorem number, page, and URL or identifier when available.
4. For substantive reading of an arXiv paper, follow the repository's mandatory source workflow: acquire the version-matched source and PDF, search the main TeX file, and verify the final statement against the PDF or published version.
5. Expand the source's definitions, notation, ambient category, and conventions. Compare exact formulas and quantifiers, not just similar terminology.
6. Check every hypothesis against the current objects.
7. Check the specialization and every downstream deduction made from the cited result.
8. Classify each citation use as:
   - `verified and applicable`;
   - `verified but application needs repair`;
   - `partially verified`;
   - `not found or needs verification`;
   - `incorrectly cited or inapplicable`.
9. Treat a source mismatch, missing hypothesis, or invalid downstream implication as a mathematical issue even when the cited theorem itself is genuine.

## Output And Persistence

Produce a human-readable citation audit containing:

- proof location;
- source and exact version;
- source statement and hypotheses;
- definition comparison;
- applicability analysis;
- status;
- issue and repair needed.

Append reusable source findings to `<problem_dir>/memory/search_results.md`. Put proof-specific citation findings in the current daily note or the proof's review file under `notes/`. Update `refs/catalog.json` when references are downloaded or organized, following `docs/reference_workflow.md`.
