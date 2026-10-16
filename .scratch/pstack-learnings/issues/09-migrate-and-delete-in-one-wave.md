# 09 — Migrate callers and delete the old API in one wave

Type: task
Status: open

Refactor guidance: migrate every caller and delete the old API together, no shims or parallel old/new paths; subtract dead code and one-caller wrappers before reshaping; commit order subtraction, reshape, follow-up. Includes the rename spot-check against real files.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments

### 2026-10-16 — gap check against `skills/`: conflict to decide

`foundational-refactoring-rules.md` says Strangler Fig: old and new side by side until the swap is complete. pstack says migrate every caller and delete the old API in one wave, no shims. Both can hold: wide or external-consumer migrations strangle, internal ones with no outside consumers go in one wave — but the rule needs that distinction. Subtract-before-add, commit order and the rename spot-check are missing (only "rename" as a technique).
