# Reference: scanning a tooling Track

The scan of Safety Net or Guardrails: judge the Track's nodes against the target, let the parser order
them, and turn every node that is neither fulfilled nor rejected into a **proposal** for a ticket. It runs
when the Track has no open ticket or the call asked for it. The scan reads; its proposals reach the
tracker through the filing step.

## 1. Scope

From the parser's seedless call (`tooling-tree-parser.md`): the Track's `nodes`, and every
recognition-only node. A restriction in the call narrows what step 4 proposes; of the nodes outside it,
only those a covered node hangs on are judged.

## 2. Node state

- **Rejected** — the recorded rejections (`rejection.md`, *Finding rejections*), with their blockers.
- **Every other node in scope** — judged, below.
- **The other tooling Track's nodes.** In a Safety Net scan they stay undecided. In a Guardrails scan the
  Safety Net nodes decide what blocks a Guardrails node: one with an open ticket stays undecided, every other is
  judged unless this run already judged it.

Judging may run in a subagent handed this section and the tree docs; it returns the two lists of the seed
and, per node judged fulfilled under another name than its Tool, the evidence in one line.

### Judging a node

Read the node's Purpose and Fulfilment check in its tree-doc file, then the target. **Judge by Purpose:**
a node is fulfilled when a real, working tool serves its Purpose in the target, under any name.

- **The evidence the Fulfilment check names is there** — the dependency, the config file, the CI
  invocation → fulfilled.
- **It is absent, and another tool serves the Purpose** → fulfilled. A target running Laravel Pint has no
  `friendsofphp/php-cs-fixer` dependency, and Pint serves "automated code style": `php-cs-fixer` is
  fulfilled. A CI job running `composer run security-check`, a script that calls `composer audit`,
  fulfils `composer-audit`.
- **Two tools compete for the Purpose, or it is unclear whether one serves it** → undecided, and the
  proposal carries the question, so the human answers it at filing.
- **Nothing serves it** → undecided. A human who says the Purpose is met without a tool declines the node
  at filing; that is a rejection, never a fulfilment.

Step 2 is done when every node in scope is in one of the seed's two lists or deliberately in neither.

## 3. Order

Write the seed and run the parser with it. Take the Track's `backlog` and `withheld`, plus
`php_floor_blocked`, `closed_by_rejection` and `tree.edges`.

## 4. Proposals

Go through the backlog in its order. Each node becomes one proposal — its Name, its Purpose in one line,
and what blocks it — unless one of these applies first:

| The node | Instead |
| --- | --- |
| already has an open ticket (a scan the call asked for) | no proposal; the ticket stands |
| is in `php_floor_blocked` and not rejected | the proposal is to record a rejection with that PHP version as its blocker (`rejection.md`, *Below the PHP floor*) |
| waits, directly or through other nodes, behind a node that gets no ticket: an unfulfilled recognition-only node, or a node below the PHP floor | out of reach: no ticket could unblock it. Named in one line with the reason, no proposal — except behind `phpstan-baseline-empty`, below |

**What blocks a proposal** is read from `tree.edges`: every parent by a `required` or `recommended` edge
that is undecided, and, where a parent is an aggregation node, that node's undecided `resolved` parents in
its place. Where a `required-any` group has no fulfilled member, its members block together, and the
ticket says that one of them is enough.

**A PHPStan baseline with entries.** `phpstan-baseline-empty` unfulfilled means the highest fulfilled
level's baseline still holds findings, and the next level waits for them. Propose one ticket, "PHPStan
Level N: shrink the baseline", N being that fulfilled level; it belongs to that level's Track, and the next
level's proposal is blocked by it. What a baseline ticket's check asks is whether the baseline still has
entries; the level's own Fulfilment check says nothing about it.

**A scan the call asked for** also re-judged nodes that have an open ticket: one found fulfilled is laid
out at filing for closing with a note, as selection does at pick-up (`selection.md`).

## 5. Hand on

- **Proposals** → the filing step, in backlog order.
- **None** → say what the scan found — every node fulfilled or rejected, or which are out of reach and
  why — and return to Track choice with the Track marked as tried.

The scan is done when every node in scope is fulfilled, rejected, proposed, or named as out of reach.
