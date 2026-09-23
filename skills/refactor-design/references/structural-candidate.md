# Grounding and grilling a structural candidate

`refactor-design` steps 3–4, run only for a **structural candidate** — a concrete candidate
`refactor-prioritize` already selected and minimally filed (Where/Problem/Signal) via its own Select
mode (`../../refactor-prioritize/references/structural-candidate-search.md`, that file's own step 2
— the candidate *search* itself no longer lives here). An ordinary tooling-tree node skips straight
to step 5 — see `refactor-design/SKILL.md` step 1. Step numbering matches
`../SKILL.md` so its own cross-references ("step 4's side effects") still
resolve, and `refactor-prioritize/references/structural-candidate-search.md`'s "step 2" still
resolves too.

## 3. Ground in the candidate

Read the code the candidate names (and the issue `refactor-prioritize` filed — Where/Problem/Signal,
**and any comments already on it** — a human may have added context, a constraint, or a correction
since it was filed). Read `CONTEXT.md` and the ADRs in the area. Understand *why* it's a candidate
before proposing anything.

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

While grilling any of these branches: a decision meeting the ADR bar, or the seam turning out to
require an actual behavior change → `decision-gate.md`, before
continuing to step 5.

Side effects happen inline as decisions crystallise (per `/domain-modeling`): naming a module after a concept not in `CONTEXT.md` → add the term. User rejects a design with a load-bearing reason a future scan shouldn't re-suggest → offer an ADR.

**Decision trail.** Once the grilling frontier above is empty, before continuing to step 5: for every
question raised while grilling that met the same three-factor ADR bar the decision gate uses (hard to
reverse, surprising without context, a real trade-off) — regardless of whether it was answered live
here or deferred to the decision gate above — post one bundled comment on the issue naming the
question and the answer reached (`CONTEXT.md`'s **Decision trail**). This is separate from the
decision gate: the gate blocks progress on an unresolved, unattended decision; this only records one
already resolved, and never blocks anything. No qualifying question this pass → no comment. Follow
`../../continuous-refactoring/references/forge-facing-writing.md` like any other forge-facing text.
