# Mathematical Discussion and Artifact Standard

This standard governs mathematical explanations in chat and every proof,
review draft, Pro handoff, or manuscript exported for a reader. A file path,
TeX label, theorem number, or hyperlink is a locator, not a substitute for the
mathematics it locates.

## State the mathematics before the locator

- At a load-bearing use of a named result, state the usable consequence and
  explain why its hypotheses apply. Add the ordinary theorem number, label,
  source location, or path only as secondary navigation.
- Short repetition may be compressed inside one immediately adjacent
  argument. Do not make the reader search across sections, files, or a long
  chat merely to recover the assertion being used.
- For an external result, state the exact consequence, match its hypotheses to
  the present objects, and give a precise source locator.
- Use ordinary descriptive theorem names and normal LaTeX labels. Do not add a
  second project-specific ID system to a paper.

## Eligibility gate before drafting

A reviewable proof article is written only after the requested mathematical
result is closed. Before drafting, verify all of the following:

1. The exact theorem, assumptions, quantifiers, conventions, and intended
   conclusion are fixed.
2. Every local lemma used in the proof has a closed proof.
3. Every material external input has a verified statement, source,
   hypotheses, and applicability check.
4. Every construction, comparison, transition, and limiting or descent step
   needed for the conclusion is justified.
5. No material step remains plausible, conditional on an unproved local
   claim, citation-blocked, circular, or otherwise unresolved.

If this gate fails, return the argument to the research workflow. Do not write
a paper with gap notices, issue IDs, dependency-audit sections, or a claim of
closure. Explicit hypotheses in the theorem statement are not gaps, but an
unproved local lemma may not be promoted to a hypothesis merely to pass the
gate.

## Acceptance contract for an exported article

### Mathematical self-containment

- Define every nonstandard object and symbol before use.
- State every local lemma before using it and include its proof in the article
  unless an exact verified citation legitimately supplies it.
- Put dependencies in logical order and make every map, base change,
  completion, comparison, and change of ambient category explicit when it
  carries mathematical content.
- The article may not rely on project memory, chat history, hidden
  instructions, or another local file for a mathematical assertion.

### Human readability

- Begin with a compact abstract, an exact main theorem, and a proof roadmap.
- Use connected mathematical prose rather than a research-state dump.
- Give important statements descriptive names and ordinary theorem numbers.
- Explain why each lemma is introduced and how it advances the main theorem.
- A reference should name the result and state the consequence used; a bare
  `\ref{...}`, internal claim name, or path fails this gate even if clickable.
- A reviewer should be able to locate a requested correction by section,
  theorem or equation number, PDF page or draft line number, and a quoted
  phrase. No artificial revision-ID system is required.

### Terminology and reader-confusion audit

Before delivery, read the article as a domain reader who has not seen the
repository or chat. This is not a spelling pass and cannot be replaced by
compilation.

- Classify each nonroutine technical expression as established terminology,
  an explicitly defined new term, or drafting shorthand that must be removed.
  Do not invent a noun phrase merely to name a proof step or a one-use
  construction. A genuinely useful new term must be announced, completely
  defined, motivated, and used consistently.
- Remove private project vocabulary, agent plans, file headings, confidence
  bookkeeping, and drafting commentary from the article.
- Define every abbreviation and symbol before first use. Prevent symbol drift,
  silent variance changes, and unannounced changes of ambient category.
- Resolve ambiguous pronouns and compressed references such as “this”, “the
  above map”, “similarly”, or “the same argument”.
- Check each paragraph for its mathematical purpose, input, conclusion, and
  transition to the next step. Motivate new lemmas and changes of abstraction.
- Put definitions and statements before their first logical use. Eliminate
  forward dependencies disguised as previews.
- Rewrite any sentence whose quantifiers, negations, hypotheses, or relative
  clauses admit two plausible mathematical readings.

The article passes only when there is no material undefined or misleading
term, ambiguous reference, unexplained notation, unmotivated structural jump,
or sentence with two plausible mathematical readings. Fix defects before
delivery instead of asking the user to discover them through repeated review.

## Standard article and cloud delivery

When no publisher or user-supplied house style is fixed, use
`templates/math_article.tex`. The same source serves review and final delivery:
draft mode adds only a version/date and line numbers; final mode removes them.
Workflow status, proof-search history, audit logs, and unresolved issues stay
outside the reader-facing paper.

The standard Work-cloud deliverables are:

1. the authoritative `.tex` source;
2. a compiled PDF;
3. visual inspection of every changed page and relevant page transition;
4. a concise delivery report giving the source, PDF, page count, build
   warnings, pages inspected, and the mathematical and editorial audit result.

Do not maintain a generated Markdown copy of the article. Do not migrate an
existing manuscript to the repository template without authorization.

## Cold-read audit before delivery

Audit using only the exported article, with repository files and chat history
closed. Delivery fails unless a capable reader can answer:

1. What is the exact theorem and every assumption?
2. What does each material intermediate result assert?
3. Why does every external theorem apply?
4. What is the logical dependency order of the proof?
5. Can every material claim be traced to a proof, theorem hypothesis, or exact
   verified citation?
6. Does any sentence require another file or chat context for its meaning?
7. Does any term look standard although it was invented only for the draft?
8. Is any paragraph, transition, pronoun, notation choice, or long sentence
   unclear on a first linear reading?

Revise until questions 6--8 have negative answers. Compilation and valid
cross-references do not replace this semantic audit.
