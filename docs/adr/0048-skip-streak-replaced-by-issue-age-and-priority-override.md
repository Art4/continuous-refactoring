# `Skip streak` replaced by issue age and a `refactor:priority` hard override

> Amends [ADR-0015](0015-suite-merge-requests-always-stack.md) only incidentally: that ADR's own
> decision (suite MRs always stack) is unaffected and stays exactly as decided — `Fulfilled nodes`
> alone still needs it, independent of `Skip streak`'s fate. Builds on
> [ADR-0047](0047-tooling-tree-proposals-are-pre-filed-before-ranking.md), which is what makes this
> decision possible in the first place.

## Context

Ticket 32 (`.scratch/php-tooling-tree/issues/32-required-sibling-starvation.md`) introduced `Skip
streak` to fix a real, live-observed bug: a `required` tooling-tree node (`php-cs-fixer`) was
proposed and passed over for 9+ consecutive passes on a real target, because it structurally never
scores well on `refactor-prioritize`'s other four ranking factors (Heat, Leverage, Tooling pressure,
Risk) — a low-drama style tool with nothing else blocking on it in the moment, yet a hard
prerequisite for other nodes. Nothing prevented it from starving indefinitely. The fix: a per-node
counter in `bookkeeping.md`, incremented every pass a required node was proposable but unchosen,
read back as a fifth ranking factor that weighed an accumulating streak increasingly toward choosing
it.

ADR-0047 (same suite, landed the same day as this decision) changed the premise `Skip streak` was
built on: every currently-unblocked tooling-tree proposal now gets a minimal candidate issue filed
immediately, in `refactor-prioritize`'s own Rank mode, not only the pass's eventual winner. A
starving node is no longer invisible until it happens to win a ranking — it has a real, dated,
visible issue from the pass it first became proposable. That issue's own age is a more honest
starvation signal than `Skip streak`'s pass-count ever was: it tracks actual wall-clock neglect,
independent of how often this loop happens to run (hourly, daily, or only whenever a human triggers
it by hand) — a `Skip streak` of 3 could mean three hours or three months apart, information the
counter itself never carried. Reading it needs no separate, conflict-prone bookkeeping field either:
the tracker (or, for Local Markdown, the issue file itself) already carries the date the moment it's
filed.

Raised by the maintainer directly ("do we still need Skip streak, now that everything gets an
issue?") and grilled to a full replacement, including a second gap `Skip streak` alone never
addressed: a human had no way to manually break a tie once several proposals were all visible at
once — `refactor:priority` already existed as a label, but only affected the backlog cap
(`refactor-scan` step 1) and Select mode's own structural-finding tiering, never `refactor-prioritize`
Rank mode's actual choice among tooling-tree proposals.

## Decision

`Skip streak` — the field, its `refactor-learn` write step, and its ranking-factor row — is removed
entirely, replaced by two signals in `refactor-prioritize`'s Rank mode:

- **`refactor:priority` narrows the candidate pool first.** At least one surviving proposal's issue
  already carries the label (set by a human directly, never automatically) → rank only among those
  this pass; the label is a hard override, not one more weighted input. No proposal carries it → rank
  the full pool, unchanged. Multiple proposals carry it at once → no new tie-break mechanism: the
  existing ranking factors already decide among a shrunk pool the same way they'd decide among the
  full one.
- **Age** replaces `Skip streak` as the fifth ranking factor, scoped to tooling-tree proposals only
  (required and recommended alike — a recommended node sitting neglected for a long time is still a
  real signal, just never a structural blocker the way a required one is). Read from the proposal's
  own issue — native tracker: `created_at`; Local Markdown: a new `Filed: YYYY-MM-DD` line, the one
  new field this decision adds to `local-issue-tracker-template.md`'s single definition, inherited by
  every skill that ever files a local-markdown issue with no per-skill edits needed. Qualitative, like
  the other four factors — no fixed formula or day-threshold; "how long has this sat open relative to
  how often this loop actually runs" is a judgement call, the same shape `refactor-prioritize` already
  makes for Heat/Leverage/Tooling pressure/Risk. A gate name (`structural-scan`, a baseline-shrink
  family) or externally-labeled candidate carries no age here — their own tiering (Select mode) already
  covers the same concern for them.
- `refactor-scan` step 3b, which already detects issue-backed proposals, now also surfaces each one's
  creation date and whether it carries `refactor:priority` alongside it — `refactor-prioritize` never
  needs a second round-trip to the tracker to read either.

No migration for a target with existing `Skip streak` entries in `bookkeeping.md` — the field becomes
dead, unread data; cheap for a human to delete by hand, not worth an automated cleanup step nobody
would notice either way.

## Considered Options

- **Keep `Skip streak` alongside the new signals**, rather than replacing it. Rejected — it would
  keep every one of its own costs (a bookkeeping field two branches could conflict on, the
  fresh-sync discipline ADR-0034 needed to keep it correct) for a role ADR-0047's pre-filing and this
  ADR's age factor already cover between them, more honestly.
- **Age as a hard threshold** (e.g. "older than N days automatically wins"), mirroring `Skip
  streak`'s own numeric-counter shape. Rejected — inconsistent with the other four factors, all
  qualitative judgement calls; a single hard-formula row next to four soft ones reads as a
  different kind of rule for no real reason, and a fixed day-count doesn't generalize across targets
  running this loop at wildly different cadences.
- **`refactor:priority` as a soft ranking boost** rather than a hard override. Rejected — a human
  setting a label directly is a deliberate steering decision, not one more data point to weigh
  against everything else; treating it as just another factor would let a hot-but-unlabeled proposal
  outrank an explicit human request, defeating the label's own purpose.
- **A new tie-break rule for multiple `refactor:priority` proposals.** Rejected as unnecessary — pool
  restriction already reduces the problem to "rank these few candidates," something
  `refactor-prioritize` already does for the full pool; no second mechanism needed.

## Consequences

- `skills/refactor-prioritize/SKILL.md`: `Skip streak`'s ranking-factor row replaced by `Age`; Rank
  mode step 2 gains the priority-pool-restriction rule ahead of the factor table.
- `skills/refactor-learn/SKILL.md` and `skills/refactor-learn/references/fulfilled-nodes-write.md`:
  the `Skip streak` write step is gone; `Fulfilled nodes`' own fresh-sync discipline (ADR-0034) is
  unaffected and stays, now justified purely by its own (still real) staleness risk.
- `skills/continuous-refactoring/references/refactoring-bookkeeping.md`: the field, its table row,
  and its own documentation section removed.
- `skills/continuous-refactoring/references/local-issue-tracker-template.md`: gains `Filed:
  YYYY-MM-DD`.
- `skills/refactor-scan/SKILL.md` step 3b: surfaces creation date and `refactor:priority` alongside
  each issue-backed proposal it hands forward.
- A future scan/design/learn pass must not reintroduce a `Skip streak`-shaped counter field, and must
  not treat a `refactor:priority`-labeled tooling-tree proposal as merely one more ranking input —
  it's a pool filter, applied before the other factors run at all.
