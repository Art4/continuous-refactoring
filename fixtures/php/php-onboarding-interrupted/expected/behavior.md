# Expected behavior — onboarding resumed after an interruption

An earlier onboarding wrote everything except `docs/refactoring/bookkeeping.md` (the last write, and the
"onboarding complete" marker) — the process stopped before it
(`skills/continuous-refactoring/references/onboarding-setup-interview.md`, *Partial state*). Not
deterministically checkable; run via `fixtures/harness/run.sh agent-loop php-onboarding-interrupted`,
local-only and advisory.

## Seeded state

A minimal PHP project plus `docs/agents/issue-tracker.md` (Local Markdown), `docs/agents/triage-labels.md`
and an `AGENTS.md` whose `## Continuous-refactoring suite` section already carries the
`Refactoring Notes:` line and the `Create-mode` pointer — but not the backlog-labels line. No
`bookkeeping.md`.

## Expected: the next invocation

1. The first output says onboarding is starting (`bookkeeping.md` is still missing).
2. **Nothing already on record is re-asked**: no setup-gap question, no Q1 (tracker), no Q3 (notes
   location). The summary names them as already recorded. **Q2 is asked again** — the create-mode's only
   home is `bookkeeping.md`, which was never written.
3. Nothing is overwritten: `issue-tracker.md` and `triage-labels.md` are untouched; `AGENTS.md` gains only
   the missing backlog-labels line (its existing lines are unchanged). Then `bookkeeping.md` is written,
   last, with the answered `Create-mode`.
4. Closing text and end of invocation as in `php-onboarding-fresh`; no issue, branch or merge request.

## Verified

Not yet manually confirmed live — see the implementing pull request's own report.
