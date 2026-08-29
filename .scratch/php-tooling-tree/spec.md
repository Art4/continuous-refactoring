# php-tooling-tree

Spec extracted from `suite-self-containment` (2026-08-22): all tickets that hang on the PHP **tooling tree** decided in ticket 06 and recorded in **ADR-0005** (`docs/adr/0005-tooling-tree-not-baseline-skill.md`) — the primary source for this feature.

The tree has three roots: Composer-based stack (PHP-CS-Fixer · Rector · PHPStan · PHPUnit + PCOV · composer audit …), standalone binaries (gitleaks · Semgrep · Trivy …), and runtime-dependent DAST (nightly only). First wave: CI-runner, Composer, cs-fixer, Rector, PHPStan, composer audit (thin), test-runner-if-missing. Later waves: coverage floor, mutation testing, SAST, secret detection, DAST, composer-normalize/unused.

> **2026-08-22:** Revised by ADR-0007 (`docs/adr/0007-required-recommended-edges.md`): edges are **required**/**recommended**; Rector leaves the first wave and becomes `rector-dead-code` / `rector-type-coverage` behind PHPStan levels. The canonical shape lives on **`docs/php-tooling-tree.md`**.

## Issues

| # | Ticket | Wave |
|---|--------|------|
| 06 | Tooling tree decision (ADR-0005) — done | root |
| 10 | Dependency vulnerability scan (composer audit child; CI-fail is a separate child node) | first |
| 18 | Specify the PHPStan adoption chain (introduce → CI job → shrink baseline → raise level) | first |
| 29 | Per-node Learnings entry, starting with `composer` (type-dependent lockfile, description derivation, vendor/ gitignore) | first |
| 30 | Extract node prose into per-node reference files, starting with `composer` | first |
| 08 | Test-coverage floor (PHPUnit child) | later |
| 09 | Mutation testing via Infection (PHPUnit child) | later |
| 11 | OWASP-aware static security analysis (SAST) | later |
| 13 | Secret detection (gitleaks / detect-secrets / truffleHog) | later |
| 14 | Nightly DAST (OWASP ZAP / Nuclei — needs a running instance) | later |

## Constraints carried over from ADR-0005

- Git-only hard requirement: without git, the suite must not run.
- Missing tools surface as `refactor:candidate` issues, never as a start-gate.
- Security tooling is entirely a later wave; do not propose DAST without a configured running instance.
- Only PHPStan gets the adoption-chain pattern; Rector / CS-Fixer / audit do not inherit it.

Numbering was kept from the original feature so cross-references in done tickets stay valid.
