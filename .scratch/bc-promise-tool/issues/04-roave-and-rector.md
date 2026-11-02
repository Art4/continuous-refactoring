# 04 — Roave and Rector with the Tool

Type: task
Status: open
Blocked by: 02, 03

**What to build** (ADR-0093, spec Q18)

- **Roave.** `packs/php/pack.json`, `roave-bc-check`: no `requires` on `bc-promise`; `applies_when` keeps "an unsettled
  BC promise does not count" and applies to the part of the promise that covers the code `composer.json`'s `autoload`
  section names, when that part follows SemVer and a tag `x.y.z` exists. `roave-bc-check.md` follows.
- **Rector.** `rector.md`, `rector-type-coverage`: the BC-safe path taken only because the promise is not settled is
  an Opener of `bc-promise` (ticket 01's plan line).
- `bc-promise.md`'s Opener names both places: `principles.md` and `rector.md`.
- Docs: `docs/tooling/packs/php.md` regenerated.
- Changelog fragment.

**Done when** the parser, given an unsettled promise, keeps `rector-type-coverage` workable (no Stage held by
`bc-promise`), a walk-through of `rector-type-coverage` on an unsettled target writes the Opener, and tests and
validator are green.
