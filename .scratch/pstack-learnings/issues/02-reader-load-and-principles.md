# 02 — Reader load as success measure; principles with triggers

Type: task
Status: done — PR #153

A candidate is kept only if the diff lowers reader load somewhere (fewer layers, branches, hidden state); otherwise it is reverted, and speculative cleanup too. Also (pstack idea 11): keep principles in one reference, each with a "when it applies" trigger, and have the MR report name which principle shaped which decision.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments

### 2026-10-16 — gap check against `skills/`: missing

`reviewing-a-change.md` has a smell table (Speculative Generality → delete) but no "does this diff lower reader load, else revert" test. `foundational-refactoring-rules.md` is five bullets without a "when it applies" trigger, and no report names which principle shaped which decision.

### 2026-10-16 — grilled; decisions

Reader load defined (layers to trace, state to hold; only extraneous load can be lowered; source Zakirullin). Structural tickets only; Housekeeping ideas pass via the existing take-the-commits-off mechanism, and the pin gap there is closed (an existing green test must reach the code, else the task is not workable). Checked in review on the Standards axis as a new finding; a slice with no gain is taken off, not reworked; the test stands above the smell table. No new plan field: the yardstick is the friction the Ground step named. When nothing is left: no merge request, a comment on the ticket, no automatic rejection. New `references/principles.md` (title, *Applies when*, principle, *Fails when*; a header says judgement wins with a stated reason); first entry Reader load, plus the Strangler Fig and technique vocabulary moved out of `foundational-refactoring-rules.md`, which keeps only the hard rules. Design reads the principles and names the ones that changed a decision under `Decisions`; the MR gets one plain sentence, no suite terms; a target's skill gets the file as guidance. ADR 0078 partly supersedes 0004. Built in PR "Reader load and principles". Ticket 09's choice (strangle vs. migrate in one wave) is untouched.

### 2026-10-24 — closed

Built in PR #153 as recorded above; checked against `skills/` on 2026-10-24.
