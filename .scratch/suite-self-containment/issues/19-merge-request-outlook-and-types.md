# 19 — Merge-request outlook and typed rationale

**Type:** grilling + task

**What to build:** What a suite **merge request** says beyond the plain description in ticket 12 / ADR-0006 (candidate link, what changed, tests, CI). Ticket 12 explicitly does **not** include this. The 12 grilling deferred two questions together: whether the description **must end with an outlook** (what the candidate unlocks short/mid-term — next tooling-tree child or next deepening; ADR-0005 already talks as if it does), and whether a **closed type enum** names the quality dimension (brainstorming G–J plus first-wave kinds). Decide, then put the result where skills write the merge-request body.

**Blocked by:** 12 ✓ done — Deliver each candidate as a remembered merge request

**Status:** partially done — outlook decided (ADR-0009); type enum still open

Grill until settled, then specify:

- [x] Outlook: only on tooling-tree candidates, not structural ones (ADR-0009)
- [x] If outlook: shape = next child only, computed by re-running `scripts/lib/tooling_tree.py` against the changed working tree; lives at the end of the merge-request description (ADR-0009)
- [ ] Type enum: closed list vs one-sentence dimension vs omitted
- [ ] If an enum: the list (do not silently keep G–J; first-wave nodes need names if types exist)
- [x] ADR-0005’s “outlook names the child” fulfilled (ADR-0009)
- [x] Skills/orchestrator updated to the outlook decision (`skills/continuous-refactoring/SKILL.md`, ADR-0009) — type-enum half still pending

## Comments

> **2026-08-21:** Split from the 12 grilling (Q13). Do not treat “outlook Pflicht, kein Enum” as already decided — that was the recommendation, not the answer.

> **2026-08-26:** Outlook half decided and implemented — ADR-0009. Turned out the recommendation from the 2026-08-21 split *was* the answer for the outlook question specifically (only tooling-tree candidates, next-child shape), reached independently while fixing unrelated friction found in the first real end-to-end pass. Type enum remains genuinely undecided; re-open this ticket for that half alone.
