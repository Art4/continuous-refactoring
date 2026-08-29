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
One run of the orchestrator. The orchestrator carries each lifecycle skill's output to the next skill's input (ADR-0010) rather than each skill re-deriving its own context: `refactor-scan` proposes up to five tooling-tree nodes and separately detects (never acts on) remembered merge requests that have since merged or closed; `refactor-learn` is the pass's only writer, acting on scan's findings and, once fewer than two suite merge requests are open, closing out at most one completed **candidate** (propose → prioritise → design → implement → learn).
_Avoid_: session, sprint

**Merge request**:
The forge reviewable that delivers a completed candidate. Skills always use this term; conversation with the human uses the forge's native word (pull request on GitHub, merge request on GitLab).
_Avoid_: PR (in skills), delivery (as a second name for the same artifact)

**Tooling tree**:
The directed graph of adoption steps a target repo climbs — a generic root (`skills/refactor-scan/references/tooling-tree.md`: `git`, `loop-config`) that every language specialization's tree (PHP: `skills/refactor-scan/references/php-tooling-tree.md`) attaches beneath. A **node** adopts one tool, or one suite-level prerequisite at the root, up to a stated degree — a tool may own several nodes (each PHPStan level is its own node). Alongside its Tool/Purpose/Fulfilment check/MR scope, a node may carry a **Learnings** entry: operational lessons discovered while adopting or fulfilling it, filled in as they're found rather than upfront.
_Avoid_: baseline, floor, bootstrap, onboarding

**Required edge**:
The gating edge between nodes: a node is proposed only once every parent linked by a required edge is fulfilled; rejecting a required parent closes every node beneath it.
_Avoid_: hard edge, blocking edge

**Recommended edge**:
The advisory counterpart: the child stays proposable even when its recommended parent was rejected; the rejected parent is never re-proposed — at most the loop informs where it would have helped.
_Avoid_: soft edge, nice-to-have edge

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

**Leverage**:
How much future change does deepening this module unlock? A module many others call is high-leverage; a leaf nobody calls is not.
_Avoid_: (none — use the term as-is)

**Locality**:
What moves together, and what must not spread? The degree to which related code lives in one place rather than scattered across the codebase.
_Avoid_: (none — use the term as-is)

**Plan**:
The concrete refactoring plan produced by `refactor-design`: the deepened module, its seam, the interface, and the surviving tests — written on the candidate issue so the refactor is delegable.
_Avoid_: design doc

**Proposals**:
The tooling-tree node names `refactor-scan` hands the orchestrator, up to five per pass — not yet candidates, since nothing is filed until `refactor-design` picks one and specs it.
_Avoid_: suggestions, recommendations (that's `refactor-prioritize`'s output, one level further)

**Findings**:
Remembered issues or merge requests `refactor-scan` detects have since merged or closed on the external tracker — handed to `refactor-learn` to act on. Scan only notices; it never decides the outcome itself.
_Avoid_: events, notifications