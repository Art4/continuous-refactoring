# 09 — Migrate callers and delete the old API in one wave

Type: task
Status: open

Refactor guidance: migrate every caller and delete the old API together, no shims or parallel old/new paths; subtract dead code and one-caller wrappers before reshaping; commit order subtraction, reshape, follow-up. Includes the rename spot-check against real files.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments
