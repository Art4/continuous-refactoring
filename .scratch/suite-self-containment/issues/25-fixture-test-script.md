# 25 — Shell-Script für Fixture-Tests

**What to build:** Ein Shell-Script `run-test.sh` im Repo `continuous-refactoring-tests/`, das Fixture-Tests automatisiert. Das Script支持t verschiedene Modi: setup, test, clean und auto (alles in einem Durchgang).

**Blocked by:** None — kann sofort starten

**Status:** ready-for-agent

- [ ] `scripts/run-test.sh` mit Modi: setup, test, clean, auto
- [ ] `setup`: Fixture → /tmp/ kopieren, git init, git commit
- [ ] `test`: Docker-Container mit variabler PHP-Version starten
- [ ] `clean`: Temporäre Dateien aufräumen
- [ ] `auto`: setup → test → clean in einem Durchgang
- [ ] Exit-Code + Output für CI und manuelle Nutzung

## Comments

> **2026-08-21:** Abgespalten von Issue 23 (Test-Fixture-Repo-Infrastruktur).
