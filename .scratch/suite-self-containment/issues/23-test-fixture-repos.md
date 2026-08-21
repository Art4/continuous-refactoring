# 23 — Test-Fixture-Repo-Infrastruktur

**Type:** grilling + build

**What to build:** Separates Repo `continuous-refactoring-fixtures` mit PHP-Test-Repos für die Suite-Validierung. Jedes Fixture ist ein eigenständiges Git-Repo, das einen bestimmten Zustand der Tooling-Tree repräsentiert.

**Grilling-Fokus:**
- Wie viele Fixtures brauchen wir wirklich?
- Welche Zustände sind für Issue 07 (erster Loop-Pass) kritisch?
- Reset-Strategie: git clean vs. Snapshot vs. Rebuild?
- Sollten Fixtures eigene Commits haben (History) oder flach sein?
- Wie testen wir Negative Controls (nicht-PHP)?

**Geplante Fixtures:**
1. `php-minimal/` – Kein Tooling, nur PHP-Dateien (erster Wave: alles fehlt)
2. `php-partial/` – Composer + CS-Fixer, aber kein PHPStan/Rector
3. `php-full/` – CI + Composer + alle Tools (nur Structural Candidates)
4. `non-php/` – Node/Python/Go für Negative Controls

**Blocked by:** —

**Status:** done

- [x] Grilling: Anzahl und Scope der Fixtures
- [x] Grilling: Reset-Strategie
- [x] Grilling: Struktur (eigene Git-Repos oder Unterverzeichnisse?)
- [ ] 24 — README für Tests-Repo
- [ ] 25 — Shell-Script für Fixture-Tests
- [x] Build: Repo erstellen (erledigt – existiert bereits)
- [x] Build: Fixtures anlegen (erledigt – php-project-with-candidates existiert)
- [ ] Build: Reset-Scripte/Docs

## Comments

> **2026-08-21:** Abgespalten von Issue 07 – Test-Fixtures werden eigenständig gepflegt. Issue 07 wird danach auf dieses Ticket verweisen.

> **2026-08-21:** Grilling-Session abgeschlossen. Tickets 24 (README) und 25 (Shell-Script) erstellt.
