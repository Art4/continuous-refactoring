# Investigation gets its own single-entry `Open`, replacing the global `Pending candidates` for its own candidates

> Amended by [ADR-0069](0069-drop-the-top-level-pending-candidates-field.md): the top-level `Pending candidates` field this ADR narrowed to one remaining case is dropped.

> Amended by [ADR-0070](0070-no-bootstrap-exception-in-track-selection.md): Investigation's `Open` no longer decides whether Investigation is selected, only whether its pass resumes or scans; the claim that Guardrails' nodes are parents of `structural-scan` (so at most one `Open` is non-empty at a time) was wrong and is withdrawn.

> Supersedes [ADR-0055](0055-purpose-based-fulfilment-and-scheduled-tracks.md)'s Investigation-section
> decision: *"Investigation: no section content. The issue tracker / `merge-requests.md` stays
> authoritative, as today."* Investigation now carries its own `Open`, single-entry.
>
> Extends [ADR-0060](0060-track-open-entries-record-their-issue-number.md): Investigation's `Open` entry
> also records its issue number, the third example alongside Safety Net's and Guardrails' own.

Observed live in `Art4/legacy-todo` (bookkeeping issue #273): the running Investigation candidate sat in
the top-level `**Pending candidates:**` field, which sits structurally before every Track section — not
inside `## Investigation`. Confirmed as today's documented behavior, not a bug, but no longer the right
one:

- A Safety Net or Guardrails candidate never uses `Pending candidates` at all once its Track's own
  `Open` exists — that field is explicitly reserved for exactly one narrow case (a tooling-tree node's
  very first proposal, before its Track has scanned even once).
- A separate, just-landed fix scoped candidate intake to the Track that owns it: every non-tooling-tree
  candidate — structural, PHPStan baseline-shrink, and externally-labeled — is now picked up only in an
  Investigation pass (`refactor-scan/SKILL.md` step 3b). `Pending candidates` had, by then, become
  Investigation's field in every case that still used it; it just wasn't placed there, and — a related,
  independently discovered gap — it was read by `refactor-scan` regardless of which Track a pass had
  selected, unlike every Track-scoped `Open`.

## Decision

**`## Investigation` gains an `Open` field**, single-entry — `- <issue title> (#<issue>)`, `- none` when
empty — read and written exactly like Safety Net's/Guardrails' own `Open`, with two differences:

- **No `Out-of-scope`.** Investigation doesn't reject a fixed universe of candidates the way the tree
  does; a declined candidate's closing note on its own issue is the whole record.
- **Single-entry, not a backlog.** `refactor-prioritize`'s Select mode can draft more than one structural
  candidate's issue in a pass, but only one is ever chosen to be worked. The others stay ordinary open
  issues — `refactor-scan` step 3b re-discovers and re-ranks them fresh every Investigation pass, the
  same as any other candidate. Unlike a tree node, an Investigation candidate is always already an issue
  the moment it exists, so there's no un-filed backlog to persist the way Safety Net/Guardrails need one
  for.

**Written on every tracker, native-label ones included** — the same "on every tracker" exception the
structural/baseline-shrink case already carried under the old field name, now extended to externally-
labeled candidates too (they lose the Safety-Net/Guardrails-style native-tracker skip, since they're
Investigation's own candidates now, not tooling-tree ones). `refactor-design` sets it directly, the
moment the candidate has an issue; `refactor-learn` clears it on merge, rejection, or a design-time
breaking-change finding.

**Track-scoped resume, closing an independently found gap.** `refactor-scan`'s resume step now reads
`## Investigation`'s `Open` only when Investigation is the Track selected this pass — exactly like
Safety Net's/Guardrails' own `Open`, never Track-agnostic the way the global field was. The scheduler's
one-time exception and its ordinary Eligibility rule are updated the same way: Investigation joins
Safety Net/Guardrails in the "carries an `Open`, eligible only when empty" group, no longer grouped with
Housekeeping's "no `Open` concept at all." The tree's own gating (Guardrails' nodes are all required
parents of `structural-scan`) already guarantees at most one of the three `Open`s is non-empty at a time,
the same argument that already covered Safety Net vs. Guardrails.

**The top-level `Pending candidates` stays**, narrowed to its one remaining case: a tooling-tree node's
very first proposal, on a non-native tracker, before its own Track's `## Safety Net`/`## Guardrails`
section exists yet.

**No migration.** An existing target's in-flight `Pending candidates` entry (e.g. legacy-todo's own #279)
is not moved automatically. The next scan simply re-discovers it via step 3b like any other candidate —
cheap, and consistent with how a native tracker already recovers from an interrupted pass elsewhere in
the suite.

## Considered Options

- **A multi-entry `Open`, listing every open Investigation-owned candidate**, mirroring Safety Net/
  Guardrails literally. Rejected: every such candidate is already an issue from the moment it exists —
  unlike a tree node, which can sit unblocked for passes with no issue at all — so the set is already
  cheaply, live-queryable from the tracker itself (`refactor-scan` step 3b already does this every pass).
  A maintained list would duplicate exactly the state ADR-0055 originally wanted Investigation to avoid
  duplicating, and would need its own add/remove machinery for no benefit over a live query.
- **Renaming `Open` to `Pending` across all four Tracks**, for a uniform name. Rejected: `Open` at Safety
  Net/Guardrails means "the whole unresolved backlog, blocked and un-filed entries included" — a
  materially different concept from "the one candidate currently being worked." The rename would also
  touch dozens of doc/fixture references and file names (`track-open-processing.md`) for no functional
  gain, once Investigation's own section already uses the same field name.
- **Leave `Pending candidates` as the single field for everything, just document it as "really
  Investigation's."** Rejected: it doesn't fix the Track-agnostic read (an in-flight Investigation
  candidate could otherwise be resumed mid non-Investigation pass), and keeps a field named for one
  purpose describing a different Track's own bookkeeping.

## Consequences

- `skills/refactor-scan/references/investigation-track.md` gains a real "`Open` non-empty → resume,
  don't rescan" branch, the same shape `safety-net-track.md`/`guardrails-track.md` already have.
- `skills/refactor-learn/references/investigation-write.md` is rewritten: it now clears `Open` on
  merge/rejection, the same shape `safety-net-write.md`/`guardrails-write.md` already have (minus
  `Out-of-scope` and the walk-driven "record its issue number" step, since `refactor-design` sets the
  whole entry directly).
- `skills/continuous-refactoring/references/track-scheduler.md`'s one-time exception and Eligibility
  sections, `skills/refactor-scan/SKILL.md` step 2, and `skills/refactor-design/SKILL.md`'s
  externally-labeled/structural/baseline-shrink bullets change accordingly.
- `docs/playbooks/tracks.md`'s Track table and `CONTEXT.md`'s **Self-tracking** glossary entry are
  corrected to reflect that Investigation now carries an `Open`.
- Fixtures/harness prose asserting the old "Investigation carries no `Open` at all" invariant, or
  describing the one-time exception via `Pending candidates`, are updated to the new field.
