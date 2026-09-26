# Expected behavior — onboarding, engineering-skills setup present

A target that has never run the loop but already has both `docs/agents/issue-tracker.md` (Local
Markdown) and `docs/agents/triage-labels.md`. Same dispatcher step 0 as `php-onboarding-fresh`
(`skills/continuous-refactoring/references/onboarding-setup-interview.md`), minus everything the
existing setup already answers. Not deterministically checkable; run via
`fixtures/harness/run.sh agent-loop php-onboarding-set-up`, local-only and advisory.

## Seeded state

A minimal PHP project plus `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md` (all five
engineering-skills roles and a `done` row). No `AGENTS.md`/`CLAUDE.md`, no `bookkeeping.md`.

## Expected: first invocation

1. The first output says onboarding is starting; no scan subagent, no Track selected.
2. **No setup-gap question** (both files exist), and **no Q1** (`issue-tracker.md` already answers it —
   the summary names the tracker as already recorded). Q2, Q3 and Q4 are asked, one at a time.
3. An informational summary, then one status line per write: the suite's section in a newly created
   `AGENTS.md` (both backlog labels), then `.scratch/refactor/bookkeeping.md` last.
   `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md` are **left untouched** (the `done`
   row is already there).
4. Closing text: what was created, commit the files, rerun `/continuous-refactoring`. No line about
   running the engineering-skills setup later.
5. The invocation ends; no issue, branch, merge request or forge call.

## Verified

Not yet manually confirmed live — see the implementing pull request's own report.
