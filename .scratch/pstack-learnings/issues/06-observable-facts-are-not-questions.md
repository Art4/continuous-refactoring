# 06 — Don't ask the human what can be observed

Type: task
Status: done — PR #155

Before a decision point asks the human, classify it: a fact observable by running something (behavior, output, timing) is settled by observing, not asking; only real preference/product calls go to the human. Relates to the human-facing-text wording work.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments

### 2026-10-16 — gap check against `skills/`: mostly covered

`design-point.md` step 2 of *Planning any other ticket*: "Find facts in the code yourself". Missing only: a fact that needs *running* something (behaviour, output, timing) is observed, not asked.

### 2026-10-16 — built

Built with 07 in PR "Observe first, close short": the design point settles a question about behaviour, output or timing by running something that changes nothing in the target (tests, a command, a throwaway script outside the tree) instead of asking. No grilling — one sentence.

### 2026-10-24 — closed

Built in PR #155 as recorded above; checked against `skills/` on 2026-10-24.
