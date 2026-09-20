# Track scheduler

`continuous-refactoring/SKILL.md` step 0b's own process: which **Track** (`CONTEXT.md`) this pass runs,
computed generically over every Track carrying a `Cadence`/`Last scan` bookkeeping section
(`skills/continuous-refactoring/references/refactoring-bookkeeping.md`) — not a fixed two-Track special
case. Supersedes each Track's own earlier standalone "is my Track due?" check
(`skills/refactor-scan/references/safety-net-track.md`, `skills/refactor-scan/references/
guardrails-track.md`, each file's own "Is the Track due this pass?" section; and, for Housekeeping, the
now-retired standalone `continuous-housekeeping` skill's own tracker-history due-check, replaced by
`skills/continuous-refactoring/references/housekeeping-track.md`'s own same-named section) — that check
answered the question alone because, when it was written, no other Track existed yet to compete with.
This file is the real competition those sections deferred — plus the one-time exception (below) that
overrides that competition's outcome for exactly three turns per repo, right after Safety Net's
foundation is first fully in place.

## Which Tracks compete

Every Track whose own `Cadence`/`Last scan` bookkeeping section currently exists in the target's
`bookkeeping.md` — right now: `## Safety Net`, `## Guardrails`, `## Housekeeping`, `## Investigation`,
every one of the four currently-wired Tracks (`CONTEXT.md`'s **Track** entry). Nothing here
special-cases any Track by name beyond the fixed tie-break order (below), which already names all
four — including Investigation, whose own section carries only `Cadence`/`Last scan` and no `Open` at
all (`refactoring-bookkeeping.md`'s own `## Investigation` section), and Housekeeping, whose own section
carries the same two fields but, unlike Investigation, a real numeric `Cadence` that competes in ratio
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

## One-time exception

Checked first, every pass, **before** Eligibility/Selection below ever run — a target that just finished
its Safety Net foundation gets one dedicated turn each for Investigation, then Guardrails, then
Housekeeping, in that order, before ordinary ratio/tie-break selection gets a vote at all (`CONTEXT.md`'s
**Track** entry: "one deliberate exception, per target, one time only"). Only a manual override (below)
outranks this check; nothing else does.

**Precondition, all three turns:** `## Safety Net` exists and its `Open` is currently empty. Absent
either half of that — the section doesn't exist yet, or `Open` is still non-empty — this whole section
is skipped this pass and Eligibility/Selection runs unmodified (a non-empty Safety Net `Open` already
forces Safety Net's own selection anyway, via the ordinary Eligibility rule below — there is no case
where skipping this check here loses ground to Safety Net's own in-flight work).

With that precondition met, check the following three, in order, and stop at the first match:

1. **`## Investigation` section absent, or present with `Pending candidates` currently naming an
   issue (not `none`)** → select **Investigation**, this pass, overriding ratio/tie-break entirely. The
   `Pending candidates` half of this check is load-bearing, not redundant with "section absent": per
   `skills/refactor-learn/references/investigation-write.md`, `## Investigation`'s `Last scan` is written
   the moment the Track's *scan* step runs — the very first pass of this turn — long before its one
   candidate is actually delivered (design → implement → learn can each take a further pass).
   Investigation carries no `Open` list of its own to lean on the way Guardrails/Safety Net do for this
   same "stay selected until done" job, so this check reads `Pending candidates` instead — the existing
   field that already tracks exactly this one in-flight candidate
   (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`'s own `Pending candidates`
   row) — keeping Investigation force-selected on every pass until it clears, matching "one candidate,
   fully delivered," not just proposed.
2. Else, **`## Guardrails` section absent** → select **Guardrails**, this pass, overriding ratio/
   tie-break. Guardrails gets one turn; once its section exists, the ordinary eligibility rule below
   governs it like any other Track — there is no special mechanism that keeps it selected after its
   first scan.
3. Else, **`## Housekeeping` section absent** → select **Housekeeping**, this pass, overriding ratio/
   tie-break. Housekeeping's entire cycle — reconcile, open this cycle's issue, work the checklist,
   quality gate, deliver — runs to completion inside the single pass `SKILL.md` step 0c performs
   (`skills/continuous-refactoring/references/housekeeping-track.md`), so — unlike Investigation's own
   turn above — there is no multi-pass in-flight state to keep re-selecting across; the section exists
   with `Last scan` written by the time that same pass's closing call finishes.
4. Else (all three sections present, and `## Investigation` carries no in-flight `Pending candidates`)
   → this exception is permanently done for this repo. Every later pass — including a later, ordinary
   Safety Net rescan (`Cadence: 90`) whose own `Open` goes non-empty then empty again — runs
   Eligibility/Selection below unmodified, forever. This is what makes the exception fire **exactly
   once**: the trigger above never reads Safety Net's `Open` transition itself (this file has no history
   to diff against, only the current `bookkeeping.md` snapshot — see the note below), only each of
   Investigation's/Guardrails'/Housekeeping's own permanent, one-way "have I ever run" state, which the
   suite already keeps as ordinary staleness bookkeeping and never clears. Reusing it here needs no new
   stored flag, and each of the three conditions above can only ever be true once per Track, per repo.

**Open state irrelevant during the one-time exception:** the exception runs before Eligibility/Selection
below, so the `Open`-non-empty eligibility rule never fires during one of its turns. Guardrails' `Open`
being non-empty (e.g. from its own scan filling it with in-flight entries) does not block the sequence
from advancing to the next Track — the exception reads only whether each section *exists*, not whether
its `Open` is empty. This matches the design intent: the one-time exception runs exactly once per Track,
in order, regardless of in-flight state, then permanently retires.

**What this can't distinguish, by construction:** with no per-pass history file to diff against — only
`bookkeeping.md`'s current snapshot — this check cannot tell "Safety Net's `Open` just emptied for the
first time" apart from "Safety Net's `Open` has simply always been empty" (a trivial tree with nothing to
propose on its very first scan). Both look identical in a snapshot, and both are treated the same way:
if Investigation/Guardrails/Housekeeping have never run yet, this exception still fires. This matches its
own spirit either way — a repo with no residual Safety Net work in flight is exactly the state it exists
to react to, regardless of how it got there.

## Eligibility

Reached only once the one-time exception (above) didn't apply this pass. A Track only enters
ratio comparison when it is both **due** and **eligible** this pass:

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
  to finish. Guardrails follows this rule: with at least one workable `Open` node, it is selected ahead
  of Investigation; with nothing workable, it yields. A Track with no `Open` concept at all
  (Housekeeping, Investigation — neither ever carries one, per the spec's own bookkeeping schema) is
  always eligible; a Housekeeping cycle already in progress is tracked by the tracker's own history
  instead (`skills/continuous-refactoring/references/housekeeping-track.md`'s own *Resuming an
  in-progress cycle* section), not by this eligibility rule. Investigation waits behind a Guardrails
  backlog with workable nodes — Guardrails' workable nodes outrank Investigation's permanent fallback
  status.

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

**Housekeeping preemption:** Housekeeping can preempt Guardrails for one pass when due (its
`overdue_ratio >= 1`). This means Housekeeping is selected over Guardrails for that single pass,
even though Guardrails has higher tie-break priority. After that one pass, ordinary selection resumes.

**At most one Track is selected per pass.** Each pass runs exactly one Track's process (or no Track
at all, if nothing was due and eligible). This keeps each pass focused and avoids interleaving
different Tracks' work within a single pass.

The same fixed order also decides which Track's own `Open` work gets this pass's design/implement effort
on the rare occasion more than one wired Track holds non-empty `Open` at the same time — Open-bearing
Tracks resolve on this fixed order directly, never on staleness ratio, since ratio stopped applying to
either of them the moment their own `Open` went non-empty. In practice this never actually happens with
all four Tracks wired: only Safety Net and Guardrails carry an `Open` list at all (Housekeeping's own
`## Housekeeping` section carries none either — `refactoring-bookkeeping.md`'s own `## Housekeeping`
section, "swept content stays in `housekeeping-template.md`" instead — and Investigation never carries
one), and a Guardrails node is never unblocked in the tree until Safety Net itself is fully resolved, so
Safety Net's `Open` can't still be non-empty at the same moment Guardrails' is — `guardrails-track.md`'s
own Scope section. The rule stays written anyway: it's still the correct fallback if a future Track ever
gains its own `Open`-shaped in-flight state.

**No wired Track is both due and eligible** → nothing is selected; step 1 (`refactor-scan`) runs with no
Track this pass, the same outcome as today whenever nothing due was found. **In practice unreachable now
that Investigation is wired** — Investigation is always due and always eligible in every case above
(section absent, a real `overdue_ratio >= 1`, or its own no-day-count `Cadence` — it always matches at
least the last), so it always fills this slot itself at minimum. Documented anyway: it's still the
correct answer for a target with no wired Tracks at all, and stays correct if a future Track is ever
added that, unlike Investigation, genuinely can go both not-due and not-eligible at once.

## Manual override

The human invoking this pass may name a specific Track directly instead of letting the ratio/tie-break
computation above run at all — this pass runs that named Track's own process unconditionally, bypassing
the one-time exception (above) exactly the same way it bypasses ordinary Eligibility/Selection; naming a
Track is the one thing that outranks the one-time exception. The
`Open`-non-empty eligibility rule still applies to a manually-named Track exactly as it would to one the
scheduler picked itself: naming Safety Net while its `Open` is non-empty still means working that `Open`
entry, never a fresh rescan. One shared invocation surface across all four Track names — naming Safety
Net, Guardrails, Housekeeping, or Investigation directly when invoking `/continuous-refactoring` (e.g.
"run the Housekeeping Track") all bypass selection the same way. This generalizes what used to be the
now-retired standalone `continuous-housekeeping` skill's own separate on-demand invocation (a human
running that skill directly instead of waiting for its cadence) to the same pattern the other three
Tracks already used — one surface, one argument, four possible names.

## Handing off to `refactor-scan`, or directly to the Housekeeping Track's own process

`refactor-scan` no longer decides for itself whether a Track is due — this step decides once, before
`refactor-scan` starts, and hands the winner down as an explicit input (or hands down "no Track" when
nothing wired was due and eligible). `refactor-scan/SKILL.md` step 4 and each Track's own reference file
(`safety-net-track.md`, `guardrails-track.md` — Scope / Judging fulfilment / Proposing and recording;
`investigation-track.md` — the single `structural-scan` gate, no judging, no `Open`) still perform their
own process exactly as documented — the tree-walk/gate mechanics are unchanged. Only "which Track (if
any) runs this pass" moved, from each Track re-deriving it independently to this one shared step.

**Housekeeping is the one exception to "hands the winner down to `refactor-scan`."** It isn't a
tooling-tree scan at all — `refactor-scan`'s own contract is "detect, never write"
(`skills/refactor-scan/SKILL.md`), and the Housekeeping Track's own process commits, opens issues, and
opens merge requests directly, the same way it always did as the now-retired standalone
`continuous-housekeeping` skill. Selecting Housekeeping hands off straight to
`skills/continuous-refactoring/references/housekeeping-track.md`, run by the orchestrator itself
(`skills/continuous-refactoring/SKILL.md` step 0c) — `refactor-scan` never runs at all this pass in that
case.

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
