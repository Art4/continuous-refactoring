# 09 — Colliding terms

Type: task
Status: done
Blocked by: 05

**What to build** (spec S5)

- For each term that collides with an everyday or agent word — Tool, Plan, Findings, Stage, Part, Role, Signal —
  look in the runner's results for a wrong decision it caused.
- Rename a term only where one did. A rename goes through `CONTEXT.md`, the glossary (ticket 03), every skill file,
  and the docs that use it, in one PR, with a changelog fragment.
- Where none did, note it in this ticket and leave the term.

**Done when** every listed term is judged, any rename is done with its scenarios passing, and tests and validator are
green.

## Comments

**2026-11-08 — judged, no rename.** Looked through the 37 verdicts and the records' unclear places of the first full
playing and every play since (2026-11-07/08).

- **Failed lines:** d10 (ending the timer), r1 (**Search** and comments), r5 (the scenario against the design), r6
  (the comment's question). None turns on a term's meaning.
- **Unclear places** naming one of the terms: seven, none a confusion with the everyday word. They are about a Stage's
  `search` words hitting siblings (p2, r8), a Stage found in place leaving no trace (r7, fixed since), and Opener
  rules (r1, r4).

| Term | Judged |
| --- | --- |
| Tool | no wrong decision; players kept the suite's Tool apart from the agent's tools throughout |
| Plan | no wrong decision; the `Plan` comment was always found by its first line |
| Findings | no wrong decision. Open, not a collision: whether Reconcile's "In review" line is a finding that makes a decision point (d11, r7, r8) |
| Stage | no wrong decision |
| Part | no wrong decision |
| Role | no wrong decision |
| Signal | no wrong decision; no play reached a signal in a way that hinged on the word |

Every term stays.
