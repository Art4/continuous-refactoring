---
name: continuous-refactoring
description: Run one pass of the continuous refactoring loop — scan, prioritise, design, implement, review, learn. Use to keep a codebase under continuous refactoring, on a cadence or on demand.
disable-model-invocation: true
---

# Continuous Refactoring

The **loop pass** — the stateful, repeatable sequence that keeps a project under continuous refactoring. Each pass does only the work due since the last pass, then records what it learned so the next pass starts from state, not from zero.

Run this on demand whenever you're asked, or on the configured **cadence**.

## Loop state

State lives in the target repo, not in the conversation:

- **Config** — `docs/agents/refactoring.md`: cadence, last-run date, baseline marker, focus areas
- **Backlog** — `refactor:*` issues on the issue tracker (see `docs/agents/issue-tracker.md`)
- **Learned rejections** — `.out-of-scope/` entries from prior passes

Read all three at the start of every pass. If `docs/agents/refactoring.md` doesn't exist, scaffold it (ask the user for the cadence; default weekly) — this is the marker that a pass can run.

## The pass

Each step is one of the lifecycle skills. Stop between steps where the skill itself stops for user input.

1. **Baseline check.** If the **baseline** isn't marked done in `docs/agents/refactoring.md`, run `/refactor-baseline` first. No refactoring pass before the tooling floor exists.

2. **Scan.** Run `/refactor-scan`. If the last scan is recent and nothing changed, report that and stop early.

3. **Prioritise.** Run `/refactor-prioritize`. The user picks the next candidate.

4. **Design.** Run `/refactor-design` on the chosen candidate. If the candidate is tiny and the user wants to skip to implementation, that's their call — flag it, don't block.

5. **Implement.** Run `/refactor-implement`.

6. **Review.** Run `/refactor-review`. If findings come back, loop implement → review until clean.

7. **Learn.** Close the loop:
   - Mark the candidate issue done (or `wontfix` → `.out-of-scope/`)
   - Record ADRs for decisions a future scan must not re-litigate (see `/domain-modeling`)
   - Update `CONTEXT.md` with any terms that crystallised
   - Stamp the last-run date in `docs/agents/refactoring.md`

## Completion criterion

One full pass completed and the loop state updated — last-run stamped, the candidate issue closed, learnings recorded.