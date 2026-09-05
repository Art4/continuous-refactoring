# A `Refactoring goal` field lets a human state the target shape structural work should converge toward

The suite had no way to record a general "convert this app to OOP"-style intent (ticket 54, raised by
the user directly, grilled 2026-09-05). `bookkeeping.md`'s existing `Focus areas` field only answers
*where* a scan should look first (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`);
nothing answers *what shape* the result should take once `structural-scan` unlocks and
`structural-candidate.md` starts finding and grilling a candidate.

## Considered Options

- **A new tooling-tree node** (e.g. `oop-conversion`). Rejected — every existing node has a clean
  binary Fulfilment check (a tool installed, a baseline empty). "The app is now OOP" has no such
  check and would never reliably resolve `fulfilled`, unlike e.g. a PHPStan level's empty baseline.
- **Reuse `Focus areas` as-is**, letting its free text carry both location and shape. Rejected —
  conflates two already precisely-named concepts (*where* vs. *what shape*) in a suite that is
  otherwise careful about its vocabulary (`/codebase-design`'s module/interface/depth/seam/leverage/
  locality terms, kept deliberately paradigm-neutral).
- **A structured field** (a checklist of sub-criteria: "extract classes," "remove global state," …).
  Rejected — `bookkeeping.md`'s fields are never programmatically parsed by `tooling_tree.py` or
  `scripts/` today (confirmed by inspection); a structured field would be the first to require real
  parsing, and per-criterion progress tracking, for a field meant to stay as lightweight as
  `Focus areas`.
- **A per-focus-area goal** (different shape targets for different areas). Rejected — adds a second
  axis of free text coupled to `Focus areas` for a need not yet expressed; a single global field
  covers the stated need and stays as simple as its sibling.
- **A new `refactor-prioritize` ranking factor** ("advances the stated goal"). Rejected —
  `refactor-prioritize` ranks tooling-tree nodes and the coarse `structural-scan` item itself, never
  between individual structural candidates (those are only found *after* `structural-scan` is
  chosen); a goal-alignment factor there would have essentially no resolution to act on.

## Decision

**Add `Refactoring goal`**, a new freeform field in `bookkeeping.md`, sibling to `Focus areas`, global
per target repo (not scoped to a focus area). Same treatment as `Focus areas` throughout:

- Hand-editable any time, **not** asked during the `loop-config` interview
  (`skills/continuous-refactoring/references/loop-config-interview.md`) — no filesystem signal to
  recommend from.
- Never written by `refactor-learn` — purely manual, like `Focus areas`; there is nothing discrete to
  track progress against.
- Omitted → today's behaviour, unchanged, everywhere it's read.

**Consumed only by `skills/refactor-design/references/structural-candidate.md`**, at two points:

- **Step 2** (finding a candidate): when set, it acts as an added lens alongside hot-spots and a
  user-named location — friction that keeps the code away from the stated shape (e.g. global mutable
  state when the goal names OOP) counts as a genuine signal in its own right.
- **Step 4** (grilling toward the seam): a new grill branch, "against the stated goal" — does the
  design, as shaped, actually move the code toward it? Only runs when the field is set.

**Not consumed by `refactor-prioritize`** and **not** a tooling-tree node — see *Considered Options*.

## Consequences

A human can now state a general structural direction (e.g. "convert legacy procedural code to OOP")
and have it actually bias which candidates `structural-scan` surfaces and how they're grilled, rather
than having nowhere to record that intent. No change to `tooling_tree.py` or any test fixture — the
field is pure prose, read only by the two `structural-candidate.md` steps above, following the exact
pattern `Focus areas` already established (freeform, hand-editable, unparsed by the deterministic
tree). A future need for per-area goals or discrete progress tracking would need its own follow-up
ticket rather than being retrofitted onto this field.
