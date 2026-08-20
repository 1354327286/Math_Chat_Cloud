---
name: write-self-contained-math-proof
description: Clarify and turn a mathematically closed result from the selected problem's research state into a self-contained, human-readable proof for human or external-LLM review. Use when the user asks Codex to write, present, export, or polish a standalone proof or review article based on current project progress. Resolve material ambiguity before drafting, require every dependency to be closed, state every load-bearing consequence locally, and use the repository's standard article template for a new paper-length export unless another house style is fixed.
---

# Write A Self-Contained Math Proof

Write a proof document that stands on its own. Treat project memory as source material, not as the structure or voice of the final exposition.

Read and enforce `docs/mathematical_artifact_standard.md`. A correct hyperlink,
file locator, or statement label never compensates for an unstated mathematical
assertion.

## Resolve the standalone deliverable

Before drafting or creating a proof file, identify:

- the selected problem and exact theorem, proposition, or lemma;
- every assumption, convention, and fixed parameter;
- the intended reader and assumed background;
- the requested form, such as chat proof, Markdown, LaTeX, article section, or
  external-review packet;
- whether a paper-length export should use the repository template or an
  existing user/publisher house style, and whether draft line numbers should
  remain enabled for review;
- the destination and any length, style, or citation requirements.

Use recent discussion when it fixes these fields uniquely. If a material field
has more than one reasonable interpretation, ask the user for the missing
specification and make no standalone-proof write while waiting. Do not select a
weaker proved statement, change the audience, or choose an output format merely
because it is easier to deliver. A complete request that explicitly asks to
proceed needs no redundant confirmation.

This clarification gate is distinct from the mathematical eligibility gate.
Once the requested deliverable is clear, an unresolved proof dependency is a
mathematical failure of eligibility, not a reason to ask the user to choose a
different theorem.

## Enforce The Eligibility Gate

1. Use the exact theorem, proposition, or lemma fixed by the resolved deliverable. It may be the main goal or a genuinely proved intermediate result.
2. Fix all assumptions, conventions, and the intended level of background.
3. Trace the complete proof dependency chain before drafting prose.
4. Generate a review document only when all of the following hold:
   - every local lemma used in the argument has a closed proof;
   - every external result used materially has a verified statement, source, hypotheses, and applicability check;
   - every construction, comparison, and transition needed for the conclusion has been justified;
   - no material step remains `plausible`, `needs verification`, conditional on an unproved local claim, or otherwise unresolved.
5. Treat hypotheses explicitly included in the theorem statement as hypotheses, not gaps. Never promote an unproved local lemma to an assumption merely to pass this gate.
6. If the gate fails, do not write a proof article with a gap notice or review appendix. Return the argument to the research workflow and state briefly that no closed proof of the requested result is ready for exposition.

## Gather The Mathematics

1. Start with the selected problem's `research_state.md` and today's dated note,
   or the most recent dated note when today's file is absent. Then open only the
   linked proof, memory, and reference files needed to verify the target's full
   dependency chain.
2. Extract the final logical dependency chain rather than reproducing the chronology of discovery.
3. Use only established ingredients that passed the eligibility gate.
4. Recover the exact statement and hypotheses of every material external result.
5. Omit failed attempts, abandoned plans, confidence labels, and research-process commentary from the proof document.

## Write The Document

Use this order unless the mathematics clearly calls for a small variation:

1. **Title**: Name the mathematical result, not the project or workflow.
2. **Statement**: Give the exact theorem with all hypotheses and quantifiers.
3. **Setup and notation**: Define nonstandard objects, conventions, and symbols before they carry argumentative weight.
4. **Proof roadmap**: Explain the main mechanism and dependency chain in one compact paragraph.
5. **Lemmas and propositions**: State each intermediate result before proving or citing it. Give descriptive names and ordinary theorem numbers.
6. **Main proof**: Connect the lemmas in logical order and explicitly close the stated conclusion.
7. **References**: List only sources actually used, with theorem numbers or locations when available.

## Enforce Type And Interface Discipline

- State complete definitions rather than names or slogans.  When proving
  membership in a category, verify every defining condition instead of only
  the most visible one.
- Keep mathematical types distinct: modules, sheaves, degree-zero complexes,
  derived objects, crystals, and their evaluations are not interchangeable.
  If $M$ is a module and $M[0]$ is the associated complex, say so explicitly.
- Define the source, target, and ambient category of every pullback,
  restriction, completion, base-change map, comparison map, and Frobenius
  map before using it.  Do not reuse one symbol for different operations in
  different categories without an explicit comparison.
- Work directly in the manuscript's setting when an abstraction is used only
  once and would force the reader to translate all notation back.  Abstract
  first only when the result is genuinely reusable or materially simplifies
  the proof.
- Separate logically different constructions.  For example, construct and
  verify underlying-object descent, cartesianness, Frobenius descent, and
  analytic or generic restriction as distinct steps rather than saying that
  all the data descend at once.
- Name the final constructed object and identify its category.  Give enough
  local evaluations, transition maps, comparison data, and Frobenius data
  that the stated object can be recovered from the proof.
- Qualify every uniqueness assertion by the data it fixes.  State whether the
  unique isomorphism must preserve a chosen generic identification, local
  identifications, pointing, or natural transformation; do not imply
  uniqueness among arbitrary extensions unless that stronger statement is
  proved.
- Match quantifiers to the covers and families actually used.  If the proof
  uses a finite atlas, index it in the statement, say which constants are
  uniform, and explain where the covers at later stages come from.

## Control Proof Architecture

- Put every lemma or construction before its first use.  If a later result
  constructs an object assumed by an earlier result, split and reorder the
  results rather than leaving a forward dependency.
- Keep proof paragraphs for the mathematical argument.  Put explanations of
  purpose, later use, and the overall route immediately before or after the
  proof, not inside its final deductions.
- Explain positively what each step accomplishes.  Avoid defensive prose
  whose only function is to list things not claimed or not used, except when
  a negative qualification prevents a genuine mathematical misreading.
- Move general auxiliary algebra or geometry into preliminaries only after
  restating it independently of the main proof's temporary notation.  Let the
  main proof cite the result and explain its role.
- Make subsection boundaries correspond to mathematical interfaces rather
  than the chronology of drafting.  Number substantial reusable
  constructions, merge adjacent thin subsections, and retain a one-result
  subsection only when the whole subsection sets up and proves that central
  interface.
- Replace vague references and workflow shorthand such as `the common
  object`, `the treating step`, `the formal stage`, or `the preceding
  construction` by defined objects or precise numbered references.  Do not
  invent terminology that can be confused with an established technical
  term.

## Write For A Reader

- Assume the reader knows the mathematical field but has no access to this repository, its filenames, or earlier chat.
- Do not write phrases such as `the memory shows`, `as recorded in the state file`, `our current subgoal`, or `as discussed earlier`.
- Define every project-specific term and symbol in the document. Restate and prove any local lemma needed by the argument.
- Explain why each lemma is introduced and how it advances the theorem.
- When citing a result from another specialty, give an applicability bridge:
  state the exact consequence used, match its hypotheses to the present
  objects, and say what it produces here.  If its terminology or local
  geometry is opaque, include a formula or small model that makes the
  operation understandable, but do not reproduce an unrelated cited proof.
- Use paragraphs with one mathematical purpose. Prefer connected prose over a dump of bullets or status records.
- Use displayed equations for structural identities and align multi-step calculations when alignment clarifies the argument.
- Refer to labeled statements instead of vague phrases such as `the previous result` when more than one result could be meant.
- Treat ordinary theorem numbers and TeX labels as secondary locators. On every
  load-bearing use, name the result and state the exact consequence being
  applied in the same paragraph. Do not write a proof step whose mathematical
  content can be recovered only by opening a file, following a link, or looking
  up an internal claim name.
- Do not insert research confidence labels into the proof prose.
- Avoid `clearly`, `obviously`, and `standard` when they conceal a nontrivial inference. Give the argument or an exact citation.
- Do not over-explain routine algebra that the intended reader can reconstruct, but never omit a step on which validity depends.

## Audit Before Delivery

Perform a final pass using only the drafted document, without mentally supplying repository context:

1. Can a reader state the exact target and every assumption?
2. Is every symbol defined before use?
3. Can each material claim be traced to a proof, a stated theorem hypothesis, or an exact verified citation?
4. Are definition changes, base changes, limits, completions, descent, and finiteness steps justified where relevant?
5. Does the roadmap match the proof actually written?
6. Does the final paragraph prove exactly the theorem stated at the beginning?
7. Could another capable LLM review the document without receiving any local project file?
8. Is the proof free of unresolved dependencies and hidden appeals to project memory?
9. Does every load-bearing theorem reference have its usable statement or exact
   consequence in the same local passage?
10. Can a revision be located by section, theorem or equation number, PDF page
    or draft line number, and a quoted phrase?

Then perform the terminology and reader-confusion audit from
`docs/mathematical_artifact_standard.md`. In particular, identify every term not
obviously standard in the field and either verify its established use, define it
as genuinely new terminology, or replace it with a direct mathematical
description. Read the draft linearly as a first-time reader and revise ambiguous
pronouns, unexplained notation, unmotivated lemmas, abrupt abstraction changes,
overloaded sentences, and paragraphs whose logical role is not apparent. Do not
delegate this quality control to the user through repeated post-delivery fixes.

If any audit item fails mathematically, do not deliver the document with a caveat. Return to the research workflow until the proof closes. Otherwise revise the exposition until the readability checks pass.

## Delivery And Persistence

Return the proof itself, not a summary of how it was assembled. For persistent project work or a long proof, save it under `<problem_dir>/notes/` with a descriptive dated filename unless the user requests chat-only output or another location.

For a new paper-length proof or exported review draft without a fixed external
style, copy `templates/math_article.tex`. The review and final versions use the
same mathematical source: draft mode adds only the version/date and line
numbers, and final mode disables them. Do not expose workflow status, issue
tracking, dependency audits, or proof-search history in the paper. Do not
migrate an existing manuscript or publisher submission to this template without
authorization.

In Work cloud, the standard export consists of the authoritative `.tex` and a
compiled and visually inspected PDF. Build with
`python scripts/build_tex.py <source.tex> --strict`, inspect the rendered pages,
and report the final warnings and pages checked. Do not generate or maintain a
Markdown copy of the manuscript.

Do not update research memory merely because existing mathematics was rewritten. If the eligibility audit uncovers a new mathematical issue, record it in the appropriate detailed memory file and do not produce the review proof yet.
