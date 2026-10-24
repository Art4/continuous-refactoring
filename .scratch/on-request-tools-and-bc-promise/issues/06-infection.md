# 06 — Infection and Pest's mutation testing

Type: task
Status: done
Blocked by: 02, 03

Replaces `.scratch/php-tooling-tree/issues/09-mutation-testing-in-loop.md`.

**What to build** (ADR-0086)

- Role `mutation-testing` (Mutation Testing, Signal *Untested / hard-to-test*) in `roles.json`.
- Tool `infection`, **on request**, one Guardrails Stage: `requires: testing` (the Role, so PHPUnit, Pest or another
  test framework that fills it), `waits_for: coverage-floor`. `packs/php/infection.md`: Purpose (tests judged by the
  mutants they kill, not by lines they reach), Fulfilment check (a CI job runs Infection), MR scope (CI on changed files
  only, `--git-diff-filter`; a coverage driver; `testFramework: "pest"` on a Pest project), the Ratchet (`--min-msi` /
  `--min-covered-msi`, only rising), Housekeeping line (the full run, escaped mutants weighed as candidates).
- Tool `pest-mutate`, **recognized**, same Role: Pest's built-in `pest --mutate`. Present (e.g. in CI), it fills the Role
  and Infection is *out*.
- The search for structural candidates reads escaped mutants as evidence for *Untested / hard-to-test* once the Role is
  filled (`signals.md`).
- Close `.scratch/php-tooling-tree/issues/09` with a pointer here.
- Docs: regenerate `docs/tooling/`; `docs/FAQ.md` if mutation testing needs a "why on request".

**Done when** a fixture target asking for Infection gets its Stage after `coverage-floor` is decided, a target with
`pest --mutate` in CI has the Role filled, and tests and validator are green.

## Comments

> **2026-10-24:** Done. `min_runtime` php 7.0 (Infection 0.1–0.2 required ^7.0; 0.35 needs ^8.3). Found while building: an unasked on-request Tool also stayed out of `runtime_blocked` — otherwise a scan would propose a runtime rejection for a Tool nobody asked for; fixed in the parser with a test. Old ticket `php-tooling-tree/09` closed.
