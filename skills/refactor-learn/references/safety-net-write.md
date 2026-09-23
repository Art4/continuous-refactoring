# Writing the `## Safety Net` section

Part of `refactor-learn/SKILL.md`'s early call (a Safety Net Track candidate's finding) and closing
call (a Safety Net Track candidate's fresh MR, or the scan itself completing with nothing to propose) —
reached only once the call's own precondition already holds (a genuine event this pass). Applies only to
a node in the Safety Net Track's own scope
(`../../refactor-scan/references/safety-net-track.md`); every other node keeps writing
`Pending candidates`/`out-of-scope/` exactly as `refactor-learn/SKILL.md` already documents.

## Merge → remove from `Open`

The early call's "Merged" finding, for a slug listed in `## Safety Net`'s `Open` (`skills/refactor-scan/
references/safety-net-track.md` handed it forward as a resumable candidate) → remove that entry from
`Open`. Nothing else about the early call's merge handling changes (mark the candidate `done`, close the
issue, drop the `merge-requests.md` entry if non-native-tracker — `refactor-learn/SKILL.md`'s own
`## Process`).

## Fulfilled at pick-up → remove from `Open`

The early call's "fulfilled at pick-up" finding — scan's `Open` walk
(`../../refactor-scan/references/track-open-processing.md`) re-ran a node's Fulfilment check right
before working it and found the node already served, typically adopted by hand since the last scan —
→ remove that slug from `## Safety Net`'s `Open`. No merge request exists to remember, no rejection
to record, nothing filed: the node is genuinely fulfilled, the exact outcome its `Open` entry existed
to reach (`refactor-learn/SKILL.md`'s own findings list closes any already-filed issue for it). Scan
itself never writes this removal — it only reports the finding; the removal is this call's write, the
same split the merge case above already follows.

## Rejection → remove from `Open`, write `out-of-scope/`, add the `Out-of-scope` pointer

The early call's "Closed without merge" finding (closing comments support a structural rejection) or the
closing call's design-time breaking-change finding, either one naming a Safety Net Track slug → the
existing rejection handling already writes `out-of-scope/<slug>.md` (format unchanged,
`../../continuous-refactoring/references/forge-facing-writing.md`) — additionally:

- Remove the slug from `## Safety Net`'s `Open`.
- Add it to `## Safety Net`'s `Out-of-scope`: `- <slug> — out-of-scope/<slug>.md`.
- Every node closed by that rejection (as reported by the script's `closed_by_rejection()` — nodes
  whose required or required-any ancestor is effectively rejected) also leaves `Open`, with no new
  files written for those downstream closures. The next scan will re-add them to `Open` only if the
  rejection is reversed (below).

Same symmetry every other rejection in the suite already follows — merge removes from the in-flight
list, rejection removes from the in-flight list and adds a pointer to the durable record. A **PHP-version
reversal** (an existing `out-of-scope/<slug>.md` naming a now-satisfied `Blocked by: PHP >= X.Y`) removes
the file as today, and also removes that slug's `Out-of-scope` pointer line here — the rejection is
reversed, the node goes back to being proposable (not thereby fulfilled), so nothing about it belongs in
either list until a future scan resolves it again. Reversing a rejection makes the next scan bring those
nodes back into `Open` — the next scan's own `ordered_backlog()` re-evaluates the fulfilled set (now
without the rejected ancestor) and records the reopened nodes.

## Fresh MR → remove from `Open` (redundant with merge, kept for symmetry)

The closing call's freshly-opened-MR handling doesn't itself remove anything from `Open` — a node only
leaves `Open` once its delivering MR actually **merges** (the early call's own finding, above). What
*does* happen at this point, same as for any other node: the MR is remembered (`merge-requests.md` /
the tracker's native link).

**Never touches `Pending candidates`.** A Safety Net Track candidate's in-flight state lives entirely in
`## Safety Net`'s own `Open` list (`../../continuous-refactoring/references/refactoring-bookkeeping.md`)
— `refactor-design` skips writing that field for a candidate handed to it this way (marked
self-tracking, `../../refactor-scan/references/track-open-processing.md`), so it's never even
transiently set for one of these, and this call correspondingly never clears it on account of a Safety
Net Track candidate resolving.

## Issue filed for the picked `Open` entry → record its number

This pass's `Open` walk (`../../refactor-scan/references/track-open-processing.md`) picked exactly one
workable, unfulfilled entry and handed it forward — `refactor-loop` created that node's issue from scan's draft (unless one
already existed) before `refactor-design` ran — the closing call's own precondition
(`../SKILL.md`) is authorized by that hand-off alone, independent of whether
`refactor-implement` also got as far as opening a merge request this same pass. Once the issue is known
(freshly filed this pass, or already existing), rewrite that entry from a bare `- <slug>` to
`- <slug> (#<issue>)` (`../../refactor-scan/references/safety-net-track.md`'s "Filling `Open`" already
documents this as `Open`'s target shape) — the entry's only change; it stays in `Open` exactly where it
was, not touched by any of the removal cases above. Already carries `(#<issue>)` (a prior pass got this
far and was interrupted before its own closing call ran) → nothing to write, this case is idempotent.

## `Last scan` — written every time the Track's scan actually ran this pass

Whenever `safety-net-track.md`'s own process ran this pass — whether it found nothing to propose (every
node in scope already resolved) or proposed something that `Open` now tracks — write `## Safety Net`'s
`Last scan` to today's date (`YYYY-MM-DD`), last, in the closing call's own
step ordering. **Section didn't exist yet** (first-ever scan) → create it here: `Cadence: 90 days`, `Last
scan: <today>`, `Open`/`Out-of-scope` either freshly populated (something was proposed/rejected this
scan) or both `- none` (a fully-compliant target's first scan — `Open` is empty because every node is
resolved). **The scan didn't run this pass** (`Open` was already non-empty, so `safety-net-track.md`
skipped straight to working an existing entry) → don't touch `Last scan` — only a completed scan earns
that write, not merely resolving one of its `Open` entries.

## Old-schema repos

A `bookkeeping.md` with no `## Safety Net` heading yet is simply a target whose Track has never run —
this write creates the section fresh, exactly as the first-ever-scan case above already describes. The
file's pre-existing `Pending candidates` content (old schema or otherwise) is untouched
by this write — those fields keep meaning whatever they already mean for every node outside this Track's
scope.
