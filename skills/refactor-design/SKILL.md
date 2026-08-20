---
name: refactor-design
description: Grill a chosen candidate into a concrete refactoring plan — the deepened module, the seam, the interface, and the tests that survive. Part of the continuous refactoring loop.
---

# Refactor Design

Turn one chosen **candidate** into a **plan** concrete enough to implement: the deepened module, its **seam**, the interface, and which tests survive. The `/grilling` loop sharpens the design; `/domain-modeling` keeps the domain model current as decisions land.

## Process

### 1. Ground in the candidate

Read the candidate issue and the code it names. Read `CONTEXT.md` and the ADRs in the area. Understand *why* it's a candidate (the friction) before proposing anything.

### 2. Grill toward the seam

Run a `/grilling` session on the candidate. The decision tree hangs off these branches:

- **The deepened module** — what does the module become, and what is its one job? What disappears behind it?
- **The seam** — where is the public boundary, and what is it tested through?
- **The interface** — what does the interface expose, and does it stay deep (implementation complexity > interface complexity)?
- **Locality** — what moves together, and what must *not* spread?
- **Tests that survive** — which existing tests stay, which are rewritten, which new ones appear at the seam?

Side effects happen inline as decisions crystallise (per `/domain-modeling`):

- Naming a module after a concept not in `CONTEXT.md`? Add the term.
- User rejects a design with a load-bearing reason a future scan should not re-suggest? Offer an ADR.

### 3. Write the plan

Capture the plan on the candidate issue: the deepened module, the seam and interface, the surviving tests, and the ordering of slices (see `refactor-implement`). This is the handoff that makes the refactor delegable.

## Completion criterion

The candidate has a written plan on its issue — module, seam, interface, surviving tests, slice order — and the design survives the grilling session (no open frontier).