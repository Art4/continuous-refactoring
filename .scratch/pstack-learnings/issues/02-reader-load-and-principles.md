# 02 — Reader load as success measure; principles with triggers

Type: task
Status: open

A candidate is kept only if the diff lowers reader load somewhere (fewer layers, branches, hidden state); otherwise it is reverted, and speculative cleanup too. Also (pstack idea 11): keep principles in one reference, each with a "when it applies" trigger, and have the MR report name which principle shaped which decision.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments

### 2026-10-16 — gap check against `skills/`: missing

`reviewing-a-change.md` has a smell table (Speculative Generality → delete) but no "does this diff lower reader load, else revert" test. `foundational-refactoring-rules.md` is five bullets without a "when it applies" trigger, and no report names which principle shaped which decision.
