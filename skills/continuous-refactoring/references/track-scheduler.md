# Track scheduler

`continuous-refactoring/SKILL.md` step 1's own process: which **Track** (`CONTEXT.md`) this pass runs,
computed generically over every Track carrying a `Cadence`/`Last scan` bookkeeping section
(`refactoring-bookkeeping.md`) — not a fixed two-Track special
case. Supersedes each Track's own earlier standalone "is my Track due?" check
(`../../refactor-scan/references/safety-net-track.md`, `../../refactor-scan/references/guardrails-track.md`,
each file's own "Is the Track due this pass?" section; and, for Housekeeping, the
now-retired standalone `continuous-housekeeping` skill's own tracker-history due-check, replaced by
`../../continuous-housekeeping/references/housekeeping-track.md`'s own same-named section) — that check
answered the question alone because, when it was written, no other Track existed yet to compete with.
This file is the real competition those sections deferred.

## Which Tracks compete

Every Track whose own `Cadence`/`Last scan` bookkeeping section currently exists in the target's
`bookkeeping.md` — right now: `## Safety Net`, `## Guardrails`, `## Housekeeping`, `## Investigation`,
every one of the four currently-wired Tracks (`CONTEXT.md`'s **Track** entry). Nothing here
special-cases any Track by name beyond the fixed tie-break order (below), which already names all
four — including Investigation, whose own section carries its own `Open` alongside `Cadence`/`Last
scan` (`refactoring-bookkeeping.md`'s own `## Investigation` section), and Housekeeping, whose own section
carries only the latter two but, unlike Investigation, a real, unit-carrying `Cadence` that competes in ratio
comparison exactly like Safety Net's/Guardrails' own (`refactoring-bookkeeping.md`'s own `##
Housekeeping` section); see Eligibility and Selection below for exactly how each shape competes.

A Track with **no bookkeeping section at all yet** (never run) is treated as maximally overdue — it
always wins its own ratio comparison, the same "absence means never run, not nothing found" rule
`refactoring-bookkeeping.md` already documents for each Track section.

## Safety Net blockade

While Safety Net `Open` is non-empty, Safety Net is selected and nothing else runs, even if no node is
currently workable — the scheduler reports the wait. This is stronger than the ordinary eligibility rule
(a non-empty `Open` making a Track ineligible for ratio comparison): Safety Net's `Open` acts as a
system-wide blockade, not just a self-exclusion. Guardrails, Housekeeping, and Investigation all yield
until Safety Net `Open` empties.

## Eligibility

A Track only enters ratio comparison when it is both **due** and **eligible** this pass:

- **Due** — the section is absent (never run, see above); or
  `overdue_ratio(track) >= 1`, where `overdue_ratio` is computed from the Track's `Cadence` and `Last scan`
  per `refactoring-bookkeeping.md`'s *Cadence values* (an interval in hours/days/weeks/months:
  `(today − Last scan) / interval`; a `monthly on the <N>th` anchor: due once such a day has passed since
  `Last scan`, ratio `max(1, elapsed / 30)`). Investigation's `Cadence` carries no interval at all — the
  literal `continuous`, `refactoring-bookkeeping.md`'s own `## Investigation` section — so it is always
  due and contributes no ratio; it never enters ratio comparison and is selected only as the fallback
  (Selection, step 4).
- **Eligible** — a Track that carries its own `Open` (Safety Net, Guardrails) is eligible for ratio
  comparison only when that `Open` is empty. Non-empty `Open` means the Track's existing entries get
  worked (propose → design → implement → learn) instead of being rescanned (each Track's own reference
  file, "Is the Track due this pass?") — staleness stops mattering the moment there's already in-flight
  work to finish; Selection's steps 1 and 3 decide when that work gets a pass.
  **Housekeeping** is the one Track with no `Open` concept at all (`refactoring-bookkeeping.md`'s own
  `## Housekeeping` section) — always eligible the moment it's due; a cycle already in progress is
  tracked by the tracker's own history instead (`../../continuous-housekeeping/references/housekeeping-track.md`'s
  own *Resuming an in-progress cycle* section), not by this eligibility rule.

## Selection

Four checks, in order; the first that matches selects this pass's Track. The fixed order **Safety Net >
Guardrails > Housekeeping > Investigation** (`CONTEXT.md`'s **Track** entry) is what the cascade
implements, and what breaks every tie.

1. **Safety Net's `Open` is non-empty** → **Safety Net** (the blockade, above).
2. **Safety Net, Guardrails or Housekeeping is due and eligible** → the one with the highest
   `overdue_ratio`. Ties — including two Tracks that are each "never run" — fall back to the fixed
   order. This is where **Housekeeping preemption** happens: a due Housekeeping takes the pass even
   while Guardrails holds workable `Open` nodes, for that one pass — its own `Last scan` is written by
   the end of it, so the next pass falls through to step 3 again. A due Safety Net rescan takes the pass
   the same way.
3. **Guardrails' `Open` holds at least one workable node**
   (`../../refactor-scan/references/track-open-processing.md`) → **Guardrails**, working that `Open`.
   With `Open` non-empty but nothing workable, Guardrails **yields**: its `Open` stays as it is, the
   stalled nodes are reported with their reasons, and the cascade moves on.
4. **Otherwise** → **Investigation**, the permanent fallback: always due, never out-competing another
   Track's genuine ratio or Guardrails' workable backlog. Its own `Open` decides only what that pass
   does, never whether it is selected — non-empty `Open` resumes the in-flight candidate(s), empty `Open`
   scans (`../../refactor-scan/references/investigation-track.md`).

**A fresh target, right after Safety Net first closes** (`## Guardrails`, `## Housekeeping` and
`## Investigation` all still absent) gets no special treatment: step 2 ties Guardrails and Housekeeping
as never run and picks Guardrails for its first scan, then Housekeeping for its first cycle, then step 3
works Guardrails' backlog; Investigation's first pass comes once that backlog is done or stalled. A
human who wants structural work — or any other Track — sooner names that Track (Manual override, below);
`continuous-safety-net`'s closing report says so the moment Safety Net's `Open` is empty.

**More than one `Open` can be non-empty at once.** Guardrails' and Investigation's `Open` are not
mutually exclusive — Guardrails' nodes hang beneath `php-safety-net`, they are not parents of
`structural-scan` — so an Investigation candidate can be in flight while Guardrails still holds a backlog
(e.g. Guardrails stalled, Investigation scanned, a Guardrails node became workable again). The cascade
already resolves it: Guardrails' workable `Open` (step 3) goes first, and Investigation resumes its own
`Open` on the next pass that reaches step 4.

**At most one Track is selected per pass.** Each pass runs exactly one Track's process. This keeps each
pass focused and avoids interleaving different Tracks' work within a single pass.

**No Track selected** is unreachable while Investigation is wired — step 4 always matches. It stays the
correct answer for a target with no wired Tracks at all: nothing is selected, step 2 of `../SKILL.md`
has nothing to dispatch, and the pass ends with that reported.

## Manual override

The human invoking this pass may name a specific Track directly instead of letting the ratio/tie-break
computation above run at all — this pass runs that named Track's own process unconditionally, bypassing
Eligibility/Selection, the Safety Net blockade included. The
`Open`-non-empty eligibility rule still applies to a manually-named Track exactly as it would to one the
scheduler picked itself. The rule for when a scan runs is the same either way: **a selected Track with
no `Open` entries is scanned; a selected Track with a non-empty `Open` works its `Open` walk.** Naming
Safety Net while its `Open` is non-empty means working that `Open` entry, never a fresh rescan — that
includes an `Open` still written under the old meaning (only nodes that had a filed issue), which is
walked like any other and corrected by the scan that runs once it empties. One shared invocation surface across all four Track names — naming Safety
Net, Guardrails, Housekeeping, or Investigation directly when invoking `/continuous-refactoring` (e.g.
"run the Housekeeping Track") all bypass selection the same way. This generalizes what used to be the
now-retired standalone `continuous-housekeeping` skill's own separate on-demand invocation (a human
running that skill directly instead of waiting for its cadence) to the same pattern the other three
Tracks already used — one surface, one argument, four possible names.

## Handing off to `refactor-scan`, or directly to the Housekeeping Track's own process

`refactor-scan` no longer decides for itself whether a Track is due — this step decides once, before
`refactor-scan` starts, and dispatches to the winner's own skill (step 2), which hands the Track down
through `refactor-loop` to `refactor-scan` as an explicit input. `refactor-scan/SKILL.md` step 4 and each Track's own reference file
(`safety-net-track.md`, `guardrails-track.md` — Scope / Judging fulfilment / Proposing and recording;
`investigation-track.md` — the single `structural-scan` gate, no judging, no `Open`) still perform their
own process exactly as documented — the tree-walk/gate mechanics are unchanged. Only "which Track (if
any) runs this pass" moved, from each Track re-deriving it independently to this one shared step.

**Housekeeping is the one exception to "hands the winner down to `refactor-scan`."** It isn't a
tooling-tree scan at all — `refactor-scan`'s own contract is "detect, never write"
(`../../refactor-scan/SKILL.md`), and the Housekeeping Track's own process commits, opens issues, and
opens merge requests directly, the same way it always did as the now-retired standalone
`continuous-housekeeping` skill. Selecting Housekeeping hands off straight to
`../../continuous-housekeeping/references/housekeeping-track.md`, run by `continuous-housekeeping`
(dispatched to by `../SKILL.md` step 2) — `refactor-scan`
never runs at all this pass in that case.

## Suite-wide open-MR cap

Unaffected by any of the above, and already Track-agnostic before this step existed:
`refactor-loop/SKILL.md` step 5's cap gate ("two or more suite MRs already open", checked before a new MR is opened) reads every
open `refactor:candidate` issue with a linked pull request, regardless of which Track (or no Track at
all) filed it — a Safety Net or Guardrails Track candidate is filed and labeled exactly like any other
candidate (`../../refactor-learn/references/safety-net-write.md`,
`../../refactor-learn/references/guardrails-write.md`), so it already counts toward this same cap. A
structural (Investigation Track) candidate always has, too — an ordinary `refactor:candidate` issue,
nothing new about Track selection changes that. Track selection introduces no duplication here: there
was never a per-Track cap to begin with, only the one suite-wide check this file leaves untouched.
