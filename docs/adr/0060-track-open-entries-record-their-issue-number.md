# A Track `Open` entry's issue number is written back once `refactor-design` files it

> Amends [ADR-0051](0051-refactor-learn-requires-a-genuine-event.md): the closing call's precondition
> gains a fourth case — a Safety Net or Guardrails Track's `Open` walk having picked a node this pass —
> alongside the existing freshly-opened-MR, design-time breaking-change, and Track-scan-ran cases.
>
> Amends [ADR-0055](0055-purpose-based-fulfilment-and-scheduled-tracks.md): closes a write-side gap
> left open by that ADR's own `Open` shape (`- <slug> (#<issue>)`, `safety-net-track.md`/
> `guardrails-track.md`'s "Filling `Open`") — the format was specified there, but no write ever
> produced it once a node's issue existed.

`safety-net-write.md`/`guardrails-write.md` define exactly three writes to a Track's `Open` list:
Merge removes an entry, Fulfilled-at-pick-up removes one, Rejection removes one and adds an
`Out-of-scope` pointer. None of them ever *adds* the `(#<issue>)` a node's entry is supposed to carry
once `refactor-design` files it — confirmed by reading both files end to end. `refactor-scan`'s `Open`
walk (`track-open-processing.md`) hands its one workable pick to `refactor-design`, which files the
issue (or finds one already filed); nothing carries that number back into `Open`.

Observed live against a real target repo: `## Safety Net`'s `Open` held six bare slugs, none linked.
`refactor-scan`'s next walk had to re-derive, per entry, whether a candidate issue already existed —
required by the walk's own workability check 2 (a filed issue's `needs-info` label) — by searching the
ticket directory instead of reading a link off the `Open` line. One of the six had in fact already been
filed and fully planned, undiscoverable from `bookkeeping.md` alone.

Tracing the gap further surfaced a second, independent bug in the same code path:
`refactor-design/SKILL.md` step 5, as written, is blind to the Safety Net/Guardrails split entirely (it
has no vocabulary for either) and sets the global `Pending candidates` field for *every* freshly-filed
tooling-tree node on a non-native tracker — including a Track `Open`-walk node. `safety-net-write.md`/
`guardrails-write.md` already claim the opposite ("Never touches `Pending candidates`"). Left as is,
this can also let two independent resume mechanisms both pick up the same candidate after an
interrupted pass — `refactor-scan/SKILL.md` step 2's own `Pending candidates` resume (`track-open-
processing.md`'s own header: "`Pending candidates` still resumes the same way as before, tracked
separately") alongside the Track's own `Open`-based resume.

## Considered Options

- **Have `refactor-design` itself write the `(#<issue>)` annotation**, mirroring how it already writes
  `Pending candidates` for an ordinary tooling-tree node. Rejected: would require `refactor-design` to
  know it's handling a Safety Net/Guardrails Track node specifically — the vocabulary boundary between
  "grounds and plans a candidate" and "knows which scheduled Track owns it" that this suite has kept
  separate throughout (`refactor-design/SKILL.md` names neither concept anywhere today), and reusing
  it to fix the `Pending candidates` bug would mean design just learned about Tracks in order to avoid
  touching a field, then immediately needing that same knowledge to write a different one.
- **`refactor-design` keeps setting `Pending candidates` for these nodes too; a later step reconciles it
  against `Open` and moves the reference.** Rejected: still requires `refactor-design` to (at minimum)
  set a field the Track write-files already document as never touched, and reopens exactly the
  interrupted-pass double-resume risk above for as long as the reconciliation hasn't run yet.
- **A new, explicit "self-tracking" marker on the hand-off, generic enough that `refactor-design` never
  learns what it means.** Accepted. `refactor-scan`'s `Open` walk already hands its pick to
  `refactor-design` "the same as usual" (`track-open-processing.md`); marking that hand-off
  self-tracking reuses the one distinction `refactor-design` already makes for a structural/
  baseline-shrink candidate ("Select mode already set it... don't touch it here") — widened to a
  second origin, without design ever knowing it's a Track. `refactor-design` stays exactly as
  Track-blind as before; the fix lives entirely in `refactor-scan`'s references and `refactor-learn`'s
  write files, which already carry that knowledge.
- **Write the `(#<issue>)` annotation from the early call, tied to a new "issue filed" finding
  `refactor-scan` reports next pass.** Rejected: delays the write by a full pass for no reason — the
  walk already knows, this pass, which node it picked and that `refactor-design` files (or finds) its
  issue in the same pass, before the closing call runs.

## Consequences

`refactor-scan`'s `Open` walk hands its picked, unfulfilled entry to `refactor-design` marked
self-tracking (`track-open-processing.md`). `refactor-design/SKILL.md` step 5 treats that marker
exactly like a structural/baseline-shrink candidate's own: skip `Pending candidates` entirely, no new
vocabulary, no awareness of *why*. `refactor-learn/SKILL.md`'s closing-call precondition gains a fourth
case — this pass's `Open` walk having picked a node — authorizing only the matching write, independent
of whether `refactor-implement` also opened a merge request this same pass. `safety-net-write.md`/
`guardrails-write.md` each gain an "Issue filed for the picked `Open` entry → record its number"
section: rewrite that bare `- <slug>` to `- <slug> (#<issue>)`, idempotent if already annotated.

Duplicate filing was considered and set aside: `refactor-design` already prevents it independently, by
title (`Tooling tree: <Name>`), before ever reaching step 5 — this ADR only removes an avoidable
per-pass search cost and makes `bookkeeping.md` show the true state at a glance, it does not change
correctness there.
