---
name: refactor-review
description: Verify a completed refactor — tests green, baseline tools clean, and a two-axis review of the diff. Part of the continuous refactoring loop.
---

# Refactor Review

Verify a completed refactor along two axes, reported separately so neither masks the other:

- **Standards** — does the diff conform to this repo's documented standards *and* the baseline tooling?
- **Spec** — does it faithfully implement the plan on the candidate issue?

The tooling floor (PHPStan, Rector, style) sets its own standards — those are *minimums*, enforced by CI; the review adds what tools can't see.

## Process

### 1. Verify the floor

Run the baseline tooling and the test suite over the diff. Confirm green. If the floor fails, the refactor is not done — send it back to `refactor-implement`.

### 2. Standards axis

Review the diff against this repo's documented coding standards (see `docs/agents/domain.md`, any `CODING_STANDARDS.md`/`CONTRIBUTING.md`). On top of documented standards, carry the Fowler **smell baseline** and the standards-axis rules from `/code-review` — use it if installed, otherwise the inline baseline and rules in `## Fallback` below govern.

### 3. Spec axis

Review the diff against the plan on the candidate issue: requirements the plan asked for that are missing or partial; behaviour in the diff that wasn't asked for (scope creep); requirements that look implemented but wrong.

### 4. Report

Present the two axes as separate sections — do not merge or rerank findings across them. Close the loop by updating the candidate issue: mark it done, or return it with findings.

## Fallback

- **`/code-review`**: if installed, use it as the reference for the two-axis review. Otherwise run the review by the inline rules below — this section carries the contract this step uses.

  **Standards-axis rules.** Review the diff against the repo's documented coding standards (see `docs/agents/domain.md`, any `CODING_STANDARDS.md`/`CONTRIBUTING.md`). On top of documented standards, carry the Fowler **smell baseline** below — the fixed set of smells that applies even when the repo documents nothing. Two rules bind it:
  - **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
  - **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation — and, like any standard here, skip anything tooling already enforces.

  Each smell reads *what it is* → *how to fix*; match it against the diff:

  - **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
  - **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
  - **Feature Envy** — a method that reaches into another object's data more than its own. → move the method onto the data it envies.
  - **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
  - **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
  - **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
  - **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
  - **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
  - **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
  - **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
  - **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real target direct.
  - **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

## Completion criterion

Both axes reported separately, the floor is green, and the candidate issue is updated (done, or returned with concrete findings).
