# Writing the `## Guardrails` section

Part of `refactor-learn/SKILL.md`'s early call (a Guardrails Track candidate's finding) and closing
call (a Guardrails Track candidate's fresh MR, or the scan itself completing with nothing to propose)
— reached only once the call's own precondition already holds (a genuine event this pass). Applies
only to a node in the Guardrails Track's own scope
(`../../refactor-scan/references/guardrails-track.md`); every other node keeps writing whichever
section already governs it (`## Safety Net`, `Pending candidates`/`out-of-scope/`).

The write mechanics below are identical to `safety-net-write.md`'s
own — this file states the same rules, scoped to `## Guardrails` instead of `## Safety Net`, so both
sections stay independently readable without cross-referencing each other for the actual mechanics.

## Merge → remove from `Open`

The early call's "Merged" finding, for a slug listed in `## Guardrails`'s `Open`
(`../../refactor-scan/references/guardrails-track.md` handed it forward as a resumable candidate) →
remove that entry from `Open`. Nothing else about the early call's merge handling changes.

## Fulfilled at pick-up → remove from `Open`

The early call's "fulfilled at pick-up" finding — scan's `Open` walk found a `## Guardrails` node
already served when it re-ran that node's Fulfilment check right before working it (typically
adopted by hand since the last scan) — → remove that slug from `## Guardrails`' `Open`, nothing
else: no merge request, no `out-of-scope/` entry, no issue filed. The node reached the outcome its
`Open` entry was tracking; `refactor-learn/SKILL.md`'s findings list handles closing any
already-filed issue. The walk itself never removes anything — it reports the finding, this call
writes the removal.

## Rejection → remove from `Open`, write `out-of-scope/`, add the `Out-of-scope` pointer

The early call's "Closed without merge" finding (closing comments support a structural rejection) or
the closing call's design-time breaking-change finding, either one naming a Guardrails Track slug →
the existing rejection handling already writes `out-of-scope/<slug>.md` (format unchanged,
`../../continuous-refactoring/references/forge-facing-writing.md`) — additionally:

- Remove the slug from `## Guardrails`'s `Open`.
- Add it to `## Guardrails`'s `Out-of-scope`: `- <slug> — out-of-scope/<slug>.md`.
- Every node closed by that rejection (as reported by the script's `closed_by_rejection()` — nodes
  whose required or required-any ancestor is effectively rejected) also leaves `Open`, with no new
  files written for those downstream closures. The next scan will re-add them to `Open` only if the
  rejection is reversed (below).

Same symmetry every other rejection in the suite already follows. A **PHP-version reversal** (an
existing `out-of-scope/<slug>.md` naming a now-satisfied `Blocked by: PHP >= X.Y`) removes the file as
today, and also removes that slug's `Out-of-scope` pointer line here — the node goes back to being
proposable (not thereby fulfilled), so nothing about it belongs in either list until a future scan
resolves it again. Reversing a rejection makes the next scan bring those nodes back into `Open` — the
next scan's own `ordered_backlog()` re-evaluates the fulfilled set (now without the rejected ancestor)
and records the reopened nodes.

## Fresh MR → remove from `Open` (redundant with merge, kept for symmetry)

The closing call's freshly-opened-MR handling doesn't itself remove anything from `Open` — a node only
leaves `Open` once its delivering MR actually **merges** (the early call's own finding, above).

**Never touches `Pending candidates`.** A Guardrails Track candidate's in-flight state lives entirely
in `## Guardrails`'s own `Open` list
(`../../continuous-refactoring/references/refactoring-bookkeeping.md`) — `refactor-design` skips
writing that field for a candidate handed to it this way (marked self-tracking,
`../../refactor-scan/references/track-open-processing.md`), so it's never even transiently set for
one of these, and this call correspondingly never clears it on account of a Guardrails Track candidate
resolving. Also never touches `## Safety Net`'s own `Open`/`Out-of-scope` —
the two Tracks' sections are independent, each written only by its own Track's own candidates.

## Issue filed for the picked `Open` entry → record its number

This pass's `Open` walk (`../../refactor-scan/references/track-open-processing.md`) picked exactly one
workable, unfulfilled entry and handed it to `refactor-design`, which files that node's issue (unless one
already existed) — the closing call's own precondition
(`../SKILL.md`) is authorized by that hand-off alone, independent of whether
`refactor-implement` also got as far as opening a merge request this same pass. Once the issue is known
(freshly filed this pass, or already existing), rewrite that entry from a bare `- <slug>` to
`- <slug> (#<issue>)` (`../../refactor-scan/references/guardrails-track.md`'s "Filling `Open`" already
documents this as `Open`'s target shape) — the entry's only change; it stays in `Open` exactly where it
was, not touched by any of the removal cases above. Already carries `(#<issue>)` (a prior pass got this
far and was interrupted before its own closing call ran) → nothing to write, this case is idempotent.

## `Last scan` — written every time the Track's scan actually ran this pass

Whenever `guardrails-track.md`'s own process ran this pass — whether it found nothing to propose
(every node in scope already resolved) or proposed something that `Open` now tracks — write `##
Guardrails`'s `Last scan` to today's date (`YYYY-MM-DD`), last, alongside `## Safety Net`'s own write
(if that Track also ran this pass) in the closing call's own step ordering.
**Section didn't exist yet** (first-ever scan) → create it here: `Cadence: 60 days`, `Last scan: <today>`,
`Open`/`Out-of-scope` either freshly populated (something was proposed/rejected this scan) or both `-
none` (a fully-compliant target's first scan — `Open` is empty because every node is resolved). **The
scan didn't run this pass** (`Open` was already non-empty, so `guardrails-track.md` skipped straight to
working an existing entry) → don't touch `Last scan` — only a completed scan earns that write, not
merely resolving one of its `Open` entries.

## Old-schema repos

A `bookkeeping.md` with no `## Guardrails` heading yet is simply a target whose Track has never run —
this write creates the section fresh, exactly as the first-ever-scan case above already describes.
This applies whether the rest of the file is on the current schema (e.g. an already-migrated `##
Safety Net` section sitting alongside no `## Guardrails` one yet — a target whose Safety Net Track has
already run at least once but hasn't yet reached its first Guardrails Track pass) or still carries the
older `Pending candidates` shape untouched — either way, nothing about those other
fields blocks or needs understanding for this section's own first write to proceed normally.
