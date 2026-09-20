# Writing the `## Investigation` section

Part of `refactor-learn/SKILL.md`'s closing call — the only thing this section ever gets written, no
early-call handling exists for it at all (contrast `safety-net-write.md`/`guardrails-write.md`, which
both handle a Merge/Rejection finding during the early call too). Applies only to
`## Investigation`'s own `Last scan` field; a structural candidate's merge/rejection/MR-remembering
still goes through the exact same path it always did — `Pending candidates` cleared,
`merge-requests.md`/the tracker's native link updated, `out-of-scope/structural-scan.md`-style rejection
if it ever came to that (it doesn't in practice — `structural-scan` itself is a perpetual gate, never
rejected; only *the underlying concrete candidate* a pass produced from it could be) — none of that is
`## Investigation`-section state and none of it changes here.

## `Last scan` — written whenever `investigation-track.md`'s own process actually ran this pass

`skills/refactor-scan/references/investigation-track.md` ran this pass (Investigation was the Track step
1 selected, and its own *Proposing* step was reached — whether it proposed `structural-scan`, found it
still gate-blocked, or found the Investigation Track's own precondition-free scope simply had nothing new
to say) → write `## Investigation`'s `Last scan` to today's date (`YYYY-MM-DD`), last, in the
closing call's own step ordering, same position `## Safety Net`'s/`##
Guardrails`' own `Last scan` write already occupies. **Section didn't exist yet** (first-ever scan) →
create it here: `Cadence: continuous`, `Last scan: <today>` — no `Open`/`Out-of-scope` to populate, this
section never carries either (`refactoring-bookkeeping.md`'s own `## Investigation` section).

**The scan didn't run this pass** — Investigation wasn't the Track step 1 selected, or a structural
candidate already pending was resumed via `Pending candidates` at `refactor-scan/SKILL.md` step 2 before
step 4 (and `investigation-track.md`) was ever reached — don't touch `Last scan`. Resuming existing work
isn't scanning, the same distinction `## Safety Net`'s/`## Guardrails`' own writes already draw for their
`Open`-resume path, just reached here through the global `Pending candidates` field instead of a
Track-scoped `Open` list (`investigation-track.md`'s own "Is the Track due this pass?" section).

## `Cadence` is never written here, only ever read

Unlike `## Safety Net`'s/`## Guardrails`' own `Cadence` — a hand-editable number this file never touches
either — `## Investigation`'s `Cadence` is the fixed literal `continuous`, written once on first creation
above and never changed again by anything, hand or otherwise. There is nothing to tune: Investigation
carries no interval by design (`CONTEXT.md`'s **Track** entry).

## Never writes `Open`, `Out-of-scope`, or anything else on this section's account

A structural candidate's own state was never tracked in `## Investigation` to begin with — it stays on
the issue tracker / `merge-requests.md`, exactly as it did before this section existed
(`skills/refactor-scan/references/investigation-track.md`'s own *Proposing* section). This write never
adds, removes, or reads a slug from `Open`/`Out-of-scope` (this section has neither).

## Old-schema repos

A `bookkeeping.md` with no `## Investigation` heading yet is simply a target whose Investigation Track
has never run — this write creates the section fresh, exactly as the first-ever-scan case above already
describes. Independent of `## Safety Net`/`## Guardrails`'s own presence or absence — a target can have
run its first Safety Net scan, its first Guardrails scan, neither, or both, with `## Investigation`'s own
first scan arriving on its own schedule regardless (`refactoring-bookkeeping.md`'s own "Old-schema
repos" rule).
