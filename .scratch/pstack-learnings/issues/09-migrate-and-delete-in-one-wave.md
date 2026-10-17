# 09 — Migrate callers and delete the old API in one wave

Type: task
Status: open

Refactor guidance: migrate every caller and delete the old API together, no shims or parallel old/new paths; subtract dead code and one-caller wrappers before reshaping; commit order subtraction, reshape, follow-up. Includes the rename spot-check against real files.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments

### 2026-10-16 — gap check against `skills/`: conflict to decide

`foundational-refactoring-rules.md` says Strangler Fig: old and new side by side until the swap is complete. pstack says migrate every caller and delete the old API in one wave, no shims. Both can hold: wide or external-consumer migrations strangle, internal ones with no outside consumers go in one wave — but the rule needs that distinction. Subtract-before-add, commit order and the rename spot-check are missing (only "rename" as a technique).

### 2026-10-17 — grilled; decisions

Not a hard rule: three principles in `principles.md` — *Migrate callers, then delete* (new), *Strangler Fig* (trigger narrowed to: something outside depends on the old API, or the migration is too wide for one reviewable step), *Subtract before you add* (new). The line: "in one wave" only when every caller is in this repository and nothing outside depends on the API; when in doubt, treat it as depended on; the plan records the call under `Decisions`. Order after the pin: subtract, reshape, follow-up — judgement, not checked. Rename spot-check added to the implement point (search the whole repository for the old name; fix or name the hits). A test of code the plan deletes goes with it and is named among the tests that survive (added to *A check is never weakened*). No ADR; docs: one FAQ entry and a changelog fragment. A library with BC promises (see the Roave BC check idea) is the sharpest case of "something outside depends on it". Built in PR "Migrate callers and subtract first".
