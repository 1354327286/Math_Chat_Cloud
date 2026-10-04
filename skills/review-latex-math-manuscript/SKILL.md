---
name: review-latex-math-manuscript
description: Clarify, compile, validate, and visually inspect a mathematical LaTeX manuscript after edits or before external review. Use for `.tex` build verification, warning and cross-reference audits, changed-page PDF inspection, structural renumbering checks, and an explicitly requested generated `.reader.md` companion. Resolve material ambiguity about the authoritative source, diagnosis-versus-edit scope, and deliverables before building or editing.
---

# Review A LaTeX Math Manuscript

Treat the reviewed `.tex` file as the source artifact.  Verify both the
logical structure exposed by LaTeX and the rendered PDF; a successful process
exit alone is not a completed review.

## Establish The Review Scope

1. Identify the authoritative `.tex` source, its working directory, build
   directory, and expected PDF.
2. Determine whether the request is diagnosis-only or authorizes corrections,
   whether mathematical correctness is in or out of scope, and the agreed target
   reader and background. Reuse resolved context rather than changing audiences.
3. Determine the required deliverables: report, corrected source, PDF, changed
   page renders, and an explicitly requested `.reader.md` companion.
4. Determine which source regions changed and which numbered statements,
   equations, citations, or section boundaries they can affect.
5. Preserve unrelated user edits and existing public DOI, arXiv, Stacks Tag,
   or publisher links.
6. If the user asks only for diagnosis, compile and inspect without editing.

Use recent discussion when it uniquely fixes these fields. If more than one
source, review purpose, edit boundary, or output is reasonably possible, ask a
focused question before compiling, generating files, or editing. Read-only
source discovery is allowed while waiting. Do not silently select the newest
`.tex`, expand diagnosis into edits, or generate a reader companion. A complete
request that explicitly asks to proceed needs no redundant confirmation.

## Compile To A Stable PDF

Run `latexmk` from the source directory so bibliography and repeated LaTeX
passes are handled automatically.  Prefer a dedicated build directory:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -outdir=<build_dir> <source.tex>
```

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
2. Confirm that no removed subsection, obsolete label, duplicated label,
   circular reasoning, undefined object, or unclosed proof dependency remains.
   Legitimate conceptual previews, intelligible theorem announcements, and
   explicit references to complete later proofs are allowed. A LaTeX reference
   resolving successfully does not by itself close a mathematical dependency.
3. Inspect the final `.aux` or extracted PDF text when necessary to confirm
   the actual proposition, theorem, equation, and subsection numbers.
4. Check that prose references still name the correct mathematical result,
   not merely an automatically valid but semantically stale label.
5. Run `git diff --check` when the manuscript is in a Git worktree.

## Check Exposition And Mathematical Changes

Review readability for the agreed target reader, not an automatically broader
or more specialized audience. Inspect changed passages and affected uses for a
local correction; review the whole article when that is the requested scope.
Reuse existing manuscript plans, ledgers and still-valid audit evidence. Do not
create management files or inventory the whole project for a routine edit.

Check that shared terms are introduced early enough, local definitions remain
near their use, and each formal theorem follows the definitions needed to
understand it. A conceptual preview before those definitions must be honest
about the result's scope. Explanatory proof prose and appendices containing
technical proofs are legitimate when they help the reader. For appendix proofs,
keep the exact statements, role and dependency links visible in the main text
and require complete proofs at the referenced locations.

Do not turn a compile or visual review into a claim of mathematical correctness.
If a proposed correction changes hypotheses, quantifiers, a construction, a
load-bearing lemma, an external input or the proof argument substantively,
follow [the writing skill's mathematical-change review boundary](../write-self-contained-math-proof/SKILL.md#recheck-substantive-mathematical-changes).
Such edits need source reconciliation and independent mathematical review of
the affected argument and downstream uses before delivery as closed. Self-review
is not independent review. If mathematical edits are outside the authorized
scope, report the issue and ask before making them; if independent review is
unavailable, report the blocker rather than implying the compile certified it.

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

## Maintain A Reader Companion Only On Request

When the repository provides `scripts/generate_tex_reader.py` and the user
explicitly asks for a local reading copy:

- keep the `.tex` manuscript as the sole editable source of truth;
- generate the sibling `.reader.md`; never hand-edit it;
- regenerate it after source changes and require the hash check to pass.

```bash
python scripts/generate_tex_reader.py <problem_dir>/notes/proof.tex
python scripts/generate_tex_reader.py <problem_dir>/notes/proof.tex --check
```

Do not create a reader companion merely because a TeX file exists.

## Manuscript Finalization

When the authorized task includes manuscript finalization, perform the project
email-index and attribution checks in [the email workflow](../../docs/email_workflow.md).
These obligations apply at manuscript finalization, not to every short proof,
compile check or routine local edit. They do not authorize sending email.

## Report Completion

State the authoritative source, output PDF, page count, final warning count,
pages visually inspected, affected numbering, and reader status when
applicable.  Distinguish a clean compile from a completed visual review and
from a mathematical correctness audit. Identify the actual scope and revision
of any self-review or independent mathematical review; do not conflate them.
