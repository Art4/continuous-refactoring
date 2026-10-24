# 10 — Triage review-bot comments, don't churn for noise

Type: task
Status: done — PR #157

When a review bot comments on a suite MR: assess each comment on its merits, then fix, dismiss with a concrete reason, or ask. No code churn for noise.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments

### 2026-10-16 — gap check against `skills/`: missing

`implement-point.md` step 2 treats a merge request's review comments as findings for step 3, i.e. all get fixed. No assess-each, no dismiss-with-reason, no ask.

### 2026-10-17 — grilled; decisions

Triage applies to bots; a person's comment is fixed or answered, never dismissed by the suite (author type from the forge; unsure → a person's). Classes fix / dismiss / ask, in doubt ask; security, privacy, auth, permissions, migration, idempotency, concurrency are always asked. A bot's claim is checked first where cheap (run the cited test or command). Interactive: a decision point; autonomous may dismiss a bot's comment with reason and turns *ask* into an open question. A short reply under each handled comment (commit or reason), threads left unresolved. No new operation: the tool named by **Merge requests** reads and replies; if it cannot, the report says so. Trigger unchanged (only when the call names a ticket in review). No learned-pattern list (it would be state in the suite; pstack's lives in its plugin and is grown by its maintainers); standing patterns belong in the target's `AGENTS.md`. No ADR. Built in PR "Triage review comments".

### 2026-10-24 — closed

Built in PR #157 as recorded above; checked against `skills/` on 2026-10-24.
