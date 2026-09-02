---
name: refactor-design
description: Turn the chosen node into a concrete refactoring plan, filing it as an issue — search the codebase first when the node is structural-scan.
---

# Refactor Design

Turn the **node** `refactor-prioritize` chose into a **plan** and file it as the issue that carries it.

## Process

### 1. Already fully specified?

Tooling-tree nodes are fully specified by definition — their Purpose, Fulfilment check, and MR scope are in the tree doc. Skip to step 5.

**`structural-scan`** is not pre-specified — continue to step 2.

### 2. Find a structural candidate

Walk commit history for hot spots, explore where you feel friction. Pick the single strongest one. See `references/design-process.md` for what to look for.

### 3. Ground in the candidate

Read the code, `CONTEXT.md`, and ADRs in the area. Understand *why* it's a candidate before proposing anything.

### 4. Grill toward the seam

Structural candidates only. Run `/grilling` on the deepened module, seam, interface, locality, and surviving tests. Add new terms to `CONTEXT.md`; offer ADR when user rejects with a load-bearing reason.

See `references/grilling-fallback.md` if `/grilling` isn't installed.

### 5. File the issue and write the plan

**Tooling-tree:** Title `Tooling tree: <Name>`, label `refactor:candidate`. Check existing issues first. Body: Purpose, Fulfilment check, MR scope as own plan.

**Structural:** Label `refactor:candidate`. Body: Where, Problem, Signal. Plan: deepened module, seam, interface, tests, slice order.

Set `config.md`'s `Pending candidates` to this issue. Skip for `loop-config` (file doesn't exist yet).

## Output

Filed issue with plan → `refactor-implement`.

## Completion criterion

Issue filed with plan, `Pending candidates` set (except `loop-config`).
