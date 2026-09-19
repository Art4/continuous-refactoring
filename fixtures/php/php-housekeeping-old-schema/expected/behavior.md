# Expected behavior — old-schema bookkeeping.md still passes Housekeeping reconciliation

Confirms a target with a pre-ADR-0055 `bookkeeping.md` shape (`Fulfilled nodes` populated, no
`## Housekeeping` section) runs a normal Housekeeping Track pass without erroring on, migrating,
or needing to understand the pre-existing old-shape `Fulfilled nodes` field.

Not deterministically checkable — pure skill process behavior. Run via
`fixtures/harness/run.sh housekeeping php-housekeeping-old-schema --opencode`,
same non-CI, local-only, advisory posture as `decision-gate-bypass`.

## Seeded state

`docs/refactoring/bookkeeping.md` in the pre-ADR-0055 shape: `Fulfilled nodes` already lists
`loop-config`, `composer`, `php-cs-fixer`, `phpunit`, `phpstan-level-0` (no issue numbers —
predates that convention), `Pending candidates: - none`. **No `## Safety Net`, `## Guardrails`,
or `## Housekeeping` heading anywhere in the file.** The project genuinely fulfils those nodes
(`composer.json` + `.php-cs-fixer.php` + `phpunit.xml` + `phpstan.neon` with level 0 and empty
baseline). `php-minimal-version` is also fulfilled (PHP 8.1 declared) but not listed in
`Fulfilled nodes`.

## Expected: Housekeeping Track reconciliation

When the Housekeeping Track runs:

1. It reads `bookkeeping.md` and does NOT error on the `Fulfilled nodes` field — it's retired
   and ignored, not something that blocks processing.
2. The reconciliation walks the tooling tree and checks nodes with a `Housekeeping` field via
   agent judgement, NOT by reading `Fulfilled nodes`.
3. Nodes judged fulfilled (composer, php-cs-fixer, phpunit, phpstan-level-0, php-minimal-version)
   get their `Housekeeping` lines appended to `housekeeping-template.md` (created fresh).
4. The `Fulfilled nodes` field is never read — the old shape is left untouched.
5. The Track reports "due, with checklist items registered" and proceeds normally.

## Expected: `refactor-learn`

The closing call writes `## Housekeeping`'s `Last scan` to today's date. The pre-existing
`Fulfilled nodes`/`Pending candidates` content is left exactly as it was — this write never
touches, migrates, or removes it.

## The behavior this regression-tests

Without the agent-judgement reconciliation, the Housekeeping Track would try to read
`Fulfilled nodes` (the old cache) to discover which nodes contributed housekeeping lines.
While this works for most nodes, it misses Guardrails tools adopted by hand and creates a
dependency on a field that is being retired. The agent-judgement approach is independent of
`Fulfilled nodes` and handles old-schema repos transparently.

## Verified

Not yet manually confirmed live against an opencode model run — see the implementing pull request's
own report for what was attempted and observed.
