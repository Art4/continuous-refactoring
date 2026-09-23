# Expected behavior — old-schema bookkeeping.md still passes Housekeeping reconciliation

Confirms a target with a pre-ADR-0055 `bookkeeping.md` shape (global `Pending candidates`, no
`## Housekeeping` section) runs a normal Housekeeping Track pass without erroring on, migrating,
or needing to understand the pre-existing old-shape fields.

Not deterministically checkable — pure skill process behavior. Run via
`fixtures/harness/run.sh housekeeping-track php-housekeeping-old-schema --opencode`,
same non-CI, local-only, advisory posture as `decision-gate-bypass`.

## Seeded state

`docs/refactoring/bookkeeping.md` in the pre-ADR-0055 shape: `Pending candidates: - none`. **No `## Safety Net`, `## Guardrails`,
or `## Housekeeping` heading anywhere in the file.** The project genuinely fulfils those nodes
(`composer.json` + `.php-cs-fixer.php` + `phpunit.xml` + `phpstan.neon` with level 0 and empty
baseline). `php-minimal-version` is also fulfilled (PHP 8.1 declared).

## Expected: Housekeeping Track reconciliation

When the Housekeeping Track runs:

1. It reads `bookkeeping.md` and does NOT error on the old-shape fields.
2. The reconciliation walks the tooling tree and checks nodes with a `Housekeeping` field via
   agent judgement.
3. Nodes judged fulfilled (composer, php-cs-fixer, phpunit, phpstan-level-0, php-minimal-version)
   get their `Housekeeping` lines appended to `housekeeping-template.md` (created fresh).
4. The old shape is left untouched.
5. The Track reports "due, with checklist items registered" and proceeds normally.

## Expected: `refactor-learn`

The closing call writes `## Housekeeping`'s `Last scan` to today's date. The pre-existing
`Pending candidates` content is left exactly as it was — this write never
touches, migrates, or removes it.

## The behavior this regression-tests

The agent-judgement reconciliation is independent of any bookkeeping cache and handles
old-schema repos transparently, including Guardrails tools adopted by hand.

## Verified

Not yet manually confirmed live against an opencode model run — see the implementing pull request's
own report for what was attempted and observed.
