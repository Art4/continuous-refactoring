# Investigation Track scan

`refactor-scan/SKILL.md` step 4's own Investigation-specific process: whether the Track is due this
pass, and — the one difference from `safety-net-track.md`/`guardrails-track.md` — the complete absence
of anything else to decide. Vocabulary: `CONTEXT.md` (**Track**, **Investigation**, **Hot spot**,
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
- **Selected** → continue below. Investigation carries no `Open` precondition (unlike Safety Net/
  Guardrails, `refactoring-bookkeeping.md`'s own `## Investigation` section) — there is no "Open
  non-empty, resume instead of rescan" branch here. A structural candidate already in flight is tracked
  by the ordinary `Pending candidates` field instead (see *Proposing* below), and `refactor-scan/SKILL.md`
  step 2 already resumes it before step 4 is ever reached, same as it always has — independent of Track
  selection, unaffected by any of this file.

## Proposing

Selected this pass, and `Pending candidates` didn't already resume a structural candidate (step 2) →
propose `structural-scan` by Name, exactly the same mechanics `refactor-scan/SKILL.md` step 4 always
used for it before this Track existed: `structural-scan` is proposable only when:

1. The Safety Net section exists in `bookkeeping.md` and its `Open` is empty, **plus**
2. Every node with a `resolved` edge into `structural-scan` is resolved — fulfilled, or explicitly
   rejected under `out-of-scope/` (a recorded rejection counts as resolved).

The actual codebase walk that turns this gate name into one concrete candidate is still
`refactor-prioritize`'s Select mode's own job
(`../../refactor-prioritize/references/structural-candidate-search.md`), run only once this proposal wins ranking — nothing about that pipeline
changes here. Once filed, the concrete candidate's own open/done/rejected state lives entirely on the
issue tracker / `merge-requests.md`, tracked in flight via the ordinary `Pending candidates` field
(`refactoring-bookkeeping.md`) the same way any other candidate already is — `## Investigation` never
gains an `Open` entry for it.

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
`Pending candidates` at `refactor-scan/SKILL.md` step 2 never reaches this file at all** — step 4 skips
outright once step 2 already has a pending candidate to resume (same as it always has, Track selection
notwithstanding) — so resolving that candidate this pass, on its own, doesn't write `Last scan` either;
the same "resuming isn't scanning" discipline `safety-net-track.md`'s/`guardrails-track.md`'s own `Open`
resume path already follows, just reached here via the global `Pending candidates` field instead of a
Track-scoped `Open` list.
