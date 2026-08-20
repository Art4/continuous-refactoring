---
name: refactor-implement
description: Execute a designed refactor plan test-first, slice by slice, at the agreed seam. Part of the continuous refactoring loop.
---

# Refactor Implement

Execute a **plan** (from `refactor-design`) as a series of vertical slices, red → green, at the agreed **seam**. The tests written here are the ones the refactor is judged by later.

Use `/tdd` as the reference for what a good test is and the rules of the red → green loop.

## Process

### 1. Confirm the seams

Before writing any test, list the seams the plan names and confirm them with the user. **No test is written at an unconfirmed seam.** Testing at the wrong seam is how refactors produce tests that break under refactoring.

### 2. One slice at a time

Each slice: write the failing test first (red), then only enough code to pass it (green). One seam, one test, one minimal implementation per cycle. Don't anticipate future slices or add speculative features.

### 3. Verify the loop on completion

When the plan's slices are done:

- Run the full test suite — the surviving tests from the plan plus the new seam tests must be green.
- Run the baseline tooling (PHPStan, Rector, style) over the touched files — the refactor must not regress the **baseline**.

## Completion criterion

Every slice in the plan is implemented red → green, the full suite is green, and the baseline tools are clean on the touched files.