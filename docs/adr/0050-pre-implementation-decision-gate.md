# Pre-implementation decision gate for design-time decisions

Design and implementation already run back to back, unattended, in the same pass regardless of
`Create-mode` — that field only governs how the finished MR gets opened, after implementation has
already happened. A decision `refactor-design` makes that's genuinely hard to reverse, or a candidate
that turns out to need an actual behavior change, was previously only ever caught after the fact, in
the plan or the finished MR. Settled via a `/grill-with-docs` session
(`.scratch/design-decision-gate/issues/01-pre-implementation-review-gate.md`).

## Considered Options

- **Gate every candidate on `ready-for-agent`, universally.** Rejected — most tooling-tree nodes are
  fully specified, mechanical adoptions with no room for a decision to surface at all; forcing every
  one of them to wait a full extra pass for a human rubber-stamp would tax the loop's whole
  "continuous" premise for no corresponding safety benefit.
- **Key the gate off `Create-mode: autonomous`.** Rejected — every `Create-mode` already runs design
  and implementation unattended in the same pass; `Create-mode` only ever governs the moment the
  finished MR gets opened, which is after the risk this gate exists for has already materialized.
- **Let `refactor-design` write the breaking-change rejection itself, directly.** Rejected — breaks
  the suite's existing single-writer rule for bookkeeping/labels/`out-of-scope`
  (`refactor-learn/SKILL.md`'s own stated boundary), for the sake of skipping one hand-off.

## Decision

`refactor-design`, while grounding/grilling a structural or externally-labeled candidate, or planning
a PHPStan baseline-shrink fix, applies a new decision gate
(`skills/refactor-design/references/decision-gate.md`) before continuing to its own step 5:

- A decision meeting the same three-factor ADR bar `/domain-modeling` already uses (hard to reverse,
  surprising without context, a real trade-off), while the candidate itself stays behavior-preserving
  → the plan is still written, with a proposed default, plus an explicit open question on the issue.
  `ready-for-agent` (the existing triage label, `docs/agents/triage-labels.md`) is deliberately
  withheld. This is a **Flagged candidate** (`CONTEXT.md`).
- A genuine breaking change (the foundational "no breaking changes" rule) → `refactor-design` decides
  and writes nothing; it hands the finding to this same pass's closing `refactor-learn` call instead,
  which applies its already-existing rejection machinery (`wontfix`, a closing note or `out-of-scope/`
  entry) — the same treatment a load-bearing MR-review rejection already gets.

The orchestrator (`continuous-refactoring/SKILL.md`) skips step 5 (Implement) this pass for a flagged
candidate still missing `ready-for-agent`, or when step 4 produced a finding instead of a plan —
either way continuing straight to step 6 (Learn). `refactor-scan` (steps 2 and 3b) treats a flagged,
still-unconfirmed candidate as if it weren't pending at all — it doesn't block the rest of the
backlog, and scan looks for other work instead — but picks it back up the moment `ready-for-agent`
appears.

This is conditional, not universal: an ordinary candidate (the overwhelming majority — tooling-tree
nodes, most structural work) is entirely unaffected and keeps flowing straight through design →
implement in the same pass, exactly as before.

## Consequences

- `refactor-design/SKILL.md`, `structural-candidate.md`, and `phpstan-baseline-shrink.md` each gain a
  pointer to the new `decision-gate.md` reference, right before step 5.
- `refactor-scan/SKILL.md` steps 2 and 3b gain the flagged-candidate branch (wait vs. resume);
  `continuous-refactoring/SKILL.md` steps 1, 4, 5, and 6 gain the corresponding pass-level wiring.
- `refactor-learn/SKILL.md`'s closing call gains a second kind of input alongside the freshly opened
  MR: a design-time breaking-change finding, handled by the same rejection steps its early call
  already uses for a load-bearing MR-review rejection.
- `CONTEXT.md` gains a **Flagged candidate** entry and widens **Findings** to name `refactor-design`
  as a second origin, alongside `refactor-scan`.
- No new label — `ready-for-agent` (`docs/agents/triage-labels.md`) is reused, deliberately generic
  enough that a mechanism other than this suite's own `refactor-implement` could also act on it.
- Parked, not decided here: whether `refactor-learn` is better named/conceived as a "bookkeeping"
  skill — raised while designing the breaking-change hand-off, kept out of scope for this decision.
