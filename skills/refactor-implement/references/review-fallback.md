# Review fallback — inline rules when the global skills aren't installed

Backs `refactor-implement`'s `## Fallback` section. Two independent parts:
the red → green loop discipline (used when `/tdd` isn't installed) and the
two-axis review discipline (used when the `mattpocock/skills` implement skill
isn't installed).

## Red → green loop, inline

**Rules of the loop:** *red before green* — write the failing test first,
then only enough code to pass it, without anticipating future slices or
adding speculative features; *one slice at a time* — one seam, one test, one
minimal implementation per cycle; *refactoring is not part of the loop* — it
belongs to step 4 (review), so no refactoring inside the red → green cycle.

**What makes a test worth keeping:** it verifies **behaviour through public
interfaces**, not implementation details — the code can change entirely and
the test still passes, so it survives the refactor. It must never be
**tautological** (the assertion recomputes the expected value the way the
code does, so it passes by construction and can never disagree with the code)
nor **implementation-coupled** (mocks internal collaborators, tests private
methods, or verifies through a side channel).

## Two-axis review, inline

This carries the contract `refactor-review` used to own.

- **Spec axis** — does it faithfully implement the plan on the candidate
  issue: requirements missing or partial, behaviour that wasn't asked for
  (scope creep), requirements that look implemented but wrong?
- **Standards axis** — review the diff against the repo's documented coding
  standards (see `docs/agents/domain.md`, any
  `CODING_STANDARDS.md`/`CONTRIBUTING.md`). On top of documented standards,
  carry the Fowler **smell set** below — the fixed set of smells that applies
  even when the repo documents nothing. Two rules bind it:
  - **The repo overrides.** A documented repo standard always wins; where it
    endorses something the tooling would flag, suppress the smell.
  - **Always a judgement call.** Each smell is a labelled heuristic
    ("possible Feature Envy"), never a hard violation — and, like any
    standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name** — a function, variable, or type whose name doesn't
  reveal what it does or holds. → rename it; if no honest name comes, the
  design's murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or
  file in the change. → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more
  than its own. → move the method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a
  type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain
  concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type
  recurs across the change. → replace with polymorphism, or one map both
  sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many
  files in the diff. → gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated
  reasons. → split so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for
  needs the spec doesn't have. → delete it; inline back until a real need
  shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't
  depend on. → hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward. →
  cut it, call the real target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides
  most of what it inherits. → drop the inheritance, use composition.
