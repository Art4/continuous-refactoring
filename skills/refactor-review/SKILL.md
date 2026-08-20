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

Review the diff against this repo's documented coding standards (see `docs/agents/domain.md`, any `CODING_STANDARDS.md`/`CONTRIBUTING.md`). On top of documented standards, carry the Fowler **smell baseline** from `/code-review` — the fixed set of smells that applies even when the repo documents nothing, each a judgement call, with a documented repo standard always overriding.

### 3. Spec axis

Review the diff against the plan on the candidate issue: requirements the plan asked for that are missing or partial; behaviour in the diff that wasn't asked for (scope creep); requirements that look implemented but wrong.

### 4. Report

Present the two axes as separate sections — do not merge or rerank findings across them. Close the loop by updating the candidate issue: mark it done, or return it with findings.

## Completion criterion

Both axes reported separately, the floor is green, and the candidate issue is updated (done, or returned with concrete findings).