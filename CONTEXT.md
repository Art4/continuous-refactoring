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
One run of the orchestrator. The orchestrator carries each lifecycle skill's output to the next skill's input (ADR-0010) rather than each skill re-deriving its own context: `refactor-scan` proposes every currently-unblocked tooling-tree node and separately detects (never acts on) remembered merge requests that have since merged or closed; `refactor-learn` is the pass's only writer, acting on scan's findings and, once fewer than two suite merge requests are open, closing out at most one completed **candidate** (propose → prioritise → design → implement → learn).
_Avoid_: session, sprint

**Merge request**:
The forge reviewable that delivers a completed candidate. Skills always use this term; conversation with the human uses the forge's native word (pull request on GitHub, merge request on GitLab).
_Avoid_: PR (in skills), delivery (as a second name for the same artifact)

**Tooling tree**:
The directed graph of adoption steps a target repo climbs — a generic root (`skills/refactor-scan/references/tooling-tree.md`: `git`, `loop-config`) that every language specialization's tree (PHP: `skills/refactor-scan/references/php-tooling-tree.md`) attaches beneath. A **node** adopts one tool, or one suite-level prerequisite at the root, up to a stated degree — a tool may own several nodes (each PHPStan level is its own node). Operational lessons discovered while adopting or fulfilling a node are worked directly into its Purpose/Fulfilment check/MR scope prose, not tracked as a separate entry. Each node also carries a human-facing **Name** (the tree doc's `**Name:**` field), used instead of the slug anywhere a human reads it — issue titles, merge requests, the loop's closing report; internal bookkeeping (the edges table, the **Refactoring Notes**' `out-of-scope/` filenames, ledger matching) stays keyed by the slug.
_Avoid_: baseline, floor, bootstrap, onboarding

**Refactoring Notes**:
The target repo's own folder holding the loop's state — `bookkeeping.md`, `merge-requests.md`, `out-of-scope/`. Default `docs/refactoring/`; overridable per target, decided once during `loop-config`'s own interview and recorded, by this name, in that target's `AGENTS.md`/`CLAUDE.md` (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`) — every other skill refers to it by this name, never by restating the concrete path.
_Avoid_: suite folder, config folder, state folder

**Required edge**:
The gating edge between nodes: a node is proposed only once every parent linked by a required edge is fulfilled; rejecting a required parent closes every node beneath it.
_Avoid_: hard edge, blocking edge

**Recommended edge**:
The counterpart that gates on a decision rather than on fulfilment (ADR-0016): a node is proposed only once every parent linked by a recommended edge is _decided_ — fulfilled, or rejected. A rejected recommended parent still releases the child instead of closing it, unlike a required parent; the rejected parent is never re-proposed. A recommended parent that hasn't been reached yet at all counts as undecided too, withholding the child just the same as one that's merely sitting proposed-but-unactioned.
_Avoid_: soft edge, nice-to-have edge, non-blocking edge

**Required-any edge**:
An OR variant of the required edge (ADR-0019): a node with required-any parents is proposed once _at least one_ of them is fulfilled, not all — distinct from a **choice** (below), which is about mutual exclusion between siblings, not about unlocking a downstream child from either side. Combines with a node's ordinary required parents (if any) via AND between the two edge types, OR within the required-any group itself.
_Avoid_: optional required edge, either-or edge

**Choice**:
Two or more sibling nodes under a shared required parent where adopting one makes the others out-of-scope by design — recorded the same way any other rejection is, via an `out-of-scope/<node>.md` entry (in the **Refactoring Notes**) for the unchosen sibling(s), not a separate mechanism. The tree has no dedicated XOR primitive; a choice is just an ordinary sibling pair plus the convention that picking one means rejecting the rest.
_Avoid_: XOR, either-or

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
The tooling-tree node names `refactor-scan` hands the orchestrator, every currently-unblocked one, however many that is — not yet candidates, since nothing is filed until `refactor-design` picks one and specs it.
_Avoid_: suggestions, recommendations (that's `refactor-prioritize`'s output, one level further)

**Findings**:
Remembered issues or merge requests `refactor-scan` detects have since merged, closed, or — a candidate MR left in draft by an earlier interrupted pass, its fold-in bookkeeping never landed — are still open but owe a write `refactor-learn` never got to finish. Handed to `refactor-learn` to act on. Scan only notices; it never decides the outcome itself.
_Avoid_: events, notifications