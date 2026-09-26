# Expected behavior — onboarding an earlier-version target moves its state

A target that ran a version of the suite which kept its state in a committed `docs/refactoring/`: a
`bookkeeping.md` carrying the create-modes, `Focus areas`, `Refactoring goal` and a `## Safety Net` section, an
`out-of-scope/phpmd.md`, a `housekeeping-template.md`, and an `AGENTS.md` with the old `Refactoring Notes:` line. No
`.scratch/refactor/config.md`, so the Bookkeeping pointer doesn't resolve and `/continuous-refactoring` onboards
(`skills/continuous-refactoring/references/onboarding-setup-interview.md`, *Earlier state* and Q5). Not
deterministically checkable; run via `fixtures/harness/run.sh agent-loop php-onboarding-migration`, local-only and
advisory.

## Expected: first invocation

1. The first output says onboarding is starting. The tracker (Local Markdown) and the engineering-skills setup are
   already recorded, so neither Q0 nor Q1 is asked.
2. **Q2 and Q3 are not asked** — the old `bookkeeping.md` states `ask-each-time` and `human-opens`; the summary says
   they are on record. **Q4** (where the state lives: local files recommended, no forge to make an issue on) and
   **Q5** (move the earlier state: move and remove recommended) are asked.
3. Writes, in order, with one status line each: the moved `Focus areas: src/` and `Refactoring goal: convert legacy
   procedural code to OOP` lines in `AGENTS.md`'s section, and the old `Refactoring Notes:` line and pointer paragraph
   removed from it; `.scratch/refactor/out-of-scope/phpmd.md`; `.scratch/refactor/config.md` with the pointer and
   the two moved modes; `.scratch/refactor/bookkeeping.md` **last**, with the `## Safety Net` section and without the
   four moved fields; then, after all that, the old `docs/refactoring/bookkeeping.md` and `out-of-scope/` removed.
   `docs/refactoring/housekeeping-template.md` stays where it is.
4. A closing text: what was moved and removed; commit the `AGENTS.md` change and the removal of the old files; nothing
   under `.scratch/refactor/`; run `/continuous-refactoring` again.
5. The invocation ends. No candidate issue, branch, merge request or forge call.

Answering **don't move it** to Q5: the old files stay untouched and the new state starts empty.

## Verified

Not yet manually confirmed live.
