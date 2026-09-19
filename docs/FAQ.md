# FAQ

## Why does the suite install so much tooling instead of just starting the refactor?

Because an LLM can't be trusted to make sweeping code changes safely on its own. The tooling tree
introduces deterministic checks and safeguards — static analysis, coding standards, a working test
runner — *before* an agent is allowed to touch the code, so a wrong or overconfident change gets
caught mechanically rather than relying on the agent to notice its own mistake.

Nearly all of it can be skipped, but at the cost of code quality and backward compatibility: fewer
gates means fewer things stopping a bad change before it merges. The tooling also gives you a
lever — reviews of the suite's own merge requests can steer, speed up, or focus what the loop
decides to work on next, the same way any other proposal-and-review cycle would.

## Why is Housekeeping a separate Track instead of a recurring tooling-tree node?

Because the tooling tree is a purely fact-based, filesystem-driven model — its deterministic parser
has no forge access and so has no way to derive a cadence from tracker history. A time-driven
"unfulfilled again after N days" flag would also violate `structural-scan`'s own assumption that a
once-resolved leaf stays resolved.

It doesn't fit the ordinary candidate pipeline shape either: `scan → prioritise → design → implement →
learn` ranks and delivers one candidate at a time, but a housekeeping sweep works down a standing
checklist instead — there's nothing to rank. That's why it's its own Track, run directly by the
`continuous-refactoring` orchestrator when the shared Track scheduler selects it (default cadence:
weekly), rather than a step inside the ordinary candidate pipeline or a node inside the tree — the same
shared scheduler that runs Safety Net, Guardrails, and Investigation, but with its own self-contained
due-check/reconcile/checklist/deliver process once selected, architecturally independent of the
propose-then-hand-off shape the other three Tracks use.
