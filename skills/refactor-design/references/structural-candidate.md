# Grounding and grilling a structural candidate

`refactor-design` steps 3–4, run only for a **structural candidate** — a concrete candidate
`refactor-prioritize` already selected and minimally filed (Where/Problem/Signal) via its own Select
mode (`skills/refactor-prioritize/references/structural-candidate-search.md`, that file's own step 2
— the candidate *search* itself no longer lives here). An ordinary tooling-tree node skips straight
to step 5 — see `refactor-design/SKILL.md` step 1. Step numbering matches
`skills/refactor-design/SKILL.md` so its own cross-references ("step 4's side effects") still
resolve, and `refactor-prioritize/references/structural-candidate-search.md`'s "step 2" still
resolves too.

## 3. Ground in the candidate

Read the code the candidate names (and the issue `refactor-prioritize` filed — Where/Problem/Signal).
Read `CONTEXT.md` and the ADRs in the area. Understand *why* it's a candidate before proposing
anything.

## 4. Grill toward the seam

Run `/grilling` on the candidate, along these branches:

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
