# 10 — Triage review-bot comments, don't churn for noise

Type: task
Status: open

When a review bot comments on a suite MR: assess each comment on its merits, then fix, dismiss with a concrete reason, or ask. No code churn for noise.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments

### 2026-10-16 — gap check against `skills/`: missing

`implement-point.md` step 2 treats a merge request's review comments as findings for step 3, i.e. all get fixed. No assess-each, no dismiss-with-reason, no ask.
