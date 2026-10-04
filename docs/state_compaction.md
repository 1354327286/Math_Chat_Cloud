# Navigation-file compaction at research milestones

This is a session-driven workflow over the existing project files. It does not
start a scheduled monitor or an autonomous research run. It applies separately
to research_state.md and subgoal.md. Keep one shared consent, archival and
verification procedure; do not maintain a second proposal database.

## File roles and retained content

| File | Retain in the current file | Keep in linked detailed records |
| --- | --- | --- |
| research_state.md | Six sections, precise scope/assumptions, current status, key inputs and caveats, one target, next action and blocker | Full proofs, searches, chronology and detailed failures |
| subgoal.md | Exact active target and assumptions; current subgoals with statements, dependencies, status/evidence and gaps; next action and completion condition; relevant route constraints | Superseded decompositions, full proofs and chronological attempts in dated notes or memory/subgoals_state.md |

The recommended subgoal layout is templates/subgoal_plan.md. Existing headings
remain valid; no automatic migration or rigid new section requirement applies.
Keep stable subgoal labels when cited elsewhere. Retain enough failed-route
information to prevent repetition: exact failure, evidence and reopening
condition. Deferred work may remain as short pointers clearly marked inactive.
Scope changes, unresolved dependency caveats, user pauses, frozen contracts and
withdrawn premises must survive consolidation.

Both navigation files use advisory budgets of 250 lines / 24 KiB. After
approved compaction aim for about 8–12 KiB per file, allowing more for exact
statements and dependencies. Bytes are a navigation measure, not a mathematical
quality score.

goal.md preserves the exact long-term statement and scope; move extended scope
history to linked dated records only within an authorized maintenance task.
progress.md, daily notes and memory logs preserve history: use section retrieval
by default. Size alone does not authorize their compaction, rewriting or
deletion. If explicit archival into volumes is requested, preserve original
bytes, chronology, provenance and inbound links. The reminder policy below
does not automatically extend to these historical files.

## When to propose

After recording substantive progress and refreshing the current state, check
the selected project's affected navigation file. Propose compaction only when both
conditions hold:

- Its UTF-8 file size exceeds **24 KiB (24,576 bytes)**.
- A substantive milestone has been recorded: for example a scoped lemma is
  closed, an audited counterexample is established, a proof route is closed
  with an exact reusable failure, a manuscript revision is completed, or a
  reviewed external result materially changes the next goal.

A new date, routine formatting, another inconclusive wave, or merely crossing
250 lines is not a milestone. Do not invent a result to trigger maintenance.
Until a milestone, a large-state diagnostic is an internal navigation warning;
continue ordinary work using targeted retrieval. Evaluate size and proposal
history per file; do not include a small state page just because its subgoal
file is large. If both qualify, one proposal may name both files explicitly.

The read-only helper checks one named navigation file at a time. It measures the
raw UTF-8 bytes (not characters), diagnoses missing or duplicate state sections,
and optionally checks local Markdown file targets. It never verifies the
milestone, proves a claim, checks heading anchors, or changes project files.
It has no compaction or archive action. Exit status 1 means a structural,
encoding, or local-link error; size and line warnings alone exit successfully.
Existing subgoal headings remain valid and do not receive a rigid schema check.

The helper can provide conditional reminder text:

```bash
python scripts/check_research_state.py <problem_dir> --milestone "<recorded outcome>"
python scripts/check_research_state.py <problem_dir> --file subgoal.md --milestone "<recorded outcome>"
```

The agent supplies the milestone from actual evidence; the helper checks size,
not mathematical truth or prior consent/proposal history. Its reminder is
conditional on manually checking `memory/events.md` for an outstanding or deferred
proposal. It does not send a message, record consent, or modify files.

## Reminder and user agreement

At a natural milestone or closeout, tell the user the project, filename, current size,
recorded outcome, and proposed scope. For example:

> This project's state page is now 31 KiB. The scoped lemma has reached a
> recorded conclusion, so this is a good point to consolidate the state.
> May I archive the original and compact this state page, preserving its exact
> target, assumptions, confidence, open obligations and evidence links?

Use the app's question mechanism when appropriate. Continue unrelated authorized
research while awaiting an answer. Do not create an archive, draft a compressed
file, or rewrite the file for this compaction before agreement arrives.
Ordinary updates that record newly established research remain authorized.

Record the proposal and subsequent response as a short dated entry in the
existing `memory/events.md`, identifying each proposed file path, measured size, milestone
and its evidence link. Do not create a second status database. Skip such writes
in an explicitly read-only conversation.

- Do not repeat an outstanding proposal in later turns or sessions.
- If declined or deferred, wait for another substantive milestone or an explicit
  request before suggesting again. Respect a longer user-specified deferral.
- An affirmative reply covers only the named file(s) and their necessary archive,
  navigation checks and maintenance log. It does not cover other projects,
  deleting historical notes, changing mathematical claims, or resuming research.
- An explicit request to compact already supplies agreement. This workflow's
  standing authorization to remind is not consent to each future compaction.

## Execute after agreement

1. Re-read the selected file and compare its current target, assumptions, confidence,
   blockers and key source restrictions with current subgoals and relevant
   recent detailed records. If substantive conclusions conflict, resolve the
   evidence or ask about the exact conflict; do not choose a different theorem.
2. Preserve the original bytes in a unique dated directory under `notes/`.
   Never overwrite an earlier archive. Copy with byte-preserving I/O, not text
   decoding/re-encoding: retain Unicode, newline style and any byte-order mark
   exactly. Record original path, original relative-link base, byte count and
   SHA-256 in a separate receipt; verify the archive's byte count and hash against
   the original before rewriting. A hash detects byte changes, not authenticity
   or mathematical correctness. Recheck that the live source still matches the
   archived original immediately before replacement.
3. For research_state.md, keep all six state sections. Retain the exact target and hypotheses,
   current audit status, key established inputs, unresolved obligations,
   relevant failed routes and one current goal. Link to detailed evidence.
   Aim for about **8–12 KiB**, allowing more when the precise scope needs it;
   never truncate mathematics just to reach a size target.
   For subgoal.md, preserve the current dependency-ordered decomposition,
   precise subgoal statements and hypotheses, statuses, proof/source links,
   blockers, next action and completion conditions. Move historical
   decompositions to dated notes or link existing complete evidence. Retain
   stable labels and relevant failure/reopening warnings. Never turn a partial
   or conditional result into a completed subgoal by shortening its description.
4. Keep the combined live navigation and linked detailed records mathematically
   lossless: every exact statement, hypothesis, dependency, gap, status, failure,
   qualification and source must remain recoverable with its original meaning.
   A raw archive alone does not justify dropping a live warning or obligation.
   Compare the retained content against the original and detailed evidence;
   preserve user pauses, frozen contracts and withdrawn-result warnings.
   Record the maintenance date separately from the mathematical audit date.
5. Preserve inbound links to moved sections: search affected project Markdown
   for file/heading references, retain an anchor or redirect pointer at the old
   location where practical, or update referring links within the approved
   scope. Do not alter frozen handoff inputs or historical archive bytes.
   Original archive bytes retain their original relative-link base in the
   receipt; link live navigation to relocated evidence using correct paths.
6. Run `python scripts/check_research_state.py <problem_dir> --check-links`
   for state maintenance, or add `--file subgoal.md` for subgoal maintenance.
   Run both when both were edited. This checks local file targets, not heading
   anchors; manually verify moved headings, dependency links and their meaning.
   Verify archive integrity and local links, and append the result and the
   user's agreement to the existing maintenance event. Report before/after
   size and any unresolved issue. A navigation check is not a proof audit.

If a selected file changes after approval but before the rewrite, re-read the change
and rebuild the compaction from current evidence; never overwrite concurrent
user work. Materially changed scope requires resolving that scope first.

## Read-only examples and limits

```bash
python scripts/check_research_state.py <problem_dir>
python scripts/check_research_state.py <problem_dir> --check-links
python scripts/check_research_state.py <problem_dir> --file subgoal.md --check-links
```

The helper checks common inline and reference-style Markdown links, including
relative paths, nested bullet links, images and percent-encoded filenames.
HTTP(S), FTP(S), mailto, DOI and arXiv URLs and network URL references are skipped;
no network requests are made. Unknown/unsafe schemes (including local file URIs),
control characters, absolute local paths and local links escaping the repository
(including through symlinks) are errors. Each problem is a top-level repository
directory, so its parent is the link-check boundary; valid `../inbox/` links are
allowed. Use relative repository paths for local evidence. Fragment-only links
and heading anchors need manual verification, as do links constructed with HTML
or dynamically generated syntax.
Code blocks and inline code are not evidence links. A successful run means only
that the supported navigation checks passed, never that a proof, reference,
subgoal dependency, archival receipt or user approval was validated.

It reads only the selected navigation file and tests local linked paths for
existence. It does not read or update `memory/events.md`, record a proposal,
create a draft or archive, or rewrite `goal.md`, `progress.md`, daily notes or
memory logs. The agent remains responsible for evidence, consent, proposal
history, archive verification and anchor preservation under the procedure above.
