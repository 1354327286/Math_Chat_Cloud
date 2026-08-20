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

Include the date, exact statement, assumptions, status or confidence, and
evidence or failure reason in substantive mathematical records.

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
state last. If a newer dated record conflicts with the dashboard, inspect the
evidence, correct the dashboard, and preserve the superseded history. Never
delete a failed route merely to make the current state look cleaner.

## Startup and daily notes

At startup, read only `research_state.md` and today's dated note, or the most
recent dated note when today's file does not exist. Do not preload `goal.md`,
`progress.md`, `subgoal.md`, or the whole `memory/` tree. After orienting from
those two files, open only the linked detail, proof, reference, or memory files
needed by the selected task.

Create today's note only when the user expects persistent work and there is
substantive material to record. Do not create or edit project files when the
user explicitly asks for discussion only.

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

The resulting problem should include the standard snapshots, logs, `notes/`,
`memory/`, `refs/`, `downloads/`, and `handoff/`, and must be registered in the
ignored `projects.local.json`. Do not add numeric problem IDs or a `problem-id`
argument to search commands; the registered directory path identifies the
project.

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

Do not rewrite the dashboard after a trivial exchange. Do not confuse a local
workspace write or local commit with externally durable persistence.
