# Investigation Track scan

`refactor-scan/SKILL.md` step 4's own Investigation-specific process: whether the Track is due this
pass and, once due, whether to resume its in-flight candidate(s) or scan fresh — the one real
difference from `safety-net-track.md`/`guardrails-track.md` is that a fresh scan here only ever proposes
one fixed node, `structural-scan`, never a backlog of many. Vocabulary: `CONTEXT.md` (**Track**, **Investigation**, **Hot spot**,
**Deepening**).

## Scope

Exactly one node: `structural-scan` (`tooling-tree/structural-scan.md`).
Its own Fulfilment check, edge semantics (`resolved` parents, not `required`/`recommended`), and MR scope
are completely unchanged by any of this — this file only changes *when* `structural-scan` gets proposed,
never how its own gate works. No Purpose-based judgement applies here at all: per the spec's
own "Out of Scope" ("Extending Purpose-based recognition to Investigation's own candidate search — that
Track was never fulfilment-check-driven to begin with, so it's unaffected"), `structural-scan`'s
Fulfilment check already reads its resolved-parents' own state (fulfilled or rejected, either way
resolved) — there's no dependency-name match here to replace with judgement, unlike every Safety Net or
Guardrails node.

## Is the Track due this pass?

Decided once, before `refactor-scan` even starts — the orchestrator's own Track-selection step
(`../../continuous-refactoring/references/track-scheduler.md`, `../../continuous-refactoring/SKILL.md`
step 1) reads `bookkeeping.md`'s `## Investigation` section
(`../../continuous-refactoring/references/refactoring-bookkeeping.md`) and hands the winner to
`refactor-scan` as an explicit input, exactly as it does for every other wired Track. This section covers
only what this Track does with that decision — it never re-derives due-ness itself:

- **This Track wasn't the one step 1 selected** → nothing in this file runs this pass; `structural-scan`
  is **not** proposed this pass, even if its own resolved-edge gate would otherwise allow it —
  `refactor-scan` continues with whichever Track was actually selected instead (or with everything else
  it already does, if none was due). This is the actual behavior change here: before this Track existed,
  `structural-scan` was proposed unconditionally, every pass, the moment its resolved-edge parents
  cleared, with no Track gate at all.
- **Selected, `Open` non-empty** → the same "resume before propose fresh" discipline Safety Net/
  Guardrails apply to their own `Open`: don't rescan for brand-new work while any entry remains.
  `refactor-scan/SKILL.md` step 2 already does this before step 4 is ever reached — this file's own
  process doesn't run this pass at all (skip straight to `refactor-scan/SKILL.md`'s `## Output`), the
  same way `safety-net-track.md`/`guardrails-track.md` skip their own scan while their `Open` is
  non-empty. Unlike those two, resuming here is never a Fulfilment-based workability walk
  (`track-open-processing.md`) — an Investigation entry always already carries a plan by construction
  (`refactor-design` is what adds it), so step 2's existing per-entry logic (plan + `ready-for-agent` →
  implement; plan + `needs-info` → flagged, checked for a newer human comment) applies to each entry in
  turn, top to bottom, same as reading one entry always has been. Advance at most one entry per pass —
  the same "one candidate per pass" discipline the suite-wide two-merge-request cap already assumes
  (`../../continuous-refactoring/references/refactoring-bookkeeping.md`'s *Why more than one entry*). An
  entry already past design and implement, sitting on an open, unmerged PR with no reviewer activity,
  has nothing to advance here — step 3's own reconciliation is what watches it, not this read. No entry
  has anything to advance this pass → report that; `Open` still being non-empty still means no fresh scan.
- **Selected, `Open` empty** → continue below; this is a genuine scan.

## Proposing

Reached only with `Open` empty (above) → propose `structural-scan` by Name, exactly the same mechanics
`refactor-scan/SKILL.md` step 4 always used for it before this Track existed: `structural-scan` is
proposable only when:

1. The Safety Net section exists in `bookkeeping.md` and its `Open` is empty, **plus**
2. Every node with a `resolved` edge into `structural-scan` is resolved — fulfilled, or explicitly
   rejected under `out-of-scope/` (a recorded rejection counts as resolved).

The actual codebase walk that turns this gate name into one concrete candidate is still
`refactor-prioritize`'s Select mode's own job
(`../../refactor-prioritize/references/structural-candidate-search.md`), run only once this proposal wins ranking — nothing about that pipeline
changes here. Once filed, the concrete candidate's own open/done/rejected state lives entirely on the
issue tracker / `merge-requests.md`; in flight, it's tracked in `## Investigation`'s own `Open`
(`refactoring-bookkeeping.md`) — `refactor-design` adds an entry for it the moment the candidate has an
issue, on every tracker, alongside any other entry already there
(`../../refactor-design/SKILL.md`).

`structural-scan` still gate-blocked (its own resolved-parents not yet all resolved — typically because
Safety Net or Guardrails hasn't fully closed yet) → nothing to propose, even though this Track was
selected. This is expected, not an error: Investigation has no gating precondition of its own (per the
spec's Scheduling algorithm decision, "always eligible"), so the scheduler can hand it a pass before
Onboarding finishes — `structural-scan`'s own unchanged resolved-edge gate is what actually withholds it
until then, the same gate that already did this job before Track selection existed.

**This file's own process actually running this pass is what counts as a completed scan** — reaching the
*Proposing* step above at all, whether it proposed `structural-scan` or found it still gate-blocked:
`refactor-learn`'s closing call writes `## Investigation`'s `Last scan` whenever that happened
(`../../refactor-learn/references/investigation-write.md`). **A structural candidate resumed via
`## Investigation`'s own `Open`** (above) **never reaches the `Proposing` step at all** — the same
"resuming isn't scanning" discipline `safety-net-track.md`'s/`guardrails-track.md`'s own `Open` resume
path already follows, so resolving that candidate this pass, on its own, doesn't write `Last scan`
either.
