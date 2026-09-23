# Expected behavior — onboarding resumed after an interruption

An earlier onboarding was interrupted part-way through its writes: the suite's section in `AGENTS.md` (the
first write) and `docs/agents/triage-labels.md` (the second) exist, but `docs/agents/issue-tracker.md` and
`docs/refactoring/bookkeeping.md` do not
(`skills/continuous-refactoring/references/onboarding-setup-interview.md`, *Partial state — resume*). Not
deterministically checkable; run via `fixtures/harness/run.sh agent-loop php-onboarding-interrupted`, local-only and
advisory.

## Seeded state

A minimal PHP project plus an `AGENTS.md` whose `## Continuous-refactoring suite` section names
`Refactoring Notes: docs/refactoring/` and the backlog labels, and the minimal `docs/agents/triage-labels.md` the
onboarding writes (no `needs-triage`/`ready-for-human` rows). No `issue-tracker.md`, no `bookkeeping.md`.

## Expected: the next invocation

1. The first output says onboarding is starting (`bookkeeping.md` is still missing).
2. **The setup-gap question is not asked**, although `issue-tracker.md` is missing: the suite's own section already
   being there says an earlier run got past it. **Q4 is not asked** (the `Refactoring Notes:` line is on record; the
   summary says "already recorded"). **Q1 (tracker), Q2 (`Ticket-create-mode`) and Q3 (`MR-create-mode`) are asked** — the
   tracker choice was never written, and both modes' only home is `bookkeeping.md`.
3. Nothing is overwritten: `AGENTS.md` and `triage-labels.md` are untouched. The missing files are written in
   order — `issue-tracker.md`, then `bookkeeping.md` last, with the answered `Ticket-create-mode` and `MR-create-mode`.
4. The closing text still says the engineering-skills setup can be run later (the label table lacks
   `needs-triage`/`ready-for-human`, so the setup was missing), then commit, then rerun
   `/continuous-refactoring`. No issue, branch, merge request or forge call.

Variant: add a matching `issue-tracker.md` to the seed and only `bookkeeping.md` is missing — the run then asks only
Q2 and Q3, writes only `bookkeeping.md`, and reads the same closing text.

## Verified

Not yet manually confirmed live — see the implementing pull request's own report.
