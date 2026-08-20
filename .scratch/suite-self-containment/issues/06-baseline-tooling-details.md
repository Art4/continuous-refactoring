# 06 — Decide the baseline tooling details (grilling)

**Type:** grilling

**What to build:** A decision, reached by a `/grilling` session, on the open baseline-tooling questions deferred from the suite design session (Q13): dependency pinning, PHPStan / Rector levels, and which additional tools (if any) belong in the baseline basket beyond php-cs-fixer, Rector, and PHPStan. The grilling explicitly weighs the goal's missing dimensions as candidates: a test-coverage floor (08), mutation testing (09), a dependency vulnerability scan (10), an OWASP-aware static security pass (11), secret detection (13), and a nightly DAST pass (14), plus dependency-hygiene tools (composer-unused, composer-normalize). The outcome lands as an ADR in `docs/adr/` so the `refactor-baseline` skill can reference concrete defaults.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Grilling session held; each open tooling question decided
- [ ] Coverage floor, mutation testing, dependency scan, OWASP static analysis, secret detection, and DAST each decided — in the basket or explicitly out, with concrete defaults
- [ ] Outcome recorded as an ADR in `docs/adr/`
- [ ] `refactor-baseline` updated to reference the concrete defaults where applicable

## Comments

> **Brainstorming input — extended tooling (2026-08-20):** candidate tools and OWASP Top 10 mapping for the grilling session. See tickets 08–14 for where each lands.

**SAST:** Psalm Taint Analysis (A03 Injection, A01, A02 — follows data paths input → output: SQLi, XSS, path traversal) · Semgrep (Top 10 largely covered, OWASP rulesets, flexible) · PHPCS Security Audit (A02, A03, A05) · progpilot (PHP taint analyzer, A03)

**Secret detection (often forgotten):** gitleaks (secrets/API keys/tokens in code + git history) · truffleHog (git-history credentials) · detect-secrets (prevents committing secrets)

**Dependency security beyond composer audit:** OWASP Dependency-Check (broader CVE check) · Trivy (dependencies + container images) · Snyk (deps + code, free tier) · local-php-security-checker (lightweight)

**DAST (nightly, not per-MR):** OWASP ZAP (automated pentest, needs running instance) · Nuclei (template-based, active community)

**OWASP Top 10 mapping:** A01 Access Control → Arkitect, Deptrac, Semgrep · A02 Crypto Failures → Semgrep, PHPCS Security Audit · A03 Injection → Psalm Taint Analysis ⭐, Semgrep · A04 Insecure Design → Arkitect, Deptrac, PHPStan · A05 Misconfiguration → Semgrep, PHPCS Security Audit · A06 Vulnerable Components → composer audit, Trivy, OWASP Dep-Check · A07 Auth Failures → Semgrep (limited), manual · A08 Software Integrity → gitleaks, truffleHog · A09 Logging Failures → Semgrep (custom rules) · A10 SSRF → Psalm Taint Analysis, Semgrep

**Overall tooling order (brainstorming):** composer audit → OWASP Dependency-Check → gitleaks/detect-secrets → composer-unused → composer-normalize → PHP-CS-Fixer → Rector → PHPUnit + PCOV → PHPStan/Psalm → Psalm Taint Analysis ⭐ → Semgrep → PHPCS Security Audit → PHPMD/Arkitect/Deptrac → Infection → OWASP ZAP/Nuclei (nightly)

**Extended MR types:** G — Psalm taint findings · H — Semgrep OWASP violations · I — secret/credential cleanup · J — vulnerable dependency update
