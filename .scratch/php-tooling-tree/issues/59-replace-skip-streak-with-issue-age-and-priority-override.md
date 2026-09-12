# 59 — Replace `Skip streak` with issue age and a `refactor:priority` override

**What to build:** Remove `Skip streak` entirely and replace its anti-starvation role with two signals that ADR-0047's always-on candidate pre-filing (PR #76) now makes possible: the pre-filed issue's own **age**, and a human-settable **`refactor:priority`** label acting as a hard override.

**Why now, not before:** Skip streak (ticket 32, ADR-0015) existed because a `required` tooling-tree node could be proposed and passed over indefinitely without ever getting an issue filed for it — invisible to a human, and with no automatic self-correction beyond a bespoke per-node counter in `bookkeeping.md`. ADR-0047 (this same suite, landed today) already gives every tooling-tree proposal a real, dated issue the moment it's proposable, not just the eventual winner. That issue's own age is a more honest anti-starvation signal than a pass-count (it tracks wall-clock neglect, not how often the loop happens to run), and it needs no separate, conflict-prone bookkeeping field to maintain.

## Decisions (grilled, `/grill-me`)

1. **Scope of the age factor:** every tooling-tree proposal, required *and* recommended — not gate names (`structural-scan`, baseline-shrink) or externally-labeled candidates, which have their own priority/capped tiering already (Select mode).
2. **Age semantics:** qualitative, matching the existing four factors (Heat, Leverage, Tooling pressure, Risk) — no fixed formula or day-threshold. "How long has this sat open, relative to the loop's own pace" is a judgement call for `refactor-prioritize`, same as the others.
3. **`refactor:priority` in Rank mode — hard override, via pool restriction, not a new tie-break mechanism:** at least one ranked proposal's issue carries `refactor:priority` → the candidate pool for this ranking shrinks to only those; the existing four-now-five factors (Heat/Leverage/Tooling pressure/Risk/Age) rank normally *within* that shrunk pool. No proposal carries it → unchanged, rank the full pool as today.
4. **New `Filed: YYYY-MM-DD` field, Local Markdown tracker only, one place:** added to `skills/continuous-refactoring/references/local-issue-tracker-template.md`'s single "When a skill says 'file an issue'" definition — every skill that ever files a local-markdown issue inherits it automatically, no per-skill edits needed. Native trackers (GitHub, GitLab) need nothing new — `created_at` is already a native API field.
5. **No migration.** A target with pre-existing `Skip streak` entries in `bookkeeping.md` keeps them as dead, unread data — cheap to hand-delete, not worth an automated cleanup step.
6. **Plumbing (not a fresh decision, follows from the above):** `refactor-scan` step 3b, which already detects issue-backed proposals, also surfaces each one's creation date and whether it carries `refactor:priority`, so `refactor-prioritize` never needs a second round-trip to the tracker. A proposal `refactor-prioritize` itself pre-files this same pass (brand new) trivially has age zero and no label yet.

## Affected files (expected, confirm during implementation)

- `skills/refactor-prioritize/SKILL.md` — drop the `Skip streak` factor row, add `Age`; add the priority-override pool-restriction rule to step 2 (Rank), right where "File as you read" already lives.
- `skills/refactor-learn/SKILL.md` — drop `Skip streak` from the closing-call write list (keeps `Fulfilled nodes` only).
- `skills/refactor-learn/references/fulfilled-nodes-write.md` — remove the `## Skip streak` section entirely; the "Read fresh, not stale" section's reasoning stays (still needed for `Fulfilled nodes`), reworded to drop the now-gone field from its own examples.
- `skills/continuous-refactoring/references/refactoring-bookkeeping.md` — remove the `Skip streak` field's table row and its own `## Skip streak` section; drop it from the field-ordering note and the hand-edit-boundary bullet.
- `skills/continuous-refactoring/SKILL.md` — step 0's housekeeping-independence sentence drops its `Skip streak` mention.
- `skills/refactor-scan/SKILL.md` — step 3b's own description gains the creation-date/priority-label surfacing (plumbing decision 6 above).
- `skills/continuous-refactoring/references/local-issue-tracker-template.md` — add `Filed: YYYY-MM-DD` next to the existing `Status:`/`Labels:` line.
- `CONTEXT.md` — check whether `Skip streak`/`Signal` entries need wording updates (the `Signal` entry's own factor catalogue may list it).
- A new ADR under `docs/adr/`, referencing ticket 32/ADR-0015 as the origin being reversed, and ADR-0047 as what makes the reversal safe.

**Status:** ready-for-agent

- [ ] `Skip streak` removed: field, write step, ranking-factor row, all documentation mentions
- [ ] `Age` factor added to `refactor-prioritize` Rank mode, scoped to tooling-tree proposals only
- [ ] `refactor:priority` hard-override (pool restriction) wired into Rank mode
- [ ] `Filed: YYYY-MM-DD` added to the Local Markdown issue-tracker template, one place
- [ ] `refactor-scan` step 3b surfaces creation date + priority label alongside each issue-backed proposal
- [ ] New ADR recording the reversal and its reasoning

## Comments

> **2026-09-12:** Grilled (`/grill-me`) as a follow-up to a "why do we still need Skip streak" investigation (no code changes) that traced it back to ticket 32/ADR-0015 and confirmed ADR-0047's pre-filing (PR #76, same day) removes most of Skip streak's original justification. All decisions above confirmed by the maintainer.
