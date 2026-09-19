# Track scheduler

`continuous-refactoring/SKILL.md` step 0b's own process: which **Track** (`CONTEXT.md`) this pass runs,
computed generically over every Track carrying a `Cadence`/`Last scan` bookkeeping section
(`skills/continuous-refactoring/references/refactoring-bookkeeping.md`) — not a fixed two-Track special
case. Supersedes each Track's own earlier standalone "is my Track due?" check
(`skills/refactor-scan/references/safety-net-track.md`, `skills/refactor-scan/references/
guardrails-track.md`, each file's own "Is the Track due this pass?" section) — that check answered the
question alone because, when it was written, no other Track existed yet to compete with. This file is
the real competition those sections deferred.

## Which Tracks compete

Every Track whose own `Cadence`/`Last scan` bookkeeping section currently exists in the target's
`bookkeeping.md` — right now: `## Safety Net`, `## Guardrails`. **Housekeeping** and **Investigation**
join the same competition the moment their own bookkeeping sections exist (`CONTEXT.md`'s **Track**
entry; later suite changes wire each one in) — this algorithm doesn't change when they do, only the set of
sections it reads over grows. Nothing here special-cases Safety Net or Guardrails by name beyond the
fixed tie-break order (below), which already names all four.

A Track with **no bookkeeping section at all yet** (never run) is treated as maximally overdue — it
always wins its own ratio comparison, the same "absence means never run, not nothing found" rule
`refactoring-bookkeeping.md` already documents for each Track section.

## Eligibility

A Track only enters ratio comparison when it is both **due** and **eligible** this pass:

- **Due** — the section is absent (never run, see above), or
  `overdue_ratio(track) = (today − Last scan) / Cadence >= 1`.
- **Eligible** — a Track that carries its own `Open` list (Safety Net, Guardrails today) is eligible
  only when that `Open` is empty. Non-empty `Open` means the Track's existing entries get worked
  (propose → design → implement → learn) instead of being rescanned this pass (each Track's own
  reference file, "Is the Track due this pass?") — it drops out of ratio comparison entirely, whether
  or not it's numerically overdue; staleness stops mattering the moment there's already in-flight work
  to finish. A Track with no `Open` concept at all (Housekeeping, Investigation, once wired — neither
  ever carries one, per the spec's own bookkeeping schema) is always eligible.

## Selection

Among the Tracks that are due and eligible, pick the one with the highest `overdue_ratio`. **Ties** —
including two Tracks that are each "never run" (no ratio to compare numerically) — fall back to the
fixed order:

**Safety Net > Guardrails > Housekeeping > Investigation**

(`CONTEXT.md`'s **Track** entry). The same fixed order also decides which Track's own `Open` work gets
this pass's design/implement effort on the rare occasion more than one wired Track holds non-empty
`Open` at the same time — Open-bearing Tracks resolve on this fixed order directly, never on staleness
ratio, since ratio stopped applying to either of them the moment their own `Open` went non-empty. (With
only Safety Net and Guardrails wired so far this never actually happens: a Guardrails node is never
unblocked in the tree until Safety Net itself is fully resolved, so Safety Net's `Open` can't still be
non-empty at the same moment Guardrails' is — `guardrails-track.md`'s own Scope section. The rule is
written for when Housekeeping/Investigation, which carry no such gating relationship to Safety Net, join
the competition.)

**No wired Track is both due and eligible** → nothing is selected; step 1 (`refactor-scan`) runs with no
Track this pass, the same outcome as today whenever nothing due was found.

## Manual override

The human invoking this pass may name a specific Track directly instead of letting the ratio/tie-break
computation above run at all — this pass runs that named Track's own process unconditionally. The
`Open`-non-empty eligibility rule still applies to a manually-named Track exactly as it would to one the
scheduler picked itself: naming Safety Net while its `Open` is non-empty still means working that `Open`
entry, never a fresh rescan. This is the same "name a Track as this pass's input" shape
`continuous-housekeeping`'s own on-demand invocation already uses today (a human types
`/continuous-housekeeping` directly instead of waiting for its cadence) — not yet folded into one shared
invocation surface across all four Track names (that's `continuous-housekeeping`'s own retirement, a
later change); today it means naming Safety Net or Guardrails directly when invoking
`/continuous-refactoring`.

## Handing off to `refactor-scan`

`refactor-scan` no longer decides for itself whether a Track is due — this step decides once, before
`refactor-scan` starts, and hands the winner down as an explicit input (or hands down "no Track" when
nothing wired was due and eligible). `refactor-scan/SKILL.md` step 4 and each Track's own reference file
(`safety-net-track.md`, `guardrails-track.md`) still perform the Scope / Judging fulfilment / Proposing
and recording process exactly as documented — the tree-walk mechanics are unchanged. Only "which Track
(if any) runs this pass" moved, from each Track re-deriving it independently to this one shared step.

## Suite-wide open-MR cap

Unaffected by any of the above, and already Track-agnostic before this step existed:
`refactor-prioritize/SKILL.md` step 1's "two or more suite MRs already open" stop condition reads every
open `refactor:candidate` issue with a linked pull request, regardless of which Track (or no Track at
all) filed it — a Safety Net or Guardrails Track candidate is filed and labeled exactly like any other
candidate (`skills/refactor-learn/references/safety-net-write.md`,
`skills/refactor-learn/references/guardrails-write.md`), so it already counts toward this same cap.
Track selection introduces no duplication here: there was never a per-Track cap to begin with, only the
one suite-wide check this file leaves untouched.
