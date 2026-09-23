# Expected behavior — Safety Net Track rejection symmetry

Confirms `refactor-learn`'s rejection handling for a Safety Net Track candidate mirrors the suite's
existing rejection symmetry everywhere else — merge removes from the in-flight list, rejection removes
from the in-flight list **and** adds a durable pointer — scoped to `## Safety Net`'s own `Open`/
`Out-of-scope` lists instead of the global `out-of-scope/` (`skills/refactor-learn/
references/safety-net-write.md`).

Not deterministically checkable — pure bookkeeping-write behavior. Run via `fixtures/harness/run.sh
safety-net-track php-safety-net-rejection-symmetry --opencode`, same non-CI, local-only, advisory
posture as `decision-gate-bypass`.

## Seeded state

`docs/refactoring/bookkeeping.md`'s `## Safety Net` section: `Open` as a list (`- php-cs-fixer (#5)`),
`Out-of-scope` as a list (`- none`). `.scratch/refactor/issues/05-php-cs-fixer.md` — already `Status: closed`,
`Labels: refactor:candidate, wontfix`, with a maintainer's own closing comment giving a load-bearing
structural reason (code style enforced purely by PR review, no tool, by team convention) — the
"agent-undetectable equivalent" case ADR-0055's Decision section names (a committed-artifact-free
Purpose served some other way).

## Expected: `refactor-learn` early call

Given this finding (closed without merge, `php-cs-fixer`, a maintainer's own load-bearing structural
reason already on the issue), it should:

1. Recognize the closing comment as a structural rejection — mark `wontfix` (already set), close the
   issue (already closed).
2. Write `docs/refactoring/out-of-scope/php-cs-fixer.md` — a human-readable rejection entry, format
   unchanged from any other `out-of-scope/` entry, stating the reason from the closing comment.
3. Remove `php-cs-fixer` from `## Safety Net`'s `Open` list.
4. Add `php-cs-fixer` to `## Safety Net`'s `Out-of-scope` list, pointing at the file written in step 2
   (`- php-cs-fixer — out-of-scope/php-cs-fixer.md`).
5. **Never** write `php-cs-fixer` to a bare global `out-of-scope/`
   pointer outside this Track's own section — this candidate's whole lifecycle stays inside `##
   Safety Net`.

## The behavior this regression-tests

Without this symmetry, a rejected Safety Net Track candidate would either stay stuck in `Open` forever
(never rescanned, since `Open` non-empty blocks a fresh walk — `php-safety-net-open-blocks-rescan`) or
disappear from bookkeeping with no durable record of the rejection at all.

## Verified

Not yet manually confirmed live against an opencode model run — see the implementing pull request's
own report for what was attempted and observed.
