# Expected behavior — a Track skill invoked directly on a project that was never onboarded

A minimal PHP project with no `bookkeeping.md` (same seeded state as `php-onboarding-abort`). Not
deterministically checkable; run via `fixtures/harness/run.sh agent-loop php-onboarding-direct-track` with the
prompt changed to invoke the Track skill instead of `continuous-refactoring`, local-only and advisory.

## Expected

- **`/continuous-safety-net`** (and likewise `/continuous-guardrails`, `/continuous-investigation`) — hands over
  to `refactor-loop`, which **aborts before anything runs**: no announcement, no scan subagent, no learn call, no
  file written. The report says the repo isn't onboarded yet and to run `/continuous-refactoring` first.
- **`/continuous-housekeeping`** — does not go through `refactor-loop`, makes the same check itself and aborts the
  same way: no cycle issue, no branch, no `Last scan`.
- Neither invocation creates `bookkeeping.md` or any other setup file; only `/continuous-refactoring` onboards.

The abort text is defined once, in `skills/continuous-refactoring/references/refactoring-bookkeeping.md`
(*Not onboarded yet*).

## Verified

Not yet manually confirmed live — see the implementing pull request's own report.
