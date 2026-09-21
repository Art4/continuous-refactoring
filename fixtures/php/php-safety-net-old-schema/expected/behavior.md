# Expected behavior — old-schema `bookkeeping.md` pass-through

Confirms a target that adopted the suite before ADR-0055 — `Fulfilled nodes`/`Pending candidates`
already populated, no `## Safety Net` section at all — runs a normal Safety Net Track pass without
erroring on, migrating, or needing to understand the pre-existing old-shape fields
(`skills/continuous-refactoring/references/refactoring-bookkeeping.md`'s "Old-schema repos need no
migration" rule).

Not deterministically checkable — pure skill process behavior (does the pass proceed normally, does it
choke on an unrecognized field). Run via `fixtures/harness/run.sh safety-net-track
php-safety-net-old-schema --opencode`, same non-CI, local-only, advisory posture as
`decision-gate-bypass`.

## Seeded state

`docs/refactoring/bookkeeping.md` in the pre-ADR-0055 shape: `Fulfilled nodes` already lists
`onboarding-setup`, `composer`, `php-cs-fixer`, `phpunit` (no issue numbers — predates that convention),
`Pending candidates: - none`. **No `## Safety Net` heading anywhere in the file.** The project itself
matches: `composer.json` + `.php-cs-fixer.php` + `phpunit.xml` genuinely fulfill those four nodes, but
carries no `autoload.psr-4` mapping (`psr-4` unfulfilled — `src/Greeter.php` has no namespace at all,
a legacy flat layout) and no PHPStan/Psalm config (`static-code-analyzer`/`phpstan-level-0`
unfulfilled) — real, still-open Safety Net Track work exists here, this isn't a "nothing to do"
fixture.

## Expected: `refactor-scan` pass

Run `/refactor-scan`. It should:

1. Read `bookkeeping.md` without erroring on `Fulfilled nodes`/`Pending candidates` still being
   present in the old shape — nothing about reading them is invalid, they simply keep meaning what
   they already mean for every node outside the Safety Net Track's own scope (here: none of the four
   already-fulfilled nodes need re-proposing regardless of which field records them).
2. Find no `## Safety Net` section, treat the Track as due (never run), and walk its scope.
3. Propose `psr-4` and `static-code-analyzer`/`phpstan-level-0` (both genuinely still missing) as
   fresh Safety Net Track candidates — **not** `php-cs-fixer`/`phpunit` again (already fulfilled,
   confirmed by the parser directly against the filesystem, same as always — this fixture doesn't even
   need Fulfilled nodes to reach that conclusion).

## Expected: `refactor-learn`

Whichever candidate this pass actually carries through to completion (or, at minimum, the Track's own
scan completing) creates the `## Safety Net` section fresh — `Cadence: 90`, `Last scan: <today>`,
`Open` holding every unresolved node of the Safety Net scope in the script's order, blocked nodes
included, no issue numbers (see `php-guardrails-scan-fills-open` for the semantics). The pre-existing `Fulfilled
nodes`/`Pending candidates` content is left exactly as it was — this write never touches, migrates, or
removes it.

## The behavior this regression-tests

Without this rule, a target that adopted the suite before this change would either error out reading an
unfamiliar section, or need a one-time manual migration step before its next pass could run at all —
both of which ADR-0055 explicitly rejects ("No migration step").

## Verified

Not yet manually confirmed live against an opencode model run — see the implementing pull request's
own report for what was attempted and observed.
