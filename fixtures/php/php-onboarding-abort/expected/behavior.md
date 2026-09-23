# Expected behavior — onboarding aborted at the setup-gap question

Same seeded state as `php-onboarding-fresh` (a minimal PHP project with no `docs/agents/` files, no
`AGENTS.md`/`CLAUDE.md`, no `bookkeeping.md`), but the human answers the setup-gap question with **abort**
(`skills/continuous-refactoring/references/onboarding-setup-interview.md`, *Setup gap*). Not deterministically
checkable; run via `fixtures/harness/run.sh agent-loop php-onboarding-abort`, local-only and advisory. The
harness prompt has no human to answer, and unattended the question defaults to *continue* — so this scenario needs
the prompt to supply "Q0: abort" explicitly.

## Expected: the invocation

1. The first output says onboarding is starting; the engineering-skills setup is reported incomplete and the one
   up-front question is asked. Q1–Q4 are never asked.
2. On **abort**: **nothing is written** — no `AGENTS.md`, no `docs/agents/` file, no `docs/refactoring/`, no commit,
   no branch. The human is pointed at `setup-matt-pocock-skills` to run first, and the invocation ends. No scan
   subagent, no Track selected.

## Expected: the next invocation

Onboarding starts over from scratch (nothing was recorded): the same first output and the same setup-gap question
— unless the human ran the setup meanwhile, in which case the question is skipped.

## Verified

Not yet manually confirmed live — see the implementing pull request's own report.
