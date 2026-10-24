# on-request-tools-and-bc-promise

Three changes to what the suite proposes, grilled on 2026-10-24 (`/grill-with-docs`). Decisions are recorded in
ADR-0086 (Tools on request), ADR-0087 (Rector stops at the declared PHP floor) and ADR-0088 (The BC promise); this
spec cuts them into tickets.

## Why

- **Semgrep is noise on young projects.** It finds little in code written under guardrails and pays off in old code.
  Mutation testing is expensive and worth it only with a good test suite. Neither belongs in every target's backlog;
  both should be available on request.
- **Composer Audit is maintenance, not a guardrail.** Its value is in repetition, which a CI gate cannot give.
- **`php-minimal-version` legitimises a Floor raise.** A Rector PHP set above the declared floor already made the code
  need a newer PHP; the Stage then wrote that into `composer.json` under the refactor label.
- **The suite cannot tell a project with a promise to outside code from one without.** Friendica (an application with
  addons, calendar tags, a deprecation path in time and releases) shows that "library" is the wrong cut.

## Decided

| # | Decision | ADR |
|---|---|---|
| Q1 | A third Tool status `on-request`; no Track for extras. Its Stages make no scan due and count towards their Track only once one has a ticket | 0086 |
| Q2 | Semgrep and Psalm Taint Analysis are on request; Secret Detection stays recommended | 0086 |
| Q3 | Composer Audit leaves the tree: a standard task in the first Housekeeping template, for any package manager; Stage and Role Dependency Audit go | 0086 |
| Q4 | Infection is part of this plan and replaces `.scratch/php-tooling-tree/issues/09` | 0086 |
| Q5 | `rector-php-set` targets the declared floor and no higher; `php-minimal-version`, Role Runtime Floor and the term Floor correction go | 0087 |
| Q6 | The term **BC promise** (text below) | 0088 |
| Q7 | Recorded as an optional operation **BC promise** in `## Refactoring operations` | 0088 |
| Q8 | Roave BC Check is a Safety Net Stage, applies only to a SemVer promise with at least one SemVer tag | 0088 |
| Q9 | `after` is renamed `waits_for` | 0086 |
| Q10 | Secret Detection is out of this plan | — |
| Q11 | On request by naming the Tool in the call, by a scan "including on-request Tools", and a line in every scan report | 0086 |
| Q12 | Composer Audit: an existing CI job stays; an open `composer-audit` ticket is closed with a note | 0086 |
| Q13 | `rector-php-set` fulfilled when its level equals the floor; a later raise reopens it; code already above the floor is an ordinary ticket | 0087 |
| Q14 | The operation names a path or `none`; its absence means not settled yet | 0088 |
| Q15 | Settled in the onboarding interview, or by the onboarding step of the next run; autonomous runs write only an unambiguous path, never a guessed `none`, and act as if a promise exists meanwhile | 0088 |
| Q16 | `principles.md`: covered code by Strangler Fig only; the suite may hard-deprecate by the promise's procedure; removal is an ordinary ticket | 0088 |
| Q17 | `rector-bc-library` is a second path in `rector-type-coverage`, taken when the promise covers extending non-final classes and methods | 0088 |
| Q18 | No Housekeeping task for deprecations: the target's own work | 0088 (rejected option) |
| Q19 | Roave: Tool `roave-bc-check` (recommended), Role API Compatibility, Safety Net, `requires: composer`, `waits_for: ci-runner`; `rector-type-coverage` waits for it | 0088 |
| Q20 | Infection: on request, Role Mutation Testing with Signal *Untested / hard-to-test*, Guardrails, `waits_for: coverage-floor`; CI on changed files, the full run a Housekeeping line | 0086 |
| Q21 | Infection requires the Role Testing, not the Stage `phpunit`; Pest's built-in mutation testing is a recognized Tool of the same Role | — |
| Q22–24 | Three ADRs; this design PR holds ADRs and tickets, `CONTEXT.md` changes ride with the tickets; order as below | — |

## Facts

- Pest runs on PHPUnit's engine and fulfils the `phpunit` Stage today (`phpunit.md`). Infection drives a test framework
  through an adapter (PHPUnit built in; PhpSpec, Codeception, Pest via `testFramework: "pest"`) and needs a coverage
  driver. Pest 3 has mutation testing of its own (`pest --mutate`, `--min`), scoped by `covers()` / `mutates()`.
- `## Refactoring operations` already holds one bullet that is not a tracker operation: **Tooling Pack**.
- Housekeeping's scan over the Git history reads the scanner Secret Detection sets up — the reason Q10 is out.

## Not in this plan

- **Secret Detection.** Its placement feels off to the user; any change touches Housekeeping's history scan.
- **Deprecation upkeep** (Q18).

## Tickets

1. `01-rector-stops-at-the-floor` — Floor cleanup
2. `02-waits-for` — `after` → `waits_for`
3. `03-tools-on-request` — the status, Semgrep and taint on request, Composer Audit to Housekeeping (blocked by 02)
4. `04-bc-promise` — the operation, onboarding, `principles.md`
5. `05-roave-and-bc-type-coverage` — Roave and the `rector-bc-library` path (blocked by 02, 04)
6. `06-infection` — Infection and Pest's mutation testing (blocked by 02, 03)

Every ticket keeps the docs in sync in its own PR (`AGENTS.md`, *Docs stay in sync*), regenerates
`docs/tooling/` with `python3 scripts/tooling_docs.py`, adds a changelog fragment, and runs
`python3 -m unittest discover -s scripts -p 'test_*.py'` and `python3 scripts/validate_skills.py .` green before pushing.
