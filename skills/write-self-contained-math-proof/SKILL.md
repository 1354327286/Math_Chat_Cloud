---
name: write-self-contained-math-proof
description: Write or revise standalone mathematical proofs and assemble scattered results into a review manuscript. Use a lightweight path for short proofs and a manuscript-scoped result ledger, plan, skeleton and review cycle for long articles. Resolve scope before writing; deliver a proof manuscript only after its mathematical dependencies are closed.
---

# Write A Self-Contained Math Proof

Write a proof document that stands on its own. Treat project memory as source material, not as the structure or voice of the final exposition.

## Resolve the standalone deliverable

Before drafting or creating a proof file, identify:

- the selected problem and exact theorem, proposition, or lemma;
- every assumption, convention, and fixed parameter;
- the intended reader and assumed background;
- the requested form, such as chat proof, Markdown, LaTeX, article section, or
  external-review packet;
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

## Choose The Writing Path

- For a short standalone proof, use the eligibility check and exposition rules
  below directly. Do not create manuscript-management files for a small task.
- For assembling several results into an article or substantially reorganizing
  a long manuscript, read [the manuscript assembly workflow](references/manuscript-assembly.md).
  It uses five stages: inventory, reader route, statement skeleton, section
  writing/review, and global coordination. Keep a manuscript-scoped ledger
  and plan proportionate to the important inputs and decisions.
- For an existing manuscript's local correction or style-only revision, preserve
  its scope and structure. Reuse any existing ledger/plan; do not require a
  retrospective inventory of the whole project for an isolated edit. Do not
  create a ledger or plan for every routine edit. Reuse still-valid audit evidence
  and recheck the changed passage and its affected uses. Substantive mathematical
  edits require the affected independent mathematical review described below.

An authorized full writing task includes routine stage checks and repairs.
Do not ask for approval at each stage unless the user requested checkpoints.
Material ambiguity or a change to the agreed theorem, scope or destination
still requires resolution under the deliverable gate.

## Enforce The Eligibility Gate

1. Use the exact theorem, proposition, or lemma fixed by the resolved deliverable. It may be the main goal or a genuinely proved intermediate result.
2. Fix all assumptions, conventions, and the intended level of background.
3. Trace the complete proof dependency chain before drafting proof prose. Reuse valid proof and audit evidence; a ledger entry or status label alone is not evidence.
4. Generate a review document only when all of the following hold:
   - every local lemma used in the argument has a closed proof;
   - every external result used materially has a verified statement, source, hypotheses, and applicability check;
   - every construction, comparison, and transition needed for the conclusion has been justified;
   - no material step remains `plausible`, `needs verification`, conditional on an unproved local claim, or otherwise unresolved.
5. Treat hypotheses explicitly included in the theorem statement as hypotheses, not gaps. Never promote an unproved local lemma to an assumption merely to pass this gate.
6. If the gate fails, do not write a proof article with a gap notice or review appendix. Return the argument to the research workflow and state briefly that no closed proof of the requested result is ready for exposition.

After the deliverable is resolved, an internal inventory, plan or explicitly
marked incomplete statement skeleton may expose unresolved dependencies before
this gate passes. These are planning artifacts, not a review proof. Do not fill
an unresolved step with speculative prose or deliver the skeleton as a completed
article. If the user requested only a plan, deliver the plan as such. Creating a
ledger does not itself audit or certify any entry.

## Gather The Mathematics

1. Follow AGENTS.md's progressive retrieval order. Use the current state to locate the target, then retrieve complete relevant proof/source sections; do not load all progress and memory logs. In article assembly, record the selected statements and proof sources in the paper ledger.
2. Extract the final logical dependency chain rather than reproducing the chronology of discovery.
3. Use only ingredients that passed the eligibility gate in proof prose; keep unresolved inventory entries explicitly blocked or excluded.
4. Recover the exact statement and hypotheses of every material external result.
5. Omit failed attempts, abandoned plans, confidence labels, and research-process commentary from the proof document.

## Write The Document

If the user identifies a successful earlier manuscript, read it and use its
expository architecture and proof rhythm as the primary model, not just its
section titles. Map each old technical input to the currently audited input;
preserve the mathematical progression without importing withdrawn arguments
or hypotheses. Explain any departure required by the new dependency chain.

Otherwise use [the candidate proof structure](assets/review-proof-template.md)
as a starting point, not a fixed table of contents. For long articles, use the
five-stage assembly workflow; for short proofs, omit unnecessary article
apparatus. Finalize the abstract and introduction after the body stabilizes.

Choose a route that lets the agreed reader understand the problem, the main
difficulty, and the proof mechanism. A construction-led, example-led, or
successive-reduction exposition may work better than preliminaries followed by
interfaces and a final proof. Preserve the exact theorem and dependency closure
in every architecture.

- Use a mathematical title; include an abstract and a roadmap when useful for
  the requested form. An honest conceptual preview may explain the result
  before technical setup without claiming a stronger theorem.
- Place the formal theorem after the definitions needed to understand it. If
  those definitions are short, the theorem can be in the introduction;
  otherwise give a conceptual preview there and place its precise statement
  later. Do not use undefined objects to force an early formal statement.
- Introduce shared conventions and heavily reused terminology early. Put local
  definitions near their first substantive use; do not front-load every term.
- State intermediate results with their hypotheses and expose the dependencies
  at each use. Explicitly close the main theorem at the point the argument does
  so; a separate final-proof section is optional.
- Cite only sources actually used, with exact theorem, section, chapter, page,
  or equation locators when available.
- Long technical proofs, including load-bearing proofs, may go in an appendix
  when their exact statements, role, and dependency links stay visible in the
  main text and the complete appendix proof is supplied. An appendix cannot
  hide an unresolved step or leave the main route unintelligible.

## Enforce Type And Interface Discipline

- State complete definitions rather than names or slogans.  When proving
  membership in a category, verify every defining condition instead of only
  the most visible one.
- Keep mathematical types distinct: modules, sheaves, degree-zero complexes,
  derived objects, and objects with additional structure are not interchangeable.
  If $M$ is a module and $M[0]$ is the associated complex, say so explicitly.
- Define the source, target, and ambient category of every pullback,
  restriction, completion, base-change map, comparison map, and structure
  map before using it.  Do not reuse one symbol for different operations in
  different categories without an explicit comparison.
- Work directly in the manuscript's setting when an abstraction is used only
  once and would force the reader to translate all notation back.  Abstract
  first only when the result is genuinely reusable or materially simplifies
  the proof.
- Separate logically different constructions. Verify the underlying object,
  compatibility of its transition maps, additional structures, and specified
  comparison isomorphisms as distinct steps rather than saying that all
  requirements follow at once.
- Name the final constructed object and identify its category.  Give enough
  local descriptions, transition maps, comparison data, and additional structure
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

- Distinguish the internal dependency inventory from the article's contents.
  The inventory checks that every input and proof obligation is accounted for;
  the contents explain the reader's route through the problem. Do not turn
  lists of techniques or one heading per dependency into section titles.
  Name sections by their mathematical question, construction or output, and
  explain their purpose and handoff in the opening prose. Keep technical
  names when they help the intended reader; never promise a stronger output
  than the section proves. Check the contents and roadmap as a reader before
  checking them against the dependency inventory.
- Prefer dependency order for the technical development. Introductory theorem
  announcements and explicit references to later proofs are legitimate when
  their statements and notation are intelligible and dependencies are acyclic.
  If a later construction is needed to define an earlier object, move or split
  the setup so the earlier statement is meaningful.
- Explanatory prose belongs inside proofs when it clarifies the mechanism,
  purpose of a construction, or a difficult transition. Integrate it with the
  deductions; do not replace a load-bearing argument with a roadmap or slogan.
- Explain positively what each step accomplishes.  Avoid defensive prose
  whose only function is to list things not claimed or not used, except when
  a negative qualification prevents a genuine mathematical misreading.
- Use preliminaries only when they help the reader. Shared background or
  reusable auxiliary results may belong there, including original proofs.
  Restate such results independently of temporary proof notation. Keep local
  setup near its use and place material by its explanatory and dependency role,
  not by whether it is original or quoted.
- Make subsection boundaries correspond to mathematical interfaces rather
  than the chronology of drafting.  Number substantial reusable
  constructions, merge adjacent thin subsections, and retain a one-result
  subsection only when the whole subsection sets up and proves that central
  interface.
- Replace vague references and workflow shorthand such as `the common
  object`, `the treating step`, `the later step`, or `the preceding
  construction` by defined objects or precise numbered references.  Do not
  invent terminology that can be confused with an established technical
  term.

## Write For A Reader

- Write for the agreed target reader and assumed background, without access to this repository, its filenames, or earlier chat. Do not silently substitute an adjacent-specialty audience.
- Do not write phrases such as `the memory shows`, `as recorded in the state file`, `our current subgoal`, or `as discussed earlier`.
- Define every project-specific term and symbol in the document. Restate and prove any original local lemma needed by the argument. Cite borrowed definitions at their introduction, even when reproducing their full content; for verified external results, give the exact used statement and applicability bridge rather than an unnecessary replacement proof.
- Explain why each lemma is introduced and how it advances the theorem.
- When citing a result from another specialty, give an applicability bridge:
  state the exact consequence used, match its hypotheses to the present
  objects, and say what it produces here.  If its terminology or local
  geometry is opaque, include a formula or small model that makes the
  operation understandable, but do not reproduce an unrelated cited proof.
- Use paragraphs with one mathematical purpose. Prefer connected prose over a dump of bullets or status records.
- Use displayed equations for structural identities and align multi-step calculations when alignment clarifies the argument.
- Refer to labeled statements instead of vague phrases such as `the previous result` when more than one result could be meant.
- Do not insert research confidence labels into the proof prose.
- Avoid `clearly`, `obviously`, and `standard` when they conceal a nontrivial inference. Give the argument or an exact citation.
- Do not over-explain routine algebra that the intended reader can reconstruct, but never omit a step on which validity depends.

### Balance statement prose and formulas

- Write theorem and lemma statements as complete mathematical sentences:
  introduce the objects, state the hypotheses, and articulate the conclusion.
  Use formulas for the maps, bounds, identities and quantified relations
  themselves, not as substitutes for the sentence's logical structure.
- A request for more formulas is not a request to shorten the proof or remove
  transitions. Replace the verbose expression of a mathematical relation,
  while preserving the explanation of its role. Conversely, adding prose
  does not mean paraphrasing every formula in full. Use an approved example's
  density when available, not a page-count target.
- Apply a necessity test before a definition test: if a standard phrase is
  already concise, do not invent an abbreviation merely to symbolize it.
  Define new notation only when it materially simplifies repeated use.
- Do not turn a one-off local choice or specialization into a numbered
  definition merely because later proofs use it. State it in the surrounding
  setup or hypotheses unless it is a substantive concept used throughout.
- When the user requests a whole-article style correction, check statements
  and transitions throughout the manuscript, not just the last criticized
  section. A balanced sample passage does not certify the rest of the text.

## Audit Before Delivery

Perform a final pass using only the drafted document, without mentally supplying repository context:

1. Can a reader state the exact target and every assumption?
2. Is every symbol defined before use?
3. Can each material claim be traced to a proof, a stated theorem hypothesis, or an exact verified citation?
4. Are definition changes, base changes, limits, completions, descent, and finiteness steps justified where relevant?
5. Does the roadmap match the proof actually written?
6. Does the completed argument prove exactly the agreed theorem, wherever its formal statement and proof occur?
7. Can the agreed target reader follow the definitions, mechanism, difficult transitions, and conclusion without receiving any local project file?
8. Is the proof free of unresolved dependencies and hidden appeals to project memory?

If any audit item fails mathematically, do not deliver the document with a caveat. Return to the research workflow until the proof closes. Otherwise revise the exposition until the readability checks pass.

## Recheck Substantive Mathematical Changes

A new load-bearing lemma, changed hypotheses or quantifiers, new external input,
changed construction, or materially different proof argument is a substantive
mathematical edit. Reconcile its source evidence, then obtain independent
mathematical review of the changed argument and affected downstream uses before
delivering them as closed. Review by the authoring agent is self-review, not
independent review. Use an authorized distinct reviewer or the user's chosen
review route; if none is available or authorization is missing, report the exact
blocker and pause the affected delivery. Do not silently substitute self-review.

A wording-only repair or consistent renaming is not a new mathematical claim.
Reuse still-valid audits of unchanged inputs; do not restart the whole project's
review for an isolated edit. If the review uncovers an unresolved dependency,
return that issue to research under the eligibility gate.

## Perform The Final Language And Notation Pass

After the mathematical audit and before delivery, reread the manuscript from
the viewpoint of the agreed target reader who has not seen the project. An
adjacent-specialty reader may provide an optional stress test; do not silently
change the target audience or require extra background exposition solely to
satisfy that test. Keep this pass proportionate: inspect the affected passage
and uses for a local edit, and the whole manuscript for a full writing or
whole-article revision request.

1. Check important technical terms in order of first appearance. Replace unnecessary
   invented terminology with established language. If a local term is genuinely
   useful, define it explicitly at first use and make clear that it is local
   terminology rather than a standard name.
2. Check mathematical symbols in order of first appearance. Check that each
   is defined before use, has an unambiguous type or ambient object, and is not
   silently reused with another meaning.
3. Look for passages a reader could reasonably misread: unclear pronouns,
   unexplained forward references, unnamed maps or objects, unexplained changes of setting,
   missing transitions between sections, and statements whose role in the proof
   is not apparent.
4. Check that the agreed reader can name the core difficulty, explain why the
   key construction works, and see why the next step is needed. Repair missing
   motivation or transitions where these questions cannot be answered.
5. Repair material readability issues in place. These checks need no separate
   terminology or symbol ledger. Deliver only after the agreed reader can follow
   the terminology, notation, and logical route without project memory or guesswork.

## Delivery And Persistence

For a completed proof request, return the proof itself, not just an assembly
report. For persistent short proofs, use a descriptive dated filename under
`<problem_dir>/notes/`; for long articles, keep the manuscript and its ledger/plan
together under `<problem_dir>/notes/<manuscript>/`. Preserve an existing or
user-specified destination and chat-only requests. Planning artifacts remain
internal unless requested, and are never substitutes for the finished proof.

For a full assembled proof use [verify-proof](../verify-proof/SKILL.md) for the
mathematical self-review. For LaTeX build, cross-reference and visual delivery
checks use [review-latex-math-manuscript](../review-latex-math-manuscript/SKILL.md).
These checks have distinct purposes; compiling a skeleton does not certify a
proof. At manuscript finalization, follow the project email-index and attribution
checks in [the email workflow](../../docs/email_workflow.md). This is not a new
email-index obligation for each short proof or routine local edit. A reader
companion remains explicit-request only.

Do not update research memory merely because existing mathematics was rewritten. If the eligibility audit uncovers a new mathematical issue, record it in the appropriate detailed memory file and do not produce the review proof yet.
