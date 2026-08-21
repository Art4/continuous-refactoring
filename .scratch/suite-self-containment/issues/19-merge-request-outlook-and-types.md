# 19 — Merge-request outlook and typed rationale

**Type:** grilling + task

**What to build:** What a suite **merge request** says beyond the plain description in ticket 12 / ADR-0006 (candidate link, what changed, tests, CI). Ticket 12 explicitly does **not** include this. The 12 grilling deferred two questions together: whether the description **must end with an outlook** (what the candidate unlocks short/mid-term — next tooling-tree child or next deepening; ADR-0005 already talks as if it does), and whether a **closed type enum** names the quality dimension (brainstorming G–J plus first-wave kinds). Decide, then put the result where skills write the merge-request body.

**Blocked by:** 12 — Deliver each candidate as a remembered merge request

**Status:** ready-for-agent

Grill until settled, then specify:

- [ ] Outlook: required on every suite merge request, only on tooling-tree candidates, or not used
- [ ] If outlook: exact shape (next child, next deepening, both) and where it lives in the description
- [ ] Type enum: closed list vs one-sentence dimension vs omitted
- [ ] If an enum: the list (do not silently keep G–J; first-wave nodes need names if types exist)
- [ ] ADR-0005’s “outlook names the child” either fulfilled or amended
- [ ] Skills/orchestrator updated to the decision (after 12’s delivery machinery exists)

## Comments

> **2026-08-21:** Split from the 12 grilling (Q13). Do not treat “outlook Pflicht, kein Enum” as already decided — that was the recommendation, not the answer.
