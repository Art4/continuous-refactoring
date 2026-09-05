# Finding and grounding a structural candidate

`refactor-design` steps 2–4, run only for the `structural-scan` node (an ordinary tooling-tree node skips straight to step 5 — see step 1). Step numbering matches `skills/refactor-design/SKILL.md` so its step-5 cross-references ("step 2's friction signal") still resolve.

## 2. Find a structural candidate

Only runs here, for the node actually chosen — not speculatively on every pass.

Decide *where* to look before you look: the user named a direction (module, subsystem, hot spot) → take it. Otherwise walk back a good stretch of `git log --oneline` for **hot spots** — files/areas that keep coming up — and let those pull your attention first; scattered with no clear hot spot → widen the net.

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

More than one genuine friction spot → pick the single strongest (same factors as `refactor-prioritize`: heat, leverage, tooling pressure, risk), set the rest aside for a future pass. One selection, one candidate.

## 3. Ground in the candidate

Read the code the candidate names (and, for a resumed candidate, the issue). Read `CONTEXT.md` and the ADRs in the area. Understand *why* it's a candidate before proposing anything.

## 4. Grill toward the seam

Structural candidates only — skip for a tooling-tree node. Run `/grilling` on the candidate, along these branches:

- **The deepened module** — what does it become, what is its one job, what disappears behind it?
- **The seam** — where's the public boundary, tested through what?
- **The interface** — what does it expose, does it stay deep (implementation complexity > interface complexity)?
- **Locality** — what moves together, what must *not* spread?
- **Tests that survive** — which stay, which are rewritten, which new ones appear at the seam?
- **Against the stated goal** — only when `bookkeeping.md` names a `Refactoring goal`: does the
  deepened module, as designed, actually move the code toward it? A design that satisfies every
  other branch but drifts away from (or simply ignores) a stated goal is worth reconsidering. No
  goal set → skip this branch, same as today.

Side effects happen inline as decisions crystallise (per `/domain-modeling`): naming a module after a concept not in `CONTEXT.md` → add the term. User rejects a design with a load-bearing reason a future scan shouldn't re-suggest → offer an ADR.
