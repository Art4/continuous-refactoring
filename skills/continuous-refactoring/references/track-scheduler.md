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
`bookkeeping.md` — right now: `## Safety Net`, `## Guardrails`, `## Investigation`. **Housekeeping**
joins the same competition the moment its own bookkeeping section exists (`CONTEXT.md`'s **Track**
entry; a later suite change wires it in) — this algorithm doesn't change when it does, only the set of
sections it reads over grows. Nothing here special-cases any Track by name beyond the fixed tie-break
order (below), which already names all four — including Investigation, whose own section carries only
`Cadence`/`Last scan` and no `Open` at all (`refactoring-bookkeeping.md`'s own `## Investigation`
section); see Eligibility and Selection below for exactly how that shape competes.

A Track with **no bookkeeping section at all yet** (never run) is treated as maximally overdue — it
always wins its own ratio comparison, the same "absence means never run, not nothing found" rule
`refactoring-bookkeeping.md` already documents for each Track section.

## Eligibility

A Track only enters ratio comparison when it is both **due** and **eligible** this pass:

- **Due** — the section is absent (never run, see above); or
  `overdue_ratio(track) = (today − Last scan) / Cadence >= 1`; or the Track's own `Cadence` carries no
  day-count at all — Investigation's literal `continuous`, `refactoring-bookkeeping.md`'s own
  `## Investigation` section — in which case it's always due, contributing no ratio to compute at all.
  This is a different reason than "never run" (that one has no `Last scan` yet either; Investigation
  simply has no interval to measure staleness against, full stop, `Last scan` present or not) but the
  same practical outcome: always due.
- **Eligible** — a Track that carries its own `Open` list (Safety Net, Guardrails today) is eligible
  only when that `Open` is empty. Non-empty `Open` means the Track's existing entries get worked
  (propose → design → implement → learn) instead of being rescanned this pass (each Track's own
  reference file, "Is the Track due this pass?") — it drops out of ratio comparison entirely, whether
  or not it's numerically overdue; staleness stops mattering the moment there's already in-flight work
  to finish. A Track with no `Open` concept at all (Housekeeping, once wired; Investigation, per its own
  bookkeeping section — neither ever carries one, per the spec's own bookkeeping schema) is always
  eligible.

## Selection

Among the Tracks that are due and eligible, pick the one with the highest `overdue_ratio`. **Ties** —
including two Tracks that are each "never run," and **Investigation, which never produces a numeric
`overdue_ratio` at all** (no `Cadence` day-count to divide by, above) — fall back to the fixed order:

**Safety Net > Guardrails > Housekeeping > Investigation**

(`CONTEXT.md`'s **Track** entry). Investigation sitting last here is what makes it the scheduler's
permanent fallback in practice, per the spec's own "always eligible, lowest tie-break priority": it's
always due and always eligible (above), but it only actually wins a given pass the moment nothing else
does — any other wired Track that's due and eligible this pass, at any real ratio `>= 1`, outranks it,
and a never-run Track (maximally overdue, above) outranks it too. Investigation is selected only when
every other wired Track is, this pass, either not due, not eligible (non-empty `Open`), or itself absent
with nothing else changing that — never by out-competing another Track's genuine ratio.

The same fixed order also decides which Track's own `Open` work gets this pass's design/implement effort
on the rare occasion more than one wired Track holds non-empty `Open` at the same time — Open-bearing
Tracks resolve on this fixed order directly, never on staleness ratio, since ratio stopped applying to
either of them the moment their own `Open` went non-empty. (With only Safety Net and Guardrails carrying
an `Open` list at all, this never actually happens between them specifically: a Guardrails node is never
unblocked in the tree until Safety Net itself is fully resolved, so Safety Net's `Open` can't still be
non-empty at the same moment Guardrails' is — `guardrails-track.md`'s own Scope section. Investigation
never carries `Open` at all, so it can never be one of the Tracks competing for this slot either way; the
rule stays written for when Housekeeping, which does carry `Open` work of its own kind and no such
gating relationship to Safety Net, joins the competition.)

**No wired Track is both due and eligible** → nothing is selected; step 1 (`refactor-scan`) runs with no
Track this pass, the same outcome as today whenever nothing due was found. **In practice unreachable now
that Investigation is wired** — Investigation is always due and always eligible in every case above
(section absent, a real `overdue_ratio >= 1`, or its own no-day-count `Cadence` — it always matches at
least the last), so it always fills this slot itself at minimum. Documented anyway: it's still the
correct answer for a target with no wired Tracks at all, and stays correct if a future Track is ever
added that, unlike Investigation, genuinely can go both not-due and not-eligible at once.

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
(`safety-net-track.md`, `guardrails-track.md` — Scope / Judging fulfilment / Proposing and recording;
`investigation-track.md` — the single `structural-scan` gate, no judging, no `Open`) still perform their
own process exactly as documented — the tree-walk/gate mechanics are unchanged. Only "which Track (if
any) runs this pass" moved, from each Track re-deriving it independently to this one shared step.

## Suite-wide open-MR cap

Unaffected by any of the above, and already Track-agnostic before this step existed:
`refactor-prioritize/SKILL.md` step 1's "two or more suite MRs already open" stop condition reads every
open `refactor:candidate` issue with a linked pull request, regardless of which Track (or no Track at
all) filed it — a Safety Net or Guardrails Track candidate is filed and labeled exactly like any other
candidate (`skills/refactor-learn/references/safety-net-write.md`,
`skills/refactor-learn/references/guardrails-write.md`), so it already counts toward this same cap. A
structural (Investigation Track) candidate always has, too — an ordinary `refactor:candidate` issue,
nothing new about Track selection changes that. Track selection introduces no duplication here: there
was never a per-Track cap to begin with, only the one suite-wide check this file leaves untouched.
