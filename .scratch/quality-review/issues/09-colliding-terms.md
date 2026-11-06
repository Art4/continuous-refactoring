# 09 — Colliding terms

Type: task
Status: open
Blocked by: 05

**What to build** (spec S5)

- For each term that collides with an everyday or agent word — Tool, Plan, Findings, Stage, Part, Role, Signal —
  look in the runner's results for a wrong decision it caused.
- Rename a term only where one did. A rename goes through `CONTEXT.md`, the glossary (ticket 03), every skill file,
  and the docs that use it, in one PR, with a changelog fragment.
- Where none did, note it in this ticket and leave the term.

**Done when** every listed term is judged, any rename is done with its scenarios passing, and tests and validator are
green.
