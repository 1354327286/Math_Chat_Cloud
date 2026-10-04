# Academic Email Workflow

Each registered mathematical problem may keep private academic correspondence
under `<problem_dir>/email/`. Use this directory for project-specific contacts,
incoming email, reply drafts, sent-message records, and source attachments.
Use root `inbox/` only while material is unassigned or unprocessed.

Recommended layout:

    email/
    ├── README.md
    ├── contacts.md
    ├── index.md
    ├── YYYY-MM-DD_correspondent_topic.md
    └── attachments/

`contacts.md` records the name, verified email address, affiliation, verification
date/source, and relevant projects. `index.md` is a compact chronological thread
list with links to detailed records, the affected manuscript/version, message
status, and any open conditional obligation. A thread file should record:

- correspondent and verified address;
- incoming/sent dates and current status;
- a factual summary of the incoming message;
- precise mathematical claims and who supplied them;
- what was already known before the message;
- observations made only after receipt, including AI-assisted analysis;
- verification status and source checks;
- reply drafts, clearly labelled as drafts;
- the exact sent text only after the user confirms sending;
- follow-up obligations and attribution or priority notes;
- local paths to raw screenshots or exported messages.

Do not silently turn a draft into a sent record. Do not treat an external
mathematical suggestion as established project truth. Do not infer joint
authorship, permission to quote, or collaboration terms from ordinary
correspondence. Keep personal contact information and raw messages local:
the generic `.gitignore`, public-scope checker, and portable problem bundle
all treat `email/` as private project data.

## Record contribution provenance as work develops

Do not wait for an authorship question or a finished manuscript to reconstruct
the history. Start a thread record when project-specific correspondence is
processed and append evidence as the exchange and mathematics develop:

1. **Before the contribution:** identify the dated result, proof, manuscript
   version, or other local record showing what was already known. If the earlier
   state is uncertain, say so rather than backdating a claim of priority.
2. **During the exchange:** preserve the received claim or suggestion, its
   source and date, who supplied it, and what has or has not been verified.
   Record proposed collaboration or credit separately from mathematical facts.
3. **After the contribution:** link later proofs, simplifications, corrections,
   and AI-assisted analysis to the input they used. For each affected manuscript
   version, record which contributions are retained, omitted, or deferred and
   what attribution or authorship decision remains open.

Use local file paths and specific sections where possible. Preserve raw messages
and source attachments rather than replacing them with a later summary. A
summary should distinguish quotation, the user's recollection, and inference;
missing evidence remains missing. If a source is still in root `inbox/`, link
its repository-relative path so the problem bundle can include it.

Keep message state separate from commitment state: a **draft** has not been
sent; **sent** means the actual text and sending evidence have been recorded;
a sent **proposal** or **unilateral commitment** is not **mutual agreement**.
Link the correspondent's actual response before recording an agreement. Mark
later changes by a dated addendum; do not overwrite the original sent text.

For each follow-up, credit decision, or sharing restriction, record its exact
artifact/version, triggering condition, responsible person, due date or review
point when one exists, and evidence of completion, revision, or agreement.
An unknown date or undecided arrangement should remain explicit, not be filled
with an invented deadline or promise. Keep these actionable pointers in
`email/index.md` and the full evidence in the thread record.

## Manuscript finalization and release check

Before finalizing or releasing a manuscript revision, inspect the project's
`email/index.md` for conditional follow-ups, promised updates, attribution,
and acknowledgement issues. Recheck each condition against the actual
manuscript and authorship state. Do not describe a possible revision as an
existing v2, and do not send any message without the user's explicit approval.

This check is triggered by manuscript finalization or release, not by every
local LaTeX compile or grammar edit. Review the relevant thread records when
an indexed condition applies, check the actual retained contributions, and
surface any unresolved decision or promised update before presenting the
manuscript as ready. Record the reviewed version and outcome without claiming
that an unsent draft fulfilled a follow-up. If the index is missing or incomplete,
check available correspondence and report the gap; do not infer that there are
no obligations. This is a local review step, not permission to contact anyone.

## Scope before authorship or publication commitments

Discuss authorship early and revisit it as the research develops. The aim is
to avoid an unexamined commitment, not to postpone the conversation until
all work is finished. Distinguish a provisional plan from an agreed decision.

Warm mathematical discussion does not require an immediate commitment about
authorship, publication, or confidentiality. Distinguish thanking someone,
inviting further discussion, proposing a defined collaboration, and offering
coauthorship. Do not upgrade one into another when drafting or interpreting
an email. A correspondent's willingness to coauthor is not itself a decision
that coauthorship is the appropriate arrangement.

Before drafting a substantive commitment, establish from the request and
records:

- which artifact or version is involved: the original paper, a revision
  containing new results, a separate extension, or a new project;
- what was completed before the exchange, what the correspondent supplied,
  and what was developed afterward, including changes to the proofs;
- what joint work is actually proposed and what remains undecided;
- whether an invitation, acceptance, publication plan, or restriction on
  circulation has already been communicated.

Resolve a material ambiguity before putting a commitment in the user's
voice. In particular, “keep the paper single-authored” does not identify
whether the user means the original result or the expanded revision.
Use existing context when it resolves the issue; do not add a routine
confirmation step to ordinary replies or already authorized decisions.

When scope is unsettled, a discussion invitation is often sufficient, for
example: “I would be interested in exploring this further. Perhaps we could
first discuss the scope of the project.” Do not invent an offer of authorship
to make a reply sound appreciative. When the user is uncertain about an
important commitment, suggest consulting their advisor or another trusted
colleague before making it; this is advice, not a universal permission gate.

## Contributions, acknowledgements, and versions

Evaluate the nature and use of contributions, not merely their number or
length. A short conceptual suggestion may be substantial; a nearly complete
prior proof does not by itself settle authorship. Conversely, helpful
discussion does not automatically require coauthorship. Do not present a
single informal threshold as a universal academic rule.

Keep provenance specific to the version under consideration. Retaining only
the original theorem's scope is different from reverting to the original
text: the retained paper may still use a correspondent's proof simplification
or other suggestions. Match any acknowledgement to the actual help received
and reflected in that paper. Do not promise an acknowledgement merely as a
polite substitute for an authorship invitation, or remove appropriate credit
because authorship plans changed. Credit for a deferred extension must remain
recorded for any later work that uses it.

The value of an independent paper to an early-career researcher may inform
how projects are separated, but does not by itself settle credit for others'
contributions. Do not use career considerations to justify omitting credit.

## Revisiting commitments and limiting new ones

Read the exact earlier exchange before drafting a change of plan. An explicit
coauthorship invitation can create a reasonable expectation even before a
final manuscript is approved. Present a proposed change as something to
discuss with the correspondent, not as an arrangement they have already
accepted. Distinguish the user's current preference, the proposal sent, and
the other person's response in the correspondence record.

Explain reconsideration candidly. Do not invent a misunderstanding to cover
a changed preference. If the user says their advisor recommended a change,
that may be stated accurately, while taking responsibility for the earlier
communication. Avoid language that disparages the correspondent's contribution
or makes further suggestions sound like a condition for earning authorship.

Do not repair one premature commitment by introducing another. Before
offering to withhold, defer, or stop circulating results, make the intended
materials, recipients or permitted discussions, and duration or review point
clear enough for the actual situation. Do not silently expand a request to
defer publication into a ban on private discussion, or promise indefinite
restrictions the user has not chosen. Wording must also respect prior
disclosures; do not imply that already shared material has never circulated.

Record any agreed change and its precise scope without deleting the earlier
invitation or attribution history. A draft renegotiation remains a draft;
the correspondent's agreement must not be inferred from silence.

## Evidence and human judgment before sensitive advice

When advising on a new or changed authorship offer, publication separation,
or a restriction on sharing, check applicable primary guidance before
recommending a course of action. Reuse a recent verified source review when
it covers the same question; refresh it when the venue, policy or issue
changes. Mere grammar edits do not require a new search. Prefer the relevant
mathematical society, institution and target journal over anecdotes; do not
apply biomedical authorship tests to mathematics without checking scope.

Separate three things in the response: what a source actually requires or
recommends, the factual contribution/version record, and the assistant's
case-specific interpretation. Do not describe a preferred phrase or a
disputed contribution threshold as universal etiquette. Public guidelines
cannot adjudicate a particular collaboration from a short email alone.

For a sensitive change, first give the user a compact decision summary:
the exact version, proposed arrangement, existing expectations, and any new
commitment created by the draft. Where the user is unsure, recommend that
their advisor or a trusted mathematician review that concrete arrangement
and final text. Do not substitute confident language polishing for this
substantive review or invent a mandatory advisor-approval rule.

After sending, preserve the actual text and distinguish proposal, unilateral
commitment and mutual agreement. Do not repeatedly rewrite an already sent
message as though it were still a draft. Assess any further message against
new information or a material correction, rather than anxiety about wording.

## Source basis and limits

Checked 2026-09-26; these sources support principles, not a ruling on any
individual's entitlement to authorship.

- [AMS ethical guidelines, reproduced in January 2015 Council minutes,
  Attachment K, printed p. 50](https://www.ams.org/about-us/governance/council-meetings/council-minutes0115.pdf):
  significant contributions to a paper's content warrant an offer of authorship;
  unpublished contributions also deserve appropriate credit. The official
  indexed passage was available; direct retrieval of this PDF and the current
  policy landing page failed. Do not represent this as verification of every
  current AMS publication rule.
- [UKRIO, Good Authorship Practice, version 01, 17 September 2025](https://ukrio.org/wp-content/uploads/Good-Authorship-Practice.pdf),
  pp. 3–6: early discussion, review as work evolves, documented criteria and
  recognition of contributions; no universal authorship standard across fields.
  Retrieved through the [current toolkit](https://ukrio.org/resources/the-authorship-integrity-toolkit/).
- [Albert and Wager, COPE Report 2003, pp. 32–34](https://members.publicationethics.org/sites/default/files/2003pdf12_0.pdf):
  discuss expectations, record decisions and communicate changes. This older
  guide uses medical publishing criteria; its first/last-author and ICMJE
  passages are not mathematical authorship rules.

Version identification, neutral wording, scoped sharing commitments and the
assistant's source-check procedure above are local workflow safeguards.
They are not claimed to be verbatim requirements of these sources. No source
here establishes that an independent early-career paper is always necessary,
that a suggestion alone never warrants authorship, or that an earlier offer
can be unilaterally withdrawn without discussion.
