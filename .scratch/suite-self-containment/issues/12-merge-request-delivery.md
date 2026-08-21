# 12 — Deliver each candidate as a remembered merge request

**What to build:** The orchestrator implements ADR-0006. After review, Learn opens a **merge request** for the completed **candidate** (or obtains its URL in `human-opens` / `ask-each-time` mode), remembers it under `docs/refactoring/`, and sets the candidate `ready-for-human`. Every **loop pass** starts from that remembered state: respond to comments; record merge as `done`; on close-without-merge derive out-of-scope + `wontfix` or ask the human. At most two suite merge requests are open. Description is plain (candidate link, what changed, surviving tests, what CI proves) — no outlook, no type enum (ticket 19). Self-contained: no global skill for the forge.

**Blocked by:** 05 ✓ done — Make the orchestrator degrade gracefully

**Status:** in-progress

- [ ] Pass starts from remembered suite merge requests (only those count toward the cap)
- [ ] Completed candidate → one branch, one merge request; URL stored under `docs/refactoring/`; issue `ready-for-human` (not `done`)
- [ ] Open + comments → follow-up commits; that pass starts no new candidate
- [ ] Merged → issue `done`; bookkeeping-only may still take one new candidate if a slot is free
- [ ] Closed without merge → `wontfix` + out-of-scope from comments, or ask the human
- [ ] Two open → point the human at them; no third; still respond to comments
- [ ] Second merge request: stack only for a tooling-tree child or explicit design dependency; else parallel on the default branch; retarget/rebase after parent merge
- [ ] Create-mode: read `AGENTS.md` / `CLAUDE.md`; else propose `autonomous`; remember `autonomous` | `ask-each-time` | `human-opens` in suite state — never write those agent docs
- [ ] Description: candidate link, what changed, tests, CI — not outlook, not types
- [ ] Atomic commits following the target repo’s convention; skills say merge request, chat uses the forge’s word
- [ ] Works self-contained (no global-skill dependency)

## Comments

> **2026-08-21:** Grilled (grill-with-docs). Recorded as ADR-0006. Outlook and typed rationale split to ticket 19. Original “pass closes when the MR exists / issue done / chain ≤ 2 as a pass quota / letter types G–J” superseded.
