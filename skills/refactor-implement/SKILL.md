---
name: refactor-implement
description: Execute a designed refactor plan test-first, slice by slice, at the agreed seam. Part of the continuous refactoring loop.
---

# Refactor Implement

Execute a **plan** (from `refactor-design`) as a series of vertical slices, red → green, at the agreed **seam**. The tests written here are the ones the refactor is judged by later.

Use `/tdd` if installed as the reference for what a good test is and the rules of the red → green loop; otherwise the loop rules and test-quality guidance in `## Fallback` below govern.

Every slice honors the foundational refactoring rules (ADR-0004): behavior-preserving only, deterministic tools do the moves they can (code style through the formatter with the repo's ruleset, Rector-reported issues fixed by Rector — never hand-applied by the agent), and the work lives on the refactor's own branch unless the human or the plan says otherwise.

## Process

### 1. Confirm the seams

Before writing any test, list the seams the plan names and confirm them with the user. **No test is written at an unconfirmed seam.** Testing at the wrong seam is how refactors produce tests that break under refactoring.

### 2. One slice at a time

Each slice: write the failing test first (red), then only enough code to pass it (green). One seam, one test, one minimal implementation per cycle. Don't anticipate future slices or add speculative features.

### 3. Verify the loop on completion

When the plan's slices are done:

- Run the full test suite — the surviving tests from the plan plus the new seam tests must be green.
- Run the fulfilled tooling (PHPStan, Rector, style) over the touched files — the refactor must not regress mechanical quality.

## Fallback

- **`/tdd`**: if installed, use its discipline as the reference for what a good test is and the rules of the loop. Otherwise run the loop by its inline rules. **Rules of the loop:** *red before green* — write the failing test first, then only enough code to pass it, without anticipating future slices or adding speculative features; *one slice at a time* — one seam, one test, one minimal implementation per cycle; *refactoring is not part of the loop* — it belongs to the review stage, so no refactoring inside the red → green cycle. **What makes a test worth keeping:** it verifies **behaviour through public interfaces**, not implementation details — the code can change entirely and the test still passes, so it survives the refactor. It must never be **tautological** (the assertion recomputes the expected value the way the code does, so it passes by construction and can never disagree with the code) nor **implementation-coupled** (mocks internal collaborators, tests private methods, or verifies through a side channel).

## Completion criterion

Every slice in the plan is implemented red → green, the full suite is green, and the fulfilled tooling is clean on the touched files.