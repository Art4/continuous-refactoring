# Writing the `## Investigation` section

Part of `refactor-learn/SKILL.md`'s early call (a structural, PHPStan baseline-shrink, or
externally-labeled candidate's finding) and closing call (that candidate's fresh MR, or the scan itself
completing with nothing to propose) — reached only once the call's own precondition already holds (a
genuine event this pass). Applies only to a candidate `refactor-scan/SKILL.md` step 3b routes to an
Investigation pass (`../../refactor-scan/references/investigation-track.md`); every other candidate
keeps writing its own Track's section and `out-of-scope/` exactly as `refactor-learn/SKILL.md`
already documents.

## Merge → remove that one entry from `Open`

The early call's "Merged" finding, for a candidate named among `## Investigation`'s own `Open` entries
(`refactor-scan/SKILL.md` step 3 handed it forward as a resumable candidate) → remove *exactly that
entry*, leaving any other entry untouched; `Open` reads `- none` only once the last entry is gone.
Nothing else about the early call's merge handling changes (mark the candidate `done`, close the issue,
drop the `merge-requests.md` entry if there is one — `refactor-learn/SKILL.md`'s own `## Process`).

## Rejection → remove that one entry from `Open` (no `out-of-scope/` — Investigation carries none)

The early call's "Closed without merge" finding, or the closing call's design-time breaking-change
finding, either one naming a candidate among `## Investigation`'s `Open` entries → remove that one entry
the same way, other entries untouched. Unlike a Safety Net or Guardrails Track slug, nothing is written
to `out-of-scope/`: Investigation doesn't reject a fixed set of candidates the way the tree does — a
declined candidate's own closing note on the issue
(`../../continuous-refactoring/references/forge-facing-writing.md`) is the whole record.

## Fresh MR → nothing extra (redundant with merge, kept for symmetry)

The closing call's freshly-opened-MR handling doesn't itself touch `Open` — a candidate only leaves
`Open` once its own delivering MR actually **merges** (above), and only its own entry leaves; any other
entry already there is unaffected either way. What *does* happen at this point, same as for any other
candidate: the MR is remembered (`merge-requests.md` / the tracker's **Linked merge request**).

## `refactor-design` adds an entry to `Open` — this call never does

Unlike `## Safety Net`'s/`## Guardrails`' own `Open`, which starts as a bare slug and only gains its
issue number once one is filed, an `## Investigation` `Open` entry is only ever written once its
candidate already has an issue — `refactor-design` appends it directly, `- <issue title> (#<issue>)`,
the moment it writes that candidate's plan (`../../refactor-design/SKILL.md`) — on every tracker,
alongside any entry already there (more than one candidate can be in flight
at once, bounded by the suite-wide two-merge-request cap, `../../continuous-refactoring/references/refactoring-bookkeeping.md`'s *Why more than one entry*). This call only ever *removes* an
entry (above); it never adds or rewrites one itself.

## `Last scan` — written whenever `investigation-track.md`'s own process actually ran this pass

`../../refactor-scan/references/investigation-track.md` ran this pass (Investigation was the Track step
1 selected, its own `Open` was empty, and its own *Proposing* step was reached — whether it proposed
`structural-scan`, found it still gate-blocked, or found the Investigation Track's own
precondition-free scope simply had nothing new to say) → write `## Investigation`'s `Last scan` to
today's date (`YYYY-MM-DD`), last, in the closing call's own step ordering, same position `## Safety
Net`'s/`## Guardrails`' own `Last scan` write already occupies. **Section didn't exist yet** (first-ever
scan) → create it here: `Cadence: continuous`, `Last scan: <today>`, `Open: - none`.

**The scan didn't run this pass** — Investigation wasn't the Track step 1 selected, or its own `Open`
was non-empty so `investigation-track.md` skipped straight to resuming its entries instead of
reaching *Proposing* — don't touch `Last scan`. Resuming existing work isn't scanning, the same
distinction `## Safety Net`'s/`## Guardrails`' own writes already draw for their `Open`-resume path.

## `Cadence` is never written here, only ever read

Unlike `## Safety Net`'s/`## Guardrails`' own `Cadence` — a hand-editable number this file never touches
either — `## Investigation`'s `Cadence` is the fixed literal `continuous`, written once on first creation
above and never changed again by anything, hand or otherwise. There is nothing to tune: Investigation
carries no interval by design (`CONTEXT.md`'s **Track** entry).

## Never writes `Out-of-scope` — this section doesn't carry one

A rejected Investigation candidate's record is the closing note on its own issue, never a durable
`out-of-scope/` entry — Investigation doesn't reject a fixed universe of candidates the tree does, so
there's nothing to permanently exclude going forward (`../../refactor-design/references/decision-gate.md`).

## Old-schema repos

A `bookkeeping.md` with no `## Investigation` heading yet is simply a target whose Investigation Track
has never run — this write creates the section fresh, exactly as the first-ever-scan case above already
describes, `Open: - none` included regardless of whatever the file's pre-existing top-level `Pending
candidates` still names (untouched by this write; that field keeps meaning whatever it already means for
a tooling-tree node outside every Track's own `Open`). Independent of `## Safety Net`/`## Guardrails`'s
own presence or absence — a target can have run its first Safety Net scan, its first Guardrails scan,
neither, or both, with `## Investigation`'s own first scan arriving on its own schedule regardless
(`refactoring-bookkeeping.md`'s own "Old-schema repos" rule).
