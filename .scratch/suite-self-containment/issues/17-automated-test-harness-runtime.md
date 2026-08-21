# 17 — Automated test harness — Tiers 2–5: artifact contracts, ground truth, triggers, CI gate

**Type:** build

**What to build:** The runtime tiers of the suite harness, on top of the static validation tier (16).

## Grilling-Entscheidungen

| # | Entscheidung | Wahl |
|---|--------------|------|
| 1 | Infrastruktur | Eigenes Harness (opencode + Docker + Bash) |
| 2 | Scope | Tiers 2+3 zuerst, 4+5 später |
| 3 | Ground-Truth-Fixtures | 3-5 Fixtures |
| 4 | Artifact Contracts | Issue-Struktur + Config + MR-Chain |
| 5 | Script-Sprache | Bash |
| 6 | Sandbox-Modus | Docker-Container mit opencode |
| 7 | Assertion-Format | Exit-Code + stdout |
| 8 | Precision/Recall | Einfach (precision = found/expected, recall = found/planted) |
| 9 | Baseline-Speicherort | `fixtures/baselines/` |
| 10 | Commit-Struktur | Feature-Branch, eigene Commits pro Tier |

## Plan

**Feature-Branch:** `feature/test-harness-tiers-2-3`

**Abhängigkeiten:**
- 07 ✓ done — First loop pass validated
- 16 ✓ done — Tier 1 static validation
- 26 — Harness-Infrastruktur (Docker, Bash-Funktionen)

**Commits:**
1. Ticket 26: Harness-Infrastruktur
2. Tier 2: Artifact Contracts
3. Tier 3: Ground Truth + Fixtures

**Später (eigenes Ticket):**
- Tiers 4+5 (Trigger Tests + CI Gate)

## Checkliste

- [x] Harness decision made (grilling) and recorded
- [x] Ticket 26: Harness-Infrastruktur
- [x] Tier 2: artifact contract assertions over a sandboxed loop run
- [x] Tier 3: ground-truth repos + precision/recall score + saved baseline
- [ ] Tier 4: trigger tests incl. negative controls *(separates Ticket)*
- [ ] Tier 5: CI gate + rubric grading + lift measurement *(separates Ticket)*

## Comments

> **2026-08-20:** Split off from ticket 16 — the runtime tiers moved here; Tier 1 (static suite validation) stays in 16.

> **2026-08-21:** ADR-0005 retires the baseline marker. Tier 4 negative control "orchestrator without a baseline marker must not refactor" is obsolete — replace with: without git, the suite must not run; missing tools are candidates, not a start-gate. `.out-of-scope/` assertions move to `docs/refactoring/`.

> **2026-08-21:** Grilling-Session abgeschlossen. Entscheidungen: eigenes Harness (Docker + Bash), Tiers 2+3 zuerst, 3-5 Fixtures, Exit-Code + stdout, Baseline in `fixtures/baselines/`.
