# Expected behavior — Guardrails Track rejection symmetry

Confirms `refactor-learn`'s rejection handling for a Guardrails Track candidate mirrors the suite's
existing rejection symmetry everywhere else — merge removes from the in-flight list, rejection removes
from the in-flight list **and** adds a durable pointer — scoped to `## Guardrails`'s own `Open`/
`Out-of-scope` lists instead of the global `out-of-scope/`
(`skills/refactor-learn/references/guardrails-write.md`). The Guardrails Track's own counterpart to
`fixtures/php/php-safety-net-rejection-symmetry`.

Not deterministically checkable — pure bookkeeping-write behavior. Run via `fixtures/harness/run.sh
guardrails-track php-guardrails-rejection-symmetry --opencode`, same non-CI, local-only, advisory
posture as `safety-net-track`/`decision-gate-bypass`.

## Seeded state

The Safety Net is fully closed (same shape as `php-guardrails-open-blocks-rescan`). `.scratch/refactor/
bookkeeping.md`'s `## Guardrails` section: `Open` as a list (`- phpmd (#5)`), `Out-of-scope` as a list (`- none`).
`.scratch/refactor/issues/05-phpmd.md` — already `Status: closed`, `Labels: refactor:candidate,
wontfix`, with a maintainer's own closing comment giving a load-bearing structural reason (cyclomatic
complexity enforced purely by mandatory PR review against a documented checklist, no tool, by team
convention) — the "agent-undetectable equivalent" case ADR-0055's Decision section names, safe here
because `phpmd` carries no required child of its own within the tree.

## Expected: `refactor-learn` early call

Given this finding (closed without merge, `phpmd`, a maintainer's own load-bearing structural reason
already on the issue), it should:

1. Recognize the closing comment as a structural rejection — mark `wontfix` (already set), close the
   issue (already closed).
2. Write `.scratch/refactor/out-of-scope/phpmd.md` — a human-readable rejection entry, format unchanged
   from any other `out-of-scope/` entry, stating the reason from the closing comment.
3. Remove `phpmd` from `## Guardrails`'s `Open` list.
4. Add `phpmd` to `## Guardrails`'s `Out-of-scope` list, pointing at the file written in step 2
   (`- phpmd — out-of-scope/phpmd.md`).
5. **Never** write `phpmd` to a bare global `out-of-scope/` pointer
   outside this Track's own section, and never touch `## Safety Net`'s own `Open`/`Out-of-scope` —
   this candidate's whole lifecycle stays inside `## Guardrails`.

## The behavior this regression-tests

Without this symmetry, a rejected Guardrails Track candidate would either stay stuck in `Open` forever
(never rescanned, since `Open` non-empty blocks a fresh walk — `php-guardrails-open-blocks-rescan`) or
disappear from bookkeeping with no durable record of the rejection at all.

## Verified

Confirmed live via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh guardrails-track
php-guardrails-rejection-symmetry --opencode` (`opencode/muse-spark-1.2-contributor-free`): the model
wrote `out-of-scope/phpmd.md` with the maintainer's own reason, removed `phpmd` from `## Guardrails`'s
`Open`, and added the `Out-of-scope` pointer — all three assertions passed. See the implementing pull
request's own report for the full transcript summary.
