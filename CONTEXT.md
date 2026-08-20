# Continuous Refactoring

The vocabulary of a portable agent-skill suite that keeps a software project under continuous refactoring — a stateful, repeatable loop that finds, plans, executes, verifies, and records structural improvements.

## Language

**Candidate**:
A refactoring opportunity filed as an issue on the project's issue tracker.
_Avoid_: task, ticket, todo

**Backlog**:
The set of candidate issues on the tracker, awaiting prioritisation.
_Avoid_: debt list, todo list

**Loop pass**:
One run of the orchestrator: discover → prioritise → design → implement → review → learn.
_Avoid_: session, sprint

**Baseline**:
The one-time tooling foundation established before the loop starts — code style, Rector, PHPStan, and CI enforcement.
_Avoid_: setup, bootstrap

**Cadence**:
The configured schedule that decides when the next periodic loop pass is due.
_Avoid_: frequency, interval

**Hot spot**:
A part of the codebase that keeps appearing in change history — the primary place to look for candidates.
_Avoid_: problem area, pain point

**Deepening**:
The refactoring move that turns a shallow module into a deep one.
_Avoid_: cleanup, tidy-up

**Deletion test**:
The test for shallowness: would deleting this module concentrate complexity, or just move it?
_Avoid_: (none — use the term as-is)

**Seam**:
The public boundary at which a module is tested — where tests observe behaviour without reaching inside.
_Avoid_: boundary, internal hook

**Tooling pressure**:
A candidate that tools (PHPStan, Rector, CI) keep surfacing — things that will re-fail until fixed.
_Avoid_: lint noise, tool complaints