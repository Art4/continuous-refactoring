---
name: refactor-implement
description: Execute a designed refactor plan test-first, slice by slice, at the agreed seam — review the result, then open the merge request.
---

# Refactor Implement

Execute a **plan** as vertical slices, red → green, at the agreed **seam** — then review and open the merge request.

Every slice: behavior-preserving only, deterministic tools do the moves they can, work lives on the refactor's own branch.

## Process

### 1. Branch, confirm seams

Create the branch the plan names. For structural candidates: list and confirm seams with the user. **No test at an unconfirmed seam.**

Tooling-tree nodes: skip seam confirmation — make the one config/dependency change directly.

`loop-config` exception: create `docs/refactoring/config.md` with `Pending candidates` set to this issue. Leave `Create-mode` and `Fulfilled nodes` unset — `refactor-learn` fills them.

### 2. One slice at a time

Write failing test first (red), then only enough code to pass (green). One seam, one test, one minimal implementation per cycle. Don't anticipate future slices.

Tooling-tree: already done in step 1.

### 3. Verify

Structural: run full test suite + fulfilled tooling on touched files. Green.
Tooling-tree: run the Fulfilment check from the tree doc.

### 4. Review the diff

Two axes, reported separately (see `references/review-axes.md`):
- **Standards** — does it follow repo standards + Fowler smell baseline?
- **Spec** — does it implement the plan on the issue?

Findings send back to step 2. One line per finding: file, issue, fix.

### 5. Open the merge request

Push and open MR per config's create-mode. Include `Closes #<issue>` only when this MR satisfies the full fulfilment check. Wait for CI if the target runs it — confirm via forge, not local dry-run.

## Output

Opened merge request → `refactor-learn`.

## Completion criterion

Branch has the work, review clean on both axes, MR open, CI green (where applicable).
