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

## Fallback

The suite must keep working in a target repo with none of the global skills installed. Per ADR-0003, each lifecycle skill self-contains its own step: its `## Fallback` section means "use the global skill if installed, else the inline fallback". Two fallback depths apply: **crash-safe** means skip the global skill with a note — the step's core is already inline; **self-sufficient** means the fallback inlines the part of the global skill the step uses. The orchestrator itself engages one global reference:

- **`/domain-modeling`** (learn step): if installed, use its discipline for the ADR and `CONTEXT.md` side effects. Otherwise skip with a note — the learn moves in step 7 (record the ADR, update `CONTEXT.md`, close the issue, stamp last-run) are inline and run regardless. Crash-safe.

Where each lifecycle skill's inline fallback engages, so a pass runs on the suite's own skills alone:

- **Scan** — `refactor-scan`: the candidate vocabulary is inline; a missing `codebase-design` is a crash-safe skip.
- **Design** — `refactor-design`: a missing `grilling` engages the inline grilling loop (self-sufficient); a missing `domain-modeling` is a crash-safe skip — the `CONTEXT.md`/ADR side effects run inline regardless.
- **Implement** — `refactor-implement`: a missing `tdd` engages the inline red → green rules and test-quality guidance (self-sufficient).
- **Review** — `refactor-review`: a missing `code-review` engages the inline two-axis rules and Fowler smell baseline (self-sufficient).

The authoritative inventory of every global reference and its fallback type lives in `docs/agents/skill-references.md` (ADR-0003) and is enforced by the Tier 1 validator (`scripts/validate_skills.py`).

## Completion criterion

One full pass completed and the loop state updated — last-run stamped, the candidate issue closed, learnings recorded.