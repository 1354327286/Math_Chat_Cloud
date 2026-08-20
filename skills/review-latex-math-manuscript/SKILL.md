---
name: review-latex-math-manuscript
description: Clarify, compile, validate, and visually inspect a mathematical LaTeX manuscript after edits or before external review. Use for `.tex` build verification, warning and cross-reference audits, changed-page PDF inspection, structural renumbering checks, and exported-draft self-containment and human-readability audits. Resolve material ambiguity about the authoritative source, diagnosis-versus-edit scope, and deliverables before building or editing.
---

# Review A LaTeX Math Manuscript

Treat the reviewed `.tex` file as the source artifact.  Verify both the
logical structure exposed by LaTeX and the rendered PDF; a successful process
exit alone is not a completed review.

Read `docs/mathematical_artifact_standard.md` when the manuscript is an exported
proof/review draft or the user asks for a self-containment or readability audit.

## Establish The Review Scope

1. Identify the authoritative `.tex` source, its working directory, build
   directory, and expected PDF.
2. Determine whether the request is diagnosis-only or authorizes corrections,
   and whether mathematical correctness is in or out of scope.
3. Determine whether this is an existing manuscript or a new exported review
   draft, and the required deliverables: report, corrected source, PDF, and
   changed page renders.
4. Determine which source regions changed and which numbered statements,
   equations, citations, or section boundaries they can affect.
5. Preserve unrelated user edits and existing public DOI, arXiv, Stacks Tag,
   or publisher links.
6. If the user asks only for diagnosis, compile and inspect without editing.

Use recent discussion when it uniquely fixes these fields. If more than one
source, review purpose, edit boundary, or output is reasonably possible, ask a
focused question before compiling, generating files, or editing. Read-only
source discovery is allowed while waiting. Do not silently select the newest
`.tex` or expand diagnosis into edits. A complete
request that explicitly asks to proceed needs no redundant confirmation.

For a new paper-length export with no fixed style, use
`templates/math_article.tex`. Review and final delivery use the same source;
draft mode adds only a version/date and line numbers. Do not migrate an existing
manuscript or publisher template merely to standardize its appearance.

## Compile To A Stable PDF

In Work cloud, use the repository builder so temporary formats, repeated passes,
final-log checks, and page rendering are handled consistently:

```bash
python scripts/build_tex.py <source.tex> --strict
```

For an external manuscript whose build system cannot be represented by this
entry point, preserve and run its documented build command instead.

After the final pass, inspect the final log rather than the first-pass output.
Search at least for:

- `LaTeX Warning` and package warnings;
- undefined or multiply defined references and citations;
- `Overfull` and `Underfull` boxes;
- `pdfTeX warning`, missing destinations, and stale rerun requests.

Investigate every hit.  If an intentional warning remains, report it exactly;
do not describe the build as clean.  Do not run broad cleanup commands or
delete an existing build directory merely to obtain a fresh log.

## Audit Numbering And References

After moving, splitting, merging, or renumbering mathematical material:

1. Search the source for every affected `\label`, `\ref`, `\eqref`, citation,
   and old heading.
2. Confirm that no removed subsection, obsolete label, duplicated label, or
   forward dependency remains.
3. Inspect the final `.aux` or extracted PDF text when necessary to confirm
   the actual proposition, theorem, equation, and subsection numbers.
4. Check that prose references still name the correct mathematical result,
   not merely an automatically valid but semantically stale label.
5. Run `git diff --check` when the manuscript is in a Git worktree.

## Audit Human Readability

For an artifact intended to leave the current chat, audit the prose rather than
only the cross-reference graph:

1. Find each load-bearing use of a theorem, lemma, equation, local claim ID, or
   file locator.
2. Require the same local passage to name the result and state the exact
   consequence used. A bare `\ref`, internal claim name, or path-plus-label is
   a defect even when the link resolves.
3. Confirm that ordinary section, theorem, equation, page, and draft line
   locators are sufficient to identify requested corrections; do not add a
   second project-specific ID system.
4. Perform the cold-read audit using only the rendered artifact. Do not supply
   definitions or dependencies mentally from chat or repository memory.
5. Treat clickability as optional navigation. No sentence may require opening a
   second file merely to recover the assertion it uses.
6. Audit terminology independently of correctness. Flag a phrase that was
   coined by the draft but presented as standard, a project label disguised as
   mathematical vocabulary, or a one-use abstraction that makes the reader
   translate notation without simplifying the proof.
7. Read linearly for reader confusion: undefined abbreviations, symbol drift,
   ambiguous pronouns, forward dependencies, unmotivated lemmas, abrupt changes
   of abstraction, overloaded sentences, and paragraphs with no clear logical
   role. Revise every material finding before delivery.

## Inspect The Rendered Pages

Use `pdfinfo` and `pdftoppm` from the bundled workspace dependencies or the
system path.  Render all changed pages and the adjacent pages containing
section, subsection, theorem, proof, table, or bibliography transitions:

```bash
pdftoppm -f <first_page> -l <last_page> -png -r 130 \
  <manuscript.pdf> <tmp_prefix>
```

Locate affected pages with PDF text extraction when page numbers have shifted,
then inspect the PNGs visually.  Check for clipped text, overflow, bad page
breaks, isolated headings, split displays, crowded statements, broken links,
unreadable symbols, and inconsistent hierarchy.  For broad structural edits,
also inspect the title page, the final page, and every affected section
transition.  Recompile and rerender after any correction.

Keep render intermediates under `tmp/pdfs/` or another explicit temporary
directory.  Do not present scratch PNGs as final artifacts.

## Report Completion

State the authoritative source, output PDF, page count, final warning count,
pages visually inspected, and affected numbering. Report the cold-read and
statement-first audit separately when the artifact standard applies.
Distinguish a clean compile from a completed visual
review, a human-readability audit, and a mathematical correctness audit.
