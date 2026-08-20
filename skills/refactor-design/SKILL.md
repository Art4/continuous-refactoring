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

## Fallback

- **`/grilling`**: if installed, use its session. Otherwise run the grilling loop inline: map the design as a **design tree** — every decision branches into the decisions that hang off it — and work it in **rounds**. The **frontier** is every decision whose prerequisites are already settled. Ask the whole frontier in one round, numbering each question (`❓ **Q1** - **<title>**: <body>`, multiple choices allowed) with your recommended answer (`➡️ <recommendation>`), then wait for the user. Their answers reshape the tree and push the frontier outward — a question depending on one still open in this round belongs to a later round. Facts are your job (dispatch a sub-agent rather than asking the user), decisions are the user's. Done when the frontier is empty: every branch visited, nothing silently assumed. In this step the tree hangs off the five branches in section 2 — the deepened module, the seam, the interface, locality, and the tests that survive.
- **`/domain-modeling`**: if installed, use its discipline. Otherwise skip it with a note — the side effects this step performs are already inline in section 2 above and run regardless: add resolved terms to `CONTEXT.md` (a glossary and nothing else — no implementation details) as they crystallise, and offer an ADR under `docs/adr/` when the user rejects a design with a load-bearing reason a future scan should not re-suggest. The discipline's enrichment moves (challenging fuzzy terms, probing edge-case scenarios, cross-referencing the code) are not part of this step.

## Completion criterion

The candidate has a written plan on its issue — module, seam, interface, surviving tests, slice order — and the design survives the grilling session (no open frontier).