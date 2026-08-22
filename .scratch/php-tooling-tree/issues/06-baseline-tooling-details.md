# 06 — Decide the baseline tooling details (grilling)

**Type:** grilling

**What to build:** A decision, reached by a `/grilling` session, on the open baseline-tooling questions deferred from the suite design session (Q13): dependency pinning, PHPStan / Rector levels, and which additional tools (if any) belong in the baseline basket beyond php-cs-fixer, Rector, and PHPStan. The grilling explicitly weighs the goal's missing dimensions as candidates: a test-coverage floor (08), mutation testing (09), a dependency vulnerability scan (10), an OWASP-aware static security pass (11), secret detection (13), and a nightly DAST pass (14), plus dependency-hygiene tools (composer-unused, composer-normalize). The outcome lands as an ADR in `docs/adr/` so the `refactor-baseline` skill can reference concrete defaults.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] Grilling session held; each open tooling question decided
- [x] Coverage floor, mutation testing, dependency scan, OWASP static analysis, secret detection, and DAST each decided — in the basket or explicitly out, with concrete defaults
- [x] Outcome recorded as an ADR in `docs/adr/`
- [x] `refactor-baseline` updated to reference the concrete defaults where applicable — **superseded:** there is no baseline skill; ADR-0005 retires `/refactor-baseline`. Skill/playbook edits are follow-up, not this ticket.

## Comments

> **Brainstorming input — extended tooling (2026-08-20):** candidate tools and OWASP Top 10 mapping for the grilling session. See tickets 08–14 for where each lands.

**SAST:** Psalm Taint Analysis (A03 Injection, A01, A02 — follows data paths input → output: SQLi, XSS, path traversal) · Semgrep (Top 10 largely covered, OWASP rulesets, flexible) · PHPCS Security Audit (A02, A03, A05) · progpilot (PHP taint analyzer, A03)

**Secret detection (often forgotten):** gitleaks (secrets/API keys/tokens in code + git history) · truffleHog (git-history credentials) · detect-secrets (prevents committing secrets)

**Dependency security beyond composer audit:** OWASP Dependency-Check (broader CVE check) · Trivy (dependencies + container images) · Snyk (deps + code, free tier) · local-php-security-checker (lightweight)

**DAST (nightly, not per-MR):** OWASP ZAP (automated pentest, needs running instance) · Nuclei (template-based, active community)

**OWASP Top 10 mapping:** A01 Access Control → Arkitect, Deptrac, Semgrep · A02 Crypto Failures → Semgrep, PHPCS Security Audit · A03 Injection → Psalm Taint Analysis ⭐, Semgrep · A04 Insecure Design → Arkitect, Deptrac, PHPStan · A05 Misconfiguration → Semgrep, PHPCS Security Audit · A06 Vulnerable Components → composer audit, Trivy, OWASP Dep-Check · A07 Auth Failures → Semgrep (limited), manual · A08 Software Integrity → gitleaks, truffleHog · A09 Logging Failures → Semgrep (custom rules) · A10 SSRF → Psalm Taint Analysis, Semgrep

**Overall tooling order (brainstorming):** composer audit → OWASP Dependency-Check → gitleaks/detect-secrets → composer-unused → composer-normalize → PHP-CS-Fixer → Rector → PHPUnit + PCOV → PHPStan/Psalm → Psalm Taint Analysis ⭐ → Semgrep → PHPCS Security Audit → PHPMD/Arkitect/Deptrac → Infection → OWASP ZAP/Nuclei (nightly)

**Extended MR types:** G — Psalm taint findings · H — Semgrep OWASP violations · I — secret/credential cleanup · J — vulnerable dependency update

**Tool dependency trees:** the baseline order must respect what each tool needs first — a tool's dependencies must exist before it (PHPStan, Rector, and PHPUnit all depend on Composer being introduced first):

- **Tree 1 — PHP + Composer root:** PHP runtime → Composer → the Composer-based stack: PHP-CS-Fixer · Rector · PHPStan (+ security extension) · Psalm (+ taint plugin) · PHPUnit + PCOV · PHPCS Security Audit · PHPMD · Arkitect/Deptrac · Infection · composer audit · local-php-security-checker · composer-unused · composer-normalize.
- **Tree 2 — Standalone binaries (no Composer):** gitleaks · truffleHog · detect-secrets (Python) · Semgrep (Python/Docker) · Trivy · Nuclei · OWASP Dependency-Check (Java runtime).
- **Tree 3 — Runtime/instance-dependent:** OWASP ZAP (running app + Java) · DAST generally → deployed instance → nightly pipeline, never a per-MR gate.

The tooling order emerges from these trees: Composer first, then the Composer stack, standalone binaries independent of it, DAST last (nightly).

> **2026-08-21:** Grilled. The “baseline basket” framing was replaced: no `/refactor-baseline`, git-only hard requirement, PHP **tooling tree**, suite state under `docs/refactoring/`. Recorded as ADR-0005 (amends ADR-0002, path part of ADR-0001). PHPStan child sequence specified in ticket 18. First wave: CI-runner, Composer, cs-fixer, Rector, PHPStan, composer audit, test-runner-if-missing. Later: 08 coverage, 09 mutation, 11 SAST, 13 secrets, 14 DAST, normalize/unused. Ticket 10 (audit) stays first-wave but as a thin node, not a CI-fail default. Skills and playbooks are not updated in this ticket.

> **2026-08-22:** Moved from `suite-self-containment/issues/` to `php-tooling-tree/issues/` — regrouped around the PHP tooling tree.
