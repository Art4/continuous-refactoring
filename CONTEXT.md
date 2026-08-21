# Continuous Refactoring

The vocabulary of a portable agent-skill suite that keeps a software project under continuous refactoring — a stateful, repeatable loop that finds, plans, executes, verifies, and records structural improvements.

## Language

**Candidate**:
A backlog item filed on the project's issue tracker — either a structural deepening or a missing node on the **tooling tree**.
_Avoid_: task, ticket, todo

**Backlog**:
The set of candidate issues on the tracker, awaiting prioritisation.
_Avoid_: debt list, todo list

**Loop pass**:
One run of the orchestrator. It starts from remembered **merge request** state (respond to comments, record a merge, or learn a rejection). If fewer than two suite merge requests are open, it may then complete at most one **candidate** (discover → prioritise → design → implement → review → learn).
_Avoid_: session, sprint

**Merge request**:
The forge reviewable that delivers a completed candidate. Skills always use this term; conversation with the human uses the forge's native word (pull request on GitHub, merge request on GitLab).
_Avoid_: PR (in skills), delivery (as a second name for the same artifact)

**Tooling tree**:
The directed graph of tools in a language specialization. A child node is reachable only after its parent is fulfilled or rejected; a rejection closes that subtree.
_Avoid_: baseline, floor, bootstrap, onboarding

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
A candidate that an already-fulfilled tooling-tree node keeps surfacing — things that will re-fail until fixed.
_Avoid_: lint noise, tool complaints