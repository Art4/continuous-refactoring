# Selecting a structural candidate

`refactor-prioritize`'s own Select mode, run only when Rank mode recommended the `structural-scan`
node — a gate name, not a concrete candidate yet. This is a fresh dispatch, separate from Rank mode's
own (see `refactor-prioritize/SKILL.md` step 4): explore, file every genuine candidate found, hand
forward the single strongest to continue this pass. The actual grounding and grilling that turns the
forwarded candidate into a full plan is `refactor-design`'s job afterward
(`skills/refactor-design/references/structural-candidate.md`, that file's own steps 3–4) — not run
here.

## 2. Find every genuine structural candidate

Decide *where* to look before you look: the user named a direction (module, subsystem, hot spot) →
take it. Otherwise walk back a good stretch of `git log --oneline` for **hot spots** —
files/areas that keep coming up — and let those pull your attention first; scattered with no clear
hot spot → widen the net.

The Refactoring Notes' `bookkeeping.md` may also name a **`Refactoring goal`**
(`skills/continuous-refactoring/references/refactoring-bookkeeping.md`) — a stated target *shape*
for structural work (e.g. "convert legacy procedural code to OOP"), as opposed to `Focus areas`'
*where*. When set, treat it as an added lens on top of wherever you're looking: friction that keeps
the code away from the stated shape is a genuine signal in its own right, on top of the factors below
(e.g. global mutable state and include-based coupling are strong signals when the goal names OOP).
Unset → look for friction exactly as today, no change.

Explore organically, note every genuine friction spot — checking against the full catalogue in
`skills/refactor-prioritize/references/signals.md` (structural cues: shallow modules, missing
locality, low leverage, tightly-coupled seams, untested/hard-to-test, tooling pressure; consequence
cues: security, blast radius of inaction, defect density, understandability, observability,
domain/business criticality, timing). The quality bar doesn't drop for filing more than one — a
friction spot that wouldn't have qualified alone doesn't qualify just to round out a batch.

Use `/codebase-design` vocabulary (module, interface, depth, seam, leverage, locality) in each
candidate's description — not "component," "service," "API."

## 3. Rank what was found

More than one genuine friction spot found → don't discard the rest. Rank them by the same four
factors Rank mode itself uses (heat, leverage, tooling pressure, risk), same as always for deciding
which one is strongest — that one is this pass's recommendation, carried forward per *File it* below.
The others still get filed (next step), just not pursued this pass.

## 4. Admission tier per candidate

Each found candidate sorts into one of two admission tiers by its Signal — **priority** (security or
blast radius of inaction, `signals.md`) or **capped** (everything else). The actual threshold and
admission rule live in one place, `refactor-scan/SKILL.md` step 1 (`skills/refactor-scan/SKILL.md`) —
read it fresh here rather than restating the number, so the two never drift apart. A capped candidate
this exploration finds but the cap has no room for queues for a future exploration, same as today's
single-pick behaviour, just for the overflow instead of everything past the first.

## File it

Each candidate to file gets an issue labelled **`refactor:candidate`** — plus **`refactor:priority`**
too, for a priority-tier one — naming **Where** (module/files), **Problem** (the friction, in the
project's domain language), **Signal** (which `signals.md` factor drove the pick). This is the
minimal payload — the full plan (deepened module, seam, interface, surviving tests, slice ordering)
is `refactor-design`'s job afterward, added as a comment only on the one candidate this pass actually
pursues.

Continue at `refactor-prioritize/SKILL.md` step 4 for the rest (`Pending candidates` write, naming
only the single recommended candidate — the others sit as ordinary open issues for a future pass) —
no dedupe check here, unlike a baseline-shrink group: a structural candidate's Where/Problem/Signal
has no deterministic title to dedupe against the way a fresh group's does.
