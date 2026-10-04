# Research State Workflow

This document owns the detailed state, project-creation, and closeout rules
indexed by the root `AGENTS.md`.

## Problem layout

Each registered mathematical problem is one independent directory:

```text
<problem_dir>/
├── research_state.md
├── goal.md
├── progress.md
├── subgoal.md
├── YYYY-MM-DD.md
├── notes/
├── memory/
├── refs/
├── downloads/
├── email/
└── handoff/
```

Use the files as follows:

| Content | Destination |
| --- | --- |
| Compact current dashboard | `research_state.md` |
| High-level objective and problem statement | `goal.md` |
| Cross-session progress | `progress.md` |
| Current proof decomposition | `subgoal.md` or `memory/subgoals_state.md` |
| Session narrative and calculations | `YYYY-MM-DD.md` |
| Informal fragments | `notes/` |
| Failed routes and exact failure points | `memory/failed_paths.md` |
| Counterexamples | `memory/counterexamples.md` |
| Toy examples | `memory/toy_examples.md` |
| Direct consequences | `memory/immediate_conclusions.md` |
| Literature findings | `memory/search_results.md` |
| Formalization plans | `memory/formalization/<slug>.md` |
| Substantial skill/tool event log | `memory/events.md` |
| Source files and searchable extracts | `refs/` and `downloads/` |
| Explicit cross-project/external relay records | `handoff/` |
| Private correspondence, contribution provenance, and version-scoped commitments | `email/`; see [email workflow](email_workflow.md) |
| Manuscript-specific result ledger and reader plan | `notes/<manuscript>/THEOREM_LEDGER.md` and `PAPER_PLAN.md` |

Include the date, exact statement, assumptions, status or confidence, and
evidence or failure reason in substantive mathematical records. Conditional
claims name the unresolved premises. Failed routes record a precise reopening
condition; withdrawals and user pauses stay visible until explicitly resolved.
Distinguish self-review, independent review, and formal verification.

## Compact state contract

Every problem must have `research_state.md`, initialized from
`templates/research_state.md`, with these six sections:

1. `Research State`: exact target, assumptions, status, confidence, last update,
   and compact summary.
2. `Known Theorems`: directly relevant results with hypotheses and verification
   status.
3. `Open Problems`: unresolved obligations.
4. `Failed Attempts`: attempted route, first failure point, and reusable lesson.
5. `Current Goal`: exactly one active target, next action, and blocker.
6. `References`: key sources, local locations, theorem numbers, relevance, and
   verification caveats.

`research_state.md` is a dashboard and navigation page, not a transcript. Keep
long proofs, searches, examples, and historical detail in their specific files
and link to them. Detailed records are authoritative for evidence and history;
the state page is authoritative for the current snapshot.

For substantive progress, update detailed records first and refresh the compact
state last. If a dated record conflicts with the dashboard, inspect the actual
evidence and current scope, correct the dashboard, and preserve superseded
history. A newer timestamp is not proof of validity; a maintenance date is not
a mathematical audit date. Never delete a failed route merely to make the
current state look cleaner.

`subgoal.md` is the current decomposition, initialized for new projects from
`templates/subgoal_plan.md`: precise subgoals, dependencies, status and evidence,
blockers, and reopening conditions. Keep earlier decompositions in the dated
notes or `memory/subgoals_state.md`. Do not automatically migrate existing files.

## Lossless navigation-file compaction

Follow [state compaction](state_compaction.md) for `research_state.md` and
`subgoal.md` separately. More than 24,576 bytes AND a recorded substantive
milestone permits a proposal, not an edit; 250 lines is only an advisory warning.
Check prior proposals in `memory/events.md` and ask once for the named files.
Wait for explicit approval before drafting, archiving, or rewriting; a user's
explicit request to compact those named files already supplies approval.

Archive and verify the original raw bytes and SHA-256 before an approved rewrite.
Keep precise mathematical content in durable linked detail, preserve old links
and stable anchors (including inbound links), and retain hypotheses, audit
caveats, failures, pauses, withdrawals, and reopening conditions. Never compress
progress, daily notes, or memory logs automatically. No new proposal database
is needed.

The checker is read-only navigation assistance, not proof certification or
permission to compact:

```bash
python scripts/check_research_state.py <problem_dir> --check-links
python scripts/check_research_state.py <problem_dir> --file subgoal.md --check-links
python scripts/check_research_state.py <problem_dir> --milestone "<recorded outcome>"
```

## Startup and daily notes

Use the startup order in root `AGENTS.md`. Create today's note only when the user
expects persistent work and there is substantive material to record. Do not
create or edit project files when the user explicitly asks for discussion only.

Read current state and subgoals, then the latest 3–5 complete dated progress
entries and relevant daily sections before targeted backtracking. Locate heading
boundaries before extracting entries, and follow evidence links rather than
reading every historical log by default. Expand when evidence or scope conflicts;
resume instructions cannot override a withdrawn premise, changed goal, or pause.

Append dated sections to logs and memory files. `research_state.md` and
`subgoal.md` may be edited as current snapshots, but preserve relevant history
in the detailed records.

## Create a new project

Before creating anything, fix the directory name, title, exact objective and
scope, registry role, one-line description, and relationship to existing
projects. Ask a focused question if any of those fields is materially ambiguous.

Then run:

```bash
python scripts/create_math_project.py <problem_dir> \
  --title "<title>" \
  --role active \
  --description "<one-line objective>"
```

The resulting problem includes the standard snapshots, logs, `notes/`, `memory/`,
`refs/`, `downloads/`, `email/`, and `handoff/`. It uses both state and subgoal
templates and initializes a private email README, contact list, contribution/
obligation index, and attachments directory without inventing contacts or
agreements. It must be registered in the ignored `projects.local.json`, not the
public examples registry. Do not add numeric problem IDs or a `problem-id`
argument to search commands; the registered directory path identifies the project.

Private state created by this workflow remains ignored by Git unless the user
explicitly decides to publish it.

## Closeout order

At the end of substantive work:

1. Write new proof evidence, counterexamples, failed routes, references, and
   formalization findings to the relevant detailed files.
2. Update today's dated note with the session narrative and decisions.
3. Update `progress.md` and, when applicable, `subgoal.md`.
4. Refresh the six-section `research_state.md` last.
5. Check internal links and ensure the next action and blocker are explicit.
6. Report what changed, what remains open, and where the next session should
   resume.

When finalizing or releasing a manuscript, additionally inspect `email/index.md`
for the exact version's contribution, attribution, circulation, and reply
obligations under [email workflow](email_workflow.md). This is conditional on
finalization/release, not every compile or ordinary research closeout. Drafts
are not sent messages; proposals and silence are not agreements.

Do not rewrite the dashboard after a trivial exchange. Do not confuse a local
workspace write or local commit with externally durable persistence.
