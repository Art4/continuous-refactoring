# 05 — Roave BC Check and the BC-safe Type Coverage path

Type: task
Status: done
Blocked by: 02, 04

**What to build** (ADR-0088)

- **Roave.** Role `api-compatibility` (API Compatibility, no Signal) in `roles.json`; Tool `roave-bc-check`, recommended,
  in `packs/php/pack.json`, one Safety Net Stage: `requires: composer`, `waits_for: ci-runner`, *Applies when*: the BC
  promise follows SemVer and the repository has at least one SemVer tag. `packs/php/roave-bc-check.md`: Purpose,
  Fulfilment check (a CI job runs `roave-backward-compatibility-check`), MR scope, why it stands before the rewriters.
- **Verify before writing:** Roave's minimum PHP (for `min_runtime`); whether dev-dependency conflicts make the Docker
  image the default; that CI fetches tags (`fetch-depth: 0`); how a next-major branch ignores intended breaks; how Roave
  reads calendar tags such as `2026.05` (the Stage does not apply to an application with calendar tags, but the check should not crash on them).
- **`rector-type-coverage`** waits for `roave-bc-check`, and gets a second path in `rector.md`: `rector-bc-library`
  (`Set::BC_TYPE_DECLARATION`, `Set::withTypeCoverageLevel(n)`) when the promise covers extending and overriding
  non-final classes and methods; Rector's own set otherwise. Point at the package's README for the Rector versions it
  supports; do not copy its table.
- `docs/FAQ.md`: why Roave only for a SemVer promise; regenerate `docs/tooling/`.

**Done when** a fixture target with a SemVer promise and a tag gets the Roave Stage in the Safety Net, one with a
promise counted in time and releases does not, `rector-type-coverage` waits for it, and tests and validator are green.

## Comments

> **2026-10-24:** Done. Verified from Roave's README and Packagist: base release found only in `x.y.z` tags; tags must be fetched; autoload must cover the sources; intended breaks go into `<ignored-regex>` entries. Oldest versions ran on PHP 7.2, but the Stage installs through the Docker image or Action, so no `min_runtime` (as Semgrep). An unsettled promise takes the BC-safe Rector path. Side note: rector-bc-library's README has two typos (`typeDeclaraion:` for `typeDeclarations:`, `>withRules` missing a `-`).
