# Expected behavior — a bookkeeping issue that can't be read stops the pass

An onboarded target in issue mode: `.scratch/refactor/config.md` points at `https://github.com/example-org/no-such-repo/issues/7`,
which doesn't exist (and the harness's sandbox has no remote and no forge access). Confirms the suite never
creates a replacement for a pointer that doesn't resolve (`skills/continuous-refactoring/references/issue-mode.md`,
*Load* and *Only onboarding creates the issue*). Not deterministically checkable; run via
`fixtures/harness/run.sh agent-loop php-issue-mode-unreadable`, local-only and advisory.

## Expected: `/continuous-refactoring`

1. The dispatcher resolves the pointer, tries to load the issue and can't read it. It **stops** with a message
   naming the reason ("the bookkeeping issue can't be read: …"). It does **not** run onboarding, select a Track,
   scan, or create anything.
2. Nothing is written: no `bookkeeping.md` appears under `.scratch/refactor/`, no issue is created, no branch or
   merge request is opened, `config.md` is untouched.

## Verified

Not yet manually confirmed live.
