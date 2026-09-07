# Selecting a structural candidate

`refactor-prioritize`'s own Select mode, run only when Rank mode recommended the `structural-scan`
node — a gate name, not a concrete candidate yet. This is a fresh dispatch, separate from Rank mode's
own (see `refactor-prioritize/SKILL.md` step 4): explore, pick one, file it minimally. The actual
grounding and grilling that turns this filed candidate into a full plan is `refactor-design`'s job
afterward (`skills/refactor-design/references/structural-candidate.md`, that file's own steps 3–4) —
not run here.

## 2. Find a structural candidate

Decide *where* to look before you look: the user named a direction (module, subsystem, hot spot) →
take it. Otherwise walk back a good stretch of `git log --oneline` for **hot spots** —
files/areas that keep coming up — and let those pull your attention first; scattered with no clear
hot spot → widen the net.

The Refactoring Notes' `bookkeeping.md` may also name a **`Refactoring goal`**
(`skills/continuous-refactoring/references/refactoring-bookkeeping.md`) — a stated target *shape*
for structural work (e.g. "convert legacy procedural code to OOP"), as opposed to `Focus areas`'
*where*. When set, treat it as an added lens on top of wherever you're looking: friction that keeps
the code away from the stated shape is a genuine signal in its own right, on top of the list below
(e.g. global mutable state and include-based coupling are strong signals when the goal names OOP).
Unset → look for friction exactly as today, no change.

Explore organically, note friction. Look for:

- **Shallow modules** — little **depth**: interface nearly as complex as the implementation. Deletion test: would deleting it concentrate complexity, or just move it? "Concentrates" is the signal.
- Missing **locality** — pure functions extracted for testability, but the real bugs hide in how they're called.
- Low **leverage** — a lot of interface surface buying little behaviour.
- Tightly-coupled modules leaking across their **seams**.
- Untested parts, or parts hard to test through their current interface.
- **Tooling pressure** — places the fulfilled tooling (PHPStan, Rector, style) keeps flagging.

Use `/codebase-design` vocabulary (module, interface, depth, seam, leverage, locality) in the candidate description — not "component," "service," "API."

More than one genuine friction spot → pick the single strongest — the same four factors Rank mode
itself uses (heat, leverage, tooling pressure, risk), one level deeper: among candidates within this
gate, not among gates. Set the rest aside for a future pass. One selection, one candidate.

## File it

File an issue labelled **`refactor:candidate`** naming **Where** (module/files), **Problem** (the
friction, in the project's domain language), **Signal** (which factor above drove the pick). This is
the minimal payload — the full plan (deepened module, seam, interface, surviving tests, slice
ordering) is `refactor-design`'s job afterward, added as a comment on this same issue.

Continue at `refactor-prioritize/SKILL.md` step 4 for the rest (dedupe check, `Pending candidates`
write).
