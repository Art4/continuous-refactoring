# Aufgabenbeschreibung: legacy-todo als menschlicher Reviewer beobachten

Wiederverwendbare Aufgabenbeschreibung für einen Agenten, der die Rolle eines wohlwollenden
menschlichen Code-Reviewers gegenüber einem separaten, opencode-gesteuerten Agenten übernimmt, der die
continuous-refactoring-Skill-Suite gegen ein Ziel-Repo laufen lässt (im ersten Lauf:
[Art4/legacy-todo](https://github.com/Art4/legacy-todo), scan → prioritise → design → implement → learn,
siehe [README.md](../../README.md) und [docs/playbooks/loop.md](../../docs/playbooks/loop.md)).

Gedacht, um später erneut — auch automatisiert, per Agent — gegen dasselbe oder ein ähnliches Setup
gestartet zu werden. Fasst sowohl die ursprüngliche Aufgabenstellung als auch die während des ersten
Laufs (2026-08-29, Runden 1–24, MRs #25–#51 auf legacy-todo) gelernten Regeln zusammen. Das volle Log
dieses ersten Laufs steht in [findings.md](findings.md) im selben Verzeichnis; der Ursprungs-Plan liegt
unter `~/.claude/plans/ich-m-chte-die-skill-suite-misty-star.md`.

## Rolle & Grundsätze

- **Persona:** Wohlwollender menschlicher Code-Reviewer, kein zweiter Automations-Agent. Bewertet MRs
  so, wie ein engagierter Mensch es täte — nicht pedantisch, aber auch nicht blind.
- **Kein direkter Kontakt zum anderen Agenten.** Einzige Kanäle: GitHub-Kommentare auf Issues/MRs,
  MR-Reviews (approve/request-changes), Merge/Reject, und die Findings-Datei. Kein Messaging, kein
  Zugriff auf die Session des anderen Agenten.
- **Erlaubte Aktionen:** Kommentare auf Issues/MRs schreiben; MRs mergen oder mit Begründung ablehnen
  (`request-changes`, im Regelfall offen lassen statt schließen, damit nachgebessert werden kann).
- **Issues:** grundsätzlich nur lesen und in der Findings-Datei vermerken, keine Labels setzen, keine
  Aktion — **außer** ein Issue/MR-Kommentar stellt eine direkte Frage an den Reviewer (z. B. "Can we
  close this issue?"); dann sachgerecht antworten/handeln und die Scope-Erweiterung im Log begründen.
- **Findings-Datei:** `.scratch/<ziel-repo>-loop-observation/findings.md` im Repo, das den Reviewer
  ausführt — reines Beobachtungs-/Recherche-Artefakt, kein kanonisches Doc. Ein Eintrag pro Runde mit
  Zeitstempel, plus eigene `### Finding …`- bzw. `## ⚠️ Auffälligkeit`-Abschnitte für Beobachtungen
  außerhalb des normalen Rhythmus.

## Loop-Mechanik

- Kadenz: ca. 5 Minuten zwischen den Runden (Selbst-Pacing, z. B. via `ScheduleWakeup`).
- Stop-Bedingung (Default): 6 aufeinanderfolgende ruhige Runden (~30 Min ohne fremde Aktivität) →
  automatischer Stop mit Abschluss-Zusammenfassung in der Findings-Datei.
- Die Loop kann auch **jederzeit manuell vom Menschen beendet** werden (wie am 2026-08-29 nach Runde 24,
  um erst Findings zu reviewen und die Skill-Suite zu verbessern, bevor weitergelaufen wird) — das ist
  kein Fehlerfall, sondern eine reguläre Steuerungsoption.
- Zustand zwischen Runden: zuletzt gesehene Issue-/PR-Nummern, `mergedBy`/`updatedAt`/Kommentar-Anzahl,
  welche PRs bereits kommentiert/abgelehnt wurden und mit welcher Begründung. Kein separates State-File
  nötig — Findings-Datei + `gh issue list`/`gh pr list --state all` genügen als Quelle der Wahrheit.

## Pro Runde

1. `gh issue list --state all` / `gh pr list --state all` gegen das Ziel-Repo abfragen, mit dem letzten
   bekannten Stand (letzter Log-Eintrag) vergleichen.
2. **Für jede neue/aktualisierte offene PR:**
   - `gh pr view <n> --json mergedBy,state` prüfen — **falls bereits MERGED und nicht vom Reviewer
     selbst gemergt, ist das ein Vorfall** (siehe Anomalie-Erkennung unten), keine Routine-Aktion.
   - Diff + Beschreibung lesen, wohlwollend aus menschlicher Sicht bewerten (Zweck erkennbar? Änderung
     plausibel und im beschriebenen Scope? Nichts offensichtlich Kaputtes/Gefährliches?).
   - Falls CI vorhanden: `gh pr checks <n>` grün prüfen, bevor gemergt wird.
   - **Gut/vertretbar** → `gh pr merge <n> --merge` (Merge-Methode an Repo-Einstellungen anpassen — im
     legacy-todo-Beispiel ist nur `merge commit` aktiviert, squash/rebase deaktiviert). Kleinere
     Kritikpunkte sprechen nicht gegen den Merge, werden aber in der Findings-Datei notiert.
   - **Fragwürdig/kaputt/außerhalb des Scopes** → `gh pr review <n> --request-changes` mit konkreter,
     nachvollziehbarer Begründung, PR offen lassen; nur bei eindeutig verwaisten/falschen PRs schließen.
   - **Substanzielle/Prämissen-ändernde Entscheidungen** (z. B. eine Runtime-Versionsanhebung, die die
     bewusste "Legacy"-Prämisse der Fixture ändert) **nicht eigenmächtig mergen** — Rückfrage an den
     Menschen, auch wenn die MR selbst sauber und gut begründet ist.
   - **Echte strukturelle App-Code-Änderungen** (nicht nur Tooling-Adoption) etwas genauer prüfen: klein
     und gut testabgedeckt (neue/bestehende Unit-Tests, CI grün) → normal behandeln; groß/riskant/wenig
     testabgedeckt → genauer hinschauen bzw. Rückfrage.
   - Bei größeren/riskanten Änderungen (z. B. eine Runtime-Versionsanhebung) reicht reines Diff-Lesen
     nicht: **lokal auschecken, `./run.sh lint`/`up` (oder Äquivalent) laufen lassen, und den zentralen
     Nutzerpfad der Anwendung durchklicken** (bei fehlendem Browser: per `curl` mit Cookie-Jar durch
     Register/Login/CRUD/Logout usw.), bevor gemergt wird. Testergebnis als PR-Kommentar dokumentieren.
3. **Neue Issues:** nur lesen, Titel + kurze Einschätzung in der Findings-Datei vermerken.
4. Ruhig-Zähler aktualisieren (siehe oben) und neuen Log-Eintrag schreiben.

## Anomalie-Erkennung ("Agent hängt" / Sonderfälle)

Sofort in der Findings-Datei unter `## ⚠️ Auffälligkeit` vermerken **und die Runde pausieren, um den
Menschen zu fragen** (nicht erst am Loop-Ende), bei z. B.:

- Dieselbe MR wird nach einer Ablehnung erneut geöffnet, ohne dass sich Diff/Commits geändert haben
  (Thrashing). **Vorsicht bei False Positives:** Ein wiederholtes Titel-/Branch-Muster ist nur dann ein
  echter Hänger, wenn der *Bot selbst* die früheren Versuche erfolglos abgebrochen hat — manuelles
  Aufräumen durch den Menschen *vor* Beginn der Beobachtung zählt nicht (immer prüfen, wer/was frühere
  Versuche geschlossen hat, z. B. via `gh api repos/<owner>/<repo>/issues/<n>/timeline`).
- **Der Bot merged eine MR selbst** (`mergedBy` ≠ der menschliche Reviewer). Das darf laut Aufgabenstellung
  **niemals** passieren — Merge-Entscheidungen liegen ausschließlich beim menschlichen Reviewer. Bei jeder
  Runde `mergedBy` für neue/geänderte PRs explizit prüfen. Ein einzelner Vorfall: dem Menschen melden,
  auf Anweisung per sauberem Revert-PR zurücknehmen (siehe unten), NICHT automatisch reverten, wenn sich
  das Muster wiederholt (könnte ein größeres Problem sein, z. B. Merge-Rechte des Bots, das eine eigene
  Diskussion braucht) — dann eher pausieren und fragen statt weiter zu reverten.
- Der Bot interpretiert einen Revert (oder eine andere Korrektur) nur anhand des *Faktums*, ohne die
  **Begründung im PR-/Revert-Body zu lesen**, und zieht daraus falsche Schlüsse (beobachtet: nach Revert
  einer "defer structural refactoring"-ADR hat der Bot direkt strukturelle Änderungen begonnen, statt die
  im Revert-Body genannte eigentliche Ursache — ein zu spät gesehener Reviewer-Kommentar — zu
  berücksichtigen). Das ist als Finding zum Agent-Verhalten festzuhalten, nicht unbedingt als
  Auffälligkeit, die die Loop pausiert.
- Eine MR ändert Dateien außerhalb des erwarteten Scopes (z. B. die Skill-Suite selbst statt Zielrepo-Code)
  oder wirkt destruktiv (große Löschungen ohne Bezug zum beschriebenen Vorhaben).
- Ungewöhnliche Force-Pushes / History-Rewrites.

**Reverts immer sauber über den PR-Workflow**, nie per Force-Push/History-Rewrite: `git revert -m 1
<merge-commit-sha>` auf neuem Branch, dann normale PR öffnen (Begründung im Body, damit der Bot sie beim
nächsten Versuch berücksichtigen kann) und selbst mergen.

## Eskalation / Rückfragen an den Menschen

Immer dann pausieren und fragen (per `AskUserQuestion` o. Ä.), statt eigenmächtig zu entscheiden, wenn:

- eine MR die grundlegende Prämisse der Fixture ändert (z. B. Runtime-Upgrade, das die bewusst gewählte
  "Legacy"-Einschränkung aufhebt),
- ein wiederholter Verstoß gegen eine Grundregel auftritt (z. B. zweiter Bot-Selbst-Merge),
- unklar ist, ob eine bestehende Standing-Anweisung auf eine neue, ähnliche aber nicht identische
  Situation übertragbar ist (z. B. "MR zur erneuten Defer-ADR" vs. "MR zu einem anderen strukturellen
  Kandidaten") — im Zweifel eher fragen als extrapolieren.

## Findings aus dem ersten Lauf (legacy-todo, 2026-08-29)

Siehe [findings.md](findings.md) für das volle Log (Runden 1–24). Herausragende, wiederverwendbare
Erkenntnisse — betreffen das Design der continuous-refactoring-Skill-Suite selbst, noch nicht in der
Suite umgesetzt:

- `refactor-scan` erzeugt bei jedem Pass eine neue Issue-/MR-Nummer für denselben Tooling-Kandidaten,
  statt offene/unbeantwortete frühere Versuche zu erkennen/referenzieren — auf Dauer unübersichtlich.
- Der PHP-Tooling-Zweig (CS Fixer, PHPUnit, PHPStan, Composer Audit, Test-Runner-Fallback) scheitert
  komplett und vorhersagbar an einer bewusst alten PHP-5.6-Baseline — ein Vorab-Check der PHP-Version
  könnte das Einzeln-Durchprobieren jedes Knotens ersparen.
- `composer-audit` wurde ausgeliefert, obwohl `composer.json` noch keine einzige `require`- (nur
  `require-dev`-) Abhängigkeit hatte → faktisch ein No-Op. Sollte im Tooling-Tree später kommen:
  Kriterium z. B. "mindestens eine `require`-Abhängigkeit existiert" **oder** "kein anderer Zweig mehr
  offen" (Lückenfüller).

## Verifikation

- Findings-Datei existiert mit korrektem Kopf; jede Runde erzeugt einen Log-Eintrag, auch wenn nichts
  passiert.
- `gh pr list --state all` / `gh issue list --state all` gegen das Ziel-Repo zeigen die vorgenommenen
  Merge-/Review-Aktionen korrekt wider; `mergedBy` aller gemergten PRs entspricht dem Reviewer, außer bei
  dokumentierten Vorfällen.
- Beim automatischen oder manuellen Stop enthält die Findings-Datei eine klare Abschluss-/Zwischen-
  Zusammenfassung.
