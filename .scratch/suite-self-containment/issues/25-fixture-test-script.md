# 25 — Shell-Script für Fixture-Tests

**What to build:** Ein Shell-Script `scripts/run-test.sh`, das Fixture-Tests automatisiert. Das Script支持t verschiedene Modi: setup, test, clean und auto (alles in einem Durchgang).

**Blocked by:** None — kann sofort starten

**Status:** done

- [x] `scripts/run-test.sh` mit Modi: setup, test, clean, auto
- [x] `setup`: Fixture aus `fixtures/` → /tmp/ kopieren, git init, git commit
- [x] `test`: Docker-Container mit variabler PHP-Version starten
- [x] `clean`: Temporäre Dateien aufräumen
- [x] `auto`: setup → test → clean in einem Durchgang
- [x] Exit-Code + Output für CI und manuelle Nutzung

## Comments

> **2026-08-21:** Abgespalten von Issue 23 (Test-Fixture-Repo-Infrastruktur).

> **2026-08-21:** Fixtures ins Hauptrepo verschoben (nicht mehr separates Repo).

> **2026-08-21:** Script aus `continuous-refactoring-tests/` kopiert und angepasst.
