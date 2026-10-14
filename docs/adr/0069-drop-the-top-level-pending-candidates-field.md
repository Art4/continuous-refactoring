# The top-level `Pending candidates` field is dropped

> Superseded by [ADR-0074](0074-state-lives-in-the-tracker-found-by-search.md): the document the field
> lived in is gone.

> Amends [ADR-0064](0064-bookkeeping-state-lives-in-an-issue-or-a-local-file.md) and
> [ADR-0065](0065-investigation-gets-its-own-open.md): both kept the field "for now" and deferred
> dropping it to a later change — this is that change. Supersedes
> [ADR-0029](0029-native-tracker-design-skips-the-pending-candidate-write.md), whose per-tracker rule
> for the write has nothing left to govern, and the hand-off marker
> [ADR-0060](0060-track-open-entries-record-their-issue-number.md) introduced to suppress it.

`Pending candidates` was the suite's original resume marker: one issue, named in the bookkeeping
document, that the next `refactor-scan` resumes before proposing anything fresh. Each Track has since
taken its own candidates out of it — Safety Net and Guardrails into their own `Open` (ADR-0055,
ADR-0060), Investigation into its own `Open` (ADR-0065, ADR-0068) — and ADR-0065 narrowed the field to
"a tooling-tree node's very first proposal, on a non-native tracker, before its Track's section exists
yet."

That last case no longer occurs. Every proposable tooling-tree node belongs to a Track
(`structural-scan` is a gate, handled through Investigation; `git`, `onboarding-setup` and the language
recognition gate are never proposed). A Track's scan designs nothing — it records the complete backlog
in `Open`, files no issue, and ends. A Track node therefore reaches `refactor-design` only through the
`Open` walk, which marked it **self-tracking** precisely so design would skip the write. The field had
no writer left, yet six skills still read it, cleared it or explained why they didn't touch it; two of
those explanations had gone stale and contradicted the rest.

## Decision

**The field is removed from the suite**: no skill reads it, writes it or mentions it.
`refactor-scan`'s resume step reads only the selected Track's own `Open`.

**The self-tracking hand-off marker is removed with it.** Its only meaning was "don't set
`Pending candidates`"; with nothing to suppress, the `Open` walk hands its node forward like any other
candidate, and `refactor-design` writes no bookkeeping for a tooling-tree node at all.

**No migration.** A bookkeeping document that still carries the field keeps it, unread and untouched —
the same rule every other old-schema field follows. A value still set in it is not carried over: the
next scan rediscovers the issue through its ordinary issue-backed-candidate detection, as ADR-0065
already decided for Investigation's own leftovers.

## Consequences

- One path changes behaviour. An already-existing issue titled `Tooling tree: <Name>` — pre-filed by
  an older suite version, or created by hand — can still reach `refactor-design` as an ordinary ranked
  proposal rather than through the `Open` walk. On a non-native tracker design used to set the field
  for it; now a pass interrupted between design and implement leaves that issue to be found and ranked
  again next pass, instead of being resumed unconditionally. A native tracker has behaved this way
  since ADR-0029. Nothing is lost: every non-native tracker uses the Local Markdown mechanics, whose
  issues the scan can list.
- `refactor-learn`'s closing call no longer clears a resume marker when a merge request is freshly
  opened. A candidate's `Open` entry — its Track's, or Investigation's — leaves only once that merge
  request merges or the candidate is rejected, as each Track's own write rules already said; the
  skill's summary text had still described the older clear-on-open behaviour for Investigation.
- The old-schema fixtures and unit tests keep seeding the field and keep asserting it survives a pass
  untouched.

## Considered Options

- **Keep it as a single "in flight" entry for every candidate.** Rejected: each Track's `Open` already
  is that, scoped to the Track that owns the work and able to hold more than one entry (ADR-0068); a
  second, global marker is exactly what ADR-0065 moved away from.
- **Have `refactor-learn` delete the line from existing documents on its next write.** Rejected: a new
  write rule for a field nothing reads, against the standing rule that old-schema content is never
  migrated.
- **Keep exact resume for the residual path by adding such an issue to its Track's `Open`.** Rejected
  for now: `Open` already lists the node by slug, and matching a hand-filed issue to it is a separate
  behaviour change with its own questions; re-ranking loses nothing.
