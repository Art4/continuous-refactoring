---
name: continuous-refactoring
description: Run one pass of the continuous refactoring loop — propose, prioritise, design, implement, learn. Use to keep a codebase under continuous refactoring, on demand or via your own recurring trigger.
disable-model-invocation: true
---

# Continuous Refactoring

The **loop pass** — calls each lifecycle skill in order and carries output forward. This skill is a thin data pipe: it does not decide anything a lifecycle skill could decide.

Git is the only hard requirement. No stored schedule — run on demand whenever asked.

## The pass

Prefer dispatching each step to a fresh subagent. Bring back only its stated `## Output`.

1. **Scan.** Run `/refactor-scan`. Checks preconditions, resumes pending work, proposes nodes. Two early stops: no git (stop entirely), or backlog full (skip to step 5). A resume-candidate (open MR with reviewer activity) skips to step 5 too.

2. **Learn, early call.** Only if step 1 produced findings. Run `/refactor-learn` on them now — it resolves each and updates the ledger before prioritising reads it. Skip entirely when no findings.

3. **Prioritise.** Run `/refactor-prioritize` on scan's proposals. Stops if two suite MRs are open. Otherwise recommends one node.

4. **Design.** Run `/refactor-design` on the chosen node. Files it as an issue with the plan.

5. **Implement.** Run `/refactor-implement`. One candidate, one branch. Reviews its own diff before opening the MR.

6. **Learn, closing call.** Run `/refactor-learn` with the freshly opened MR (if any). Always runs — even a bookkeeping-only pass is complete.

## Stacking rule

While fewer than two suite MRs are open, stack new ones (base = current suite branch). Never two against default at once.

## Closing report

Two lines wherever the pass ends:
- **Status:** what happened this pass.
- **Next:** what the human can or should do now.

See `references/orchestration.md` for state locations, MR description format, and examples.

## Completion criterion

`refactor-learn` ran at least once, `Fulfilled nodes` written, outcome recorded.
