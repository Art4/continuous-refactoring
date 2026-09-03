# 19 — Merge-request outlook and typed rationale

**Type:** grilling + task

**What to build:** What a suite **merge request** says beyond the plain description in ticket 12 / ADR-0006 (candidate link, what changed, tests, CI). Ticket 12 explicitly does **not** include this. The 12 grilling deferred two questions together: whether the description **must end with an outlook** (what the candidate unlocks short/mid-term — next tooling-tree child or next deepening; ADR-0005 already talks as if it does), and whether a **closed type enum** names the quality dimension (brainstorming G–J plus first-wave kinds). Decide, then put the result where skills write the merge-request body.

**Blocked by:** 12 ✓ done — Deliver each candidate as a remembered merge request

**Status:** done

Grill until settled, then specify:

- [x] Outlook: only on tooling-tree candidates, not structural ones (ADR-0009)
- [x] If outlook: shape = next child only, computed by re-running `scripts/lib/tooling_tree.py` against the changed working tree; lives at the end of the merge-request description (ADR-0009)
- [x] Type enum: closed list vs one-sentence dimension vs omitted — **omitted** (ADR-0027)
- [x] If an enum: the list — N/A, no enum
- [x] ADR-0005’s “outlook names the child” fulfilled (ADR-0009)
- [x] Skills/orchestrator updated to the outlook decision (`skills/continuous-refactoring/SKILL.md`, ADR-0009; `opening-a-merge-request.md`, ADR-0027)

## Comments

> **2026-08-21:** Split from the 12 grilling (Q13). Do not treat “outlook Pflicht, kein Enum” as already decided — that was the recommendation, not the answer.

> **2026-08-26:** Outlook half decided and implemented — ADR-0009. Turned out the recommendation from the 2026-08-21 split *was* the answer for the outlook question specifically (only tooling-tree candidates, next-child shape), reached independently while fixing unrelated friction found in the first real end-to-end pass. Type enum remains genuinely undecided; re-open this ticket for that half alone.

> **2026-09-03:** Type-enum half grilled (`/grill-me zu Ticket 19`) — **no type enum**. The
> sentence's plain-language opener (ADR-0009) already covers most of what a type would have named,
> for less ongoing cost than maintaining a closed vocabulary. Along the way, the same session found
> and settled a real gap in the outlook *sentence* itself (it names only one of often-several
> siblings a candidate unblocks at once) — split out as its own ticket, 47, since it's a genuinely
> new addition to ADR-0009's mechanism, not the type-enum question this ticket was about. Recorded
> in `docs/adr/0027-mr-outlook-diagram-of-unblocked-nodes.md`. Ticket 19 closes.
