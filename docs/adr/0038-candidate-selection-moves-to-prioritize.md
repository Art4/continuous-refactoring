# Candidate selection moves to `refactor-prioritize`, filed before the plan exists

> Amended by [ADR-0039](0039-batch-filing-and-priority-backlog-admission.md): Select mode no longer
> picks a single strongest candidate and sets the rest aside — it files every genuine candidate found,
> sorted into a priority or capped admission tier. Everything else here (the two-dispatch mechanism,
> minimal filing, `refactor-design` grounding/grilling/commenting afterward) is unchanged.

Observed live while reviewer-loop-watching `Art4/legacy-todo`: `refactor-design` did candidate search
(structural-scan's codebase walk, or a PHPStan baseline-shrink group pick), grounding, and grilling
all inside one dispatch — the candidate's issue was filed only at the very end, together with the
finished plan. A long selection deliberation (weighing several unrelated candidates against each
other) therefore lived entirely inside one subagent's context, invisible on the tracker until it was
already over. Settled via a `/grill-with-docs` session (scan-design-split ticket 1).

## Considered Options

- **A new `refactor-select` skill**, dedicated to candidate search, dispatched between
  `refactor-prioritize` and `refactor-design`. Rejected — `structural-candidate.md`'s own candidate
  search already used the same four factors `refactor-prioritize` ranks with (heat, leverage, tooling
  pressure, risk), just one level deeper (among candidates within a chosen gate, not among gates).
  Duplicating that vocabulary in a new skill instead of reusing it added a skill without adding a
  distinct responsibility.
- **`refactor-design` writes the issue earlier, mid-context, then keeps going** in the same dispatch
  for grounding/grilling. Rejected — the context-window benefit motivating the split depends on the
  exploration never bleeding into the grounding/grilling reasoning; writing early inside the same
  subagent doesn't achieve that, only the visibility half of the goal.

## Decision

**`refactor-prioritize` gains a second mode.** Rank mode is unchanged (declarative ranking against the
tree-doc Purpose lines). When Rank mode's winner is a gate (`structural-scan`, a PHPStan
baseline-shrink family), the orchestrator dispatches `refactor-prioritize` a **second, fresh time**
(Select mode) to do the actual exploration, pick one concrete candidate, and file it minimally
(Where/Problem/Signal, or the chosen group). An already-concrete winner (an ordinary tooling-tree
node, an externally-labeled candidate) skips Select mode entirely.

**`refactor-design` simplifies.** It always receives an already-concrete, already-minimally-filed
candidate for the two gate cases — it only grounds, grills, and adds the full plan as a **comment**
on that issue, never filing a second one. Its other cases (tooling-tree node, `loop-config`,
externally-labeled candidate) are unchanged — it still files or updates those directly.

**`Pending candidates` gets written for this new handoff even on native trackers** — a narrow
exception to the existing native-tracker skip (which still applies, unchanged, to the older
design→implement handoff). Without it, `refactor-scan` step 3b would rediscover a minimally-filed,
not-yet-planned issue as an externally-labeled candidate and re-run candidate search on it, possibly
selecting something different. `refactor-scan` step 2, on resuming a `Pending candidates` entry, reads
the issue for a plan comment to know which lifecycle skill to resume at (`refactor-design` if absent,
`refactor-implement` if present) — bypassing `refactor-prioritize` either way, since the candidate is
already chosen.

## Consequences

`refactor-design`'s job narrows to grounding + grilling + writing the plan; it no longer does
candidate search at all (`skills/refactor-design/references/structural-candidate.md` keeps only its
grounding/grilling steps, `phpstan-baseline-shrink.md` keeps only its fix-planning step).
`refactor-prioritize` gains the candidate search that moved out of `refactor-design`
(`skills/refactor-prioritize/references/structural-candidate-search.md`,
`baseline-shrink-selection.md`) and the `/codebase-design` fallback reference that goes with it. Every
future candidate is visible on the tracker (Where/Problem/Signal) the moment it's chosen, not only
once its plan is finished — a side benefit noticed only after implementation: a pass interrupted
between selection and planning no longer redundantly re-runs candidate search on resume the way an
already-fully-specced pending candidate could before this change (it now resumes straight at
`refactor-design`, or skips straight to `refactor-implement` if the plan was already written).
