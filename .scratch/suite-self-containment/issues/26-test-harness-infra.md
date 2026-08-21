# 26 — Test Harness Infrastruktur

**Type:** build

**What to build:** Gemeinsame Infrastruktur für das Test-Harness: Docker-Setup, Bash-Funktionen und Assertion-Helfer. Dies ist die Basis für Tiers 2+3.

**Blocked by:** 07 ✓ done — First loop pass validated, 16 ✓ done — Tier 1 static validation

**Status:** ready-for-agent

- [ ] Docker-Image für opencode + PHP erstellen
- [ ] Bash-Lib mit Assertion-Funktionen (`assert_issue_exists`, `assert_field_value`, etc.)
- [ ] Fixture-Setup-Script (Fixture → Docker mounten, opencode ausführen)
- [ ] CI-Skript für GitHub Actions

## Plan

**Feature-Branch:** `feature/test-harness-tiers-2-3`

**Dateien:**
- `fixtures/harness/Dockerfile` — opencode + PHP 8.3 + Composer
- `fixtures/harness/lib/assertions.sh` — Gemeinsame Bash-Funktionen
- `fixtures/harness/run.sh` — Haupt-Skript (Fixture laden, opencode ausführen, Assertions)
- `.github/workflows/test-harness.yml` — CI-Pipeline

## Comments

> **2026-08-21:** Abgespalten von Issue 17. Baut die Infrastruktur für Tiers 2+3.
