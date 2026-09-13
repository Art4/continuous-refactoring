# The pre-implementation decision gate

Applies inside any design flow that can turn up a decision worth pausing over before step 5
(`refactor-design/SKILL.md`) — grounding/grilling a structural or externally-labeled candidate
(`structural-candidate.md` step 4), or planning a PHPStan baseline-shrink fix
(`phpstan-baseline-shrink.md` step 3). Check for either of the two cases below before writing
anything else.

## A decision meeting the `/domain-modeling` ADR bar

Hard to reverse, surprising without context, a real trade-off between genuine alternatives — the
same three-factor test that decides whether to offer an ADR — while the candidate itself still stays
behavior-preserving. The loop runs unattended; don't stop and wait for a live answer. Instead:

- Write the plan exactly as usual, choosing a default the same way any other design decision gets
  made.
- Also write, in the same (or an additional) issue comment, the specific question this decision
  raises and the default chosen — plain enough that a human can confirm it as written, or override
  it, by commenting and then adding `ready-for-agent` (`docs/agents/triage-labels.md`) once satisfied.
  This lands on the target repo's own issue —
  `skills/continuous-refactoring/references/forge-facing-writing.md`.
- Deliberately don't add `ready-for-agent` yourself. This is what makes the candidate a **flagged
  candidate**: designed, but not yet cleared to implement.

Nothing else about the issue changes — it stays open, `refactor:candidate` unchanged; only whether
`refactor-implement` may run against it this pass. The orchestrator
(`skills/continuous-refactoring/SKILL.md` step 5) skips implementation for a flagged candidate still
missing `ready-for-agent`. How a later pass treats it meanwhile depends on the tracker
(`refactor-scan/SKILL.md` steps 2 and 3b): a native-label tracker can always rediscover it later, so
scan looks for other work instead of waiting on it; a git-only tracker has no such rediscovery, so the
pass stops there rather than risk losing track of it.

## A genuine breaking change

The fix can't be made without changing observable behavior — the foundational rule
(`skills/continuous-refactoring/references/foundational-refactoring-rules.md`) that a refactor never
ships one. This isn't `refactor-design`'s call to act on: don't write a plan, don't comment on the
issue, don't touch any label — only `refactor-learn` writes bookkeeping/labels/`out-of-scope`
(`refactor-learn/SKILL.md`'s own stated boundary). Hand it forward instead as a **finding** — a short
statement of what was found and why it needs a behavior change — to this same pass's closing
`refactor-learn` call (`skills/continuous-refactoring/SKILL.md` step 6), which applies its existing
rejection machinery (`wontfix`, a closing note or `out-of-scope/` entry) the same way it already
would for a load-bearing MR-review rejection.
