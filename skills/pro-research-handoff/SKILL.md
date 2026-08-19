---
name: pro-research-handoff
description: Prepare, route, and audit a narrow unresolved mathematical research gap for an interactive Pro discussion. Default to a separate Pro chat in the same ChatGPT Work project when the user wants to discuss and steer the research; never substitute an ordinary Codex subagent for the requested Pro mode. Use an immutable packet only across projects, external services, inaccessible sources, or audit-required transfers. Use when the user asks to hand a gap to Pro, prepare a Pro discussion, export or submit a Pro packet, import a returned answer, or review a relay task.
---

# Pro research handoff

Use this workflow only for a genuine open, load-bearing gap with a precise
target. Distinguish an interactive discussion from a one-shot delegated task.

## Choose the route by who must continue the discussion

Use **a separate Pro chat in the same project** by default when the user wants
to question, correct, or explore branches with Pro over multiple turns. Prepare
the self-contained brief as `CURRENT_PRO_HANDOFF.md`. If project-source
create/replace actions are available, add it temporarily to the project's
Sources. Otherwise return the file and ask the user to add it. If a supported
action for creating a sibling project chat is available and the user requested
it, create the chat; otherwise tell the user to open it and select Pro/the
desired model. Never claim that a subagent thread is a user-facing Pro chat.

Do not treat a subagent as Pro unless the active tool schema explicitly exposes
the exact requested Pro model or mode. A high-reasoning Codex subagent is still
a different route. Use ordinary subagents only to prepare the brief, perform an
independent critique, or audit the final return, and label them accurately.

Use the **packet relay** only when the target is outside the current project,
a single self-contained question cannot be delivered in an accepted form, the
user requests a portable immutable audit artifact, or an existing relay task
must be imported or reviewed.

## Resolve the handoff specification

Read current project state read-only, then identify:

- the selected problem and exact mathematical target, including hypotheses and fixed parameters;
- the top-level objective and the target's place in its dependency map;
- proved inputs, conditional claims, evidence, failed routes, and the earliest load-bearing gap;
- permitted routes, prohibited substitutions, and acceptance criteria;
- the requested return: proof, counterexample, obstruction, restricted theorem, source audit, or plan;
- the minimal context that must be copied into the self-contained question;
- whether the user will discuss with Pro in a project chat or needs an external packet.

Use recent discussion when it determines every field uniquely. If a material
field has more than one reasonable interpretation, ask one focused question.
While waiting, do not delegate, create a draft packet, or submit anything. A
complete request that says to proceed needs no redundant confirmation.

## Prepare a same-project Pro chat

Before writing, check whether `CURRENT_PRO_HANDOFF.md` is already active. Do not
overwrite an unresolved handoff. Use a task-specific temporary filename only
when the user explicitly wants concurrent discussions.

Create the compact launch brief:

```markdown
### Interactive Pro discussion brief
- Exact target and hypotheses:
- Top-level dependency:
- Established inputs (with status):
- Earliest load-bearing gap:
- Failed routes worth avoiding:
- Permitted routes:
- Prohibited substitutions:
- Requested first step:
- Acceptance criteria:
- Necessary definitions and prior results, written out here:

Discussion rules:
1. Ask clarifying questions before changing the target or assumptions.
2. Keep proof, conditional claim, evidence, conjecture, and failure separate.
3. Preserve useful failed routes and unresolved obligations across turns.
4. Do not declare completion until the acceptance criteria are checked.
5. At the user's request, produce a final handoff separating proved,
   conditional, plausible, disproved, and unverified claims.
```

Use the repository and current transcript only as inputs while drafting. Make
the brief self-contained and remove dependencies on repository paths, hidden
chat context, or instructions to inspect GitHub. Pro receives only the brief,
as the temporary project Source `CURRENT_PRO_HANDOFF.md`. Do not add the
repository to project Sources merely for this handoff.

Let the user continue the mathematical dialogue directly in the Pro chat. Do
not impose an artificial turn limit on that user-driven discussion. At the end,
have Pro return copy-ready final Markdown or one file for the user to bring back
to Work for independent audit against the repository.

After the audit is recorded, remove `CURRENT_PRO_HANDOFF.md` from project
Sources when a supported removal action is available. Otherwise tell the user
the exact Source name to remove. Do not claim immediate permanent deletion;
project files and conversations follow their applicable retention policy.

## Optional non-Pro subagent assistance

If the user explicitly requests an internal multi-agent debate using the
available Codex agents, do not call it a Pro handoff. Allow one initial response
and at most three follow-ups, each tied to a concrete objection. Stop early on a
verified solution, a precise obstruction, repetition without new evidence,
scope drift, or a strategic choice belonging to the user. Continuing beyond
four responses requires explicit authorization for another bounded cycle.

## Packet relay

Use `<problem_dir>/handoff/` for a selected problem and root `inbox/` only for
cross-project, unassigned, or unprocessed external material. Export with:

```bash
python scripts/pro_handoff.py export <problem_dir> --question-file <utf8-question-file> --context <problem-relative-file> --user-authorized
```

For a short target, use `--question "..."`. Verify the request, manifest, hash,
context scope, and `ready_for_web` status. External submission is manual unless
the user separately authorizes an available browser or connector action. The
export flag records packet authorization; it does not authorize submission.

Require a stabilized `final research handoff` or `最终交接稿`, preserve it
unedited, and import it with:

```bash
python scripts/pro_handoff.py import <problem_dir> <task_id> <response-file>
```

If more than one project, task, or response matches, ask which one to use rather
than selecting by recency.

## Audit every final return

Treat Pro output as evidence, not project truth. Check the exact statement,
definitions, hypotheses, citations, hidden finiteness or base-change assumptions,
limit/completion interfaces, and circularity. Classify every useful claim as
`proved`, `conditional`, `plausible`, `needs verification`, or `false`.

Write audited results to detailed project files first and refresh
`research_state.md` only when its snapshot changes. For packet mode, complete
the review checklist and run:

```bash
python scripts/pro_handoff.py review <problem_dir> <task_id> --summary "short audit outcome"
python scripts/pro_handoff.py status <problem_dir>
```

## Verification checklist

- The chosen route matches who must conduct the multi-turn discussion.
- A user-facing Pro chat is not confused with a subagent thread.
- The target, scope, sources, forbidden substitutions, and acceptance criteria are explicit.
- The Pro brief is self-contained and requires no repository access.
- Only one fixed-slot handoff is active, and it is removed after audit.
- Any optional Codex-agent debate is labeled non-Pro and has a four-response cap.
- User-driven Pro discussion remains open-ended and user-controlled.
- Project state changes only after a final return is audited.
- Packet mode remains private and uncommitted, with matching manifest and hashes.
