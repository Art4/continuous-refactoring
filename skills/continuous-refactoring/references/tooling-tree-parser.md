# Reference: the tooling-tree parser

The parser holds the tooling tree's graph logic. It is handed which nodes are fulfilled and which are
rejected, and answers what that state means: the nodes per Track, their order, what blocks each, and
whether the aggregation nodes are fulfilled. It reads the tree docs and the target repository, and writes nothing.

- **Script:** `../../refactor-scan/references/tooling_tree.py`, relative to this file.
- **Tree docs:** beside the script — `tooling-tree.md` (the generic root) and `php-tooling-tree.md`, each
  with its edge table and, per node, Name, Tool, Purpose and a pointer to the file holding the node's
  **Fulfilment check** and **MR scope**.

## Calling it

```
python3 <script> [--seed <seed file>] <target repo>
```

Without `--seed` every node is undecided: the call for the node lists and the tree's order. The seed is a
JSON file written to a temporary directory outside the target:

```json
{"fulfilled": ["<slug>", "..."], "rejected": {"<slug>": null, "<slug>": {"php": "7.4"}}}
```

A node in neither list is undecided. `{"php": "X.Y"}` is a rejection's blocker (`rejection.md`). The
parser settles four nodes itself and ignores what is handed in for them: `git`,
`onboarding-setup`, and the two **aggregation nodes** `structural-scan` and `php-safety-net`, whose state
it computes from their leaves. A seed it cannot use ends in exit code 2: correct the file and run again.

## What it returns

| Key | Holds |
| --- | --- |
| `tracks["Safety Net"]`, `tracks["Guardrails"]` | `nodes`: every node of the Track a ticket can be filed for, as `{node, name, tool, search}` in the tree's order · `backlog`: the slugs among them that are neither fulfilled nor rejected, blocked ones included, in the tree's order · `withheld`: `{node, reason}` for each node of the Track that cannot be worked now, those closed by a rejection included · `fulfilled`: the backlog is empty |
| `detected` | `{slug: {fulfilled}}` for the nodes handed in as fulfilled and the four the parser settles |
| `next` | `{node, reason}` for the backlog nodes nothing holds back |
| `php_floor_blocked` | `{node, reason}` for each node whose tool needs a newer PHP than the target declares, a rejected one included; the reason names the minimum |
| `closed_by_rejection` | nodes closed because a required parent is rejected |
| `reversals` | rejections whose `php` blocker the target now meets |
| `tree.edges` | every edge as `{from, to, type}`; the types are `required`, `required-any`, `recommended`, `resolved` |

Nodes the tree holds that are in no Track's `nodes` and are not one of the four above are
**recognition-only**: judged like any node, handed in like any node, and no ticket is ever filed for them
(`is-php-project`, `static-code-analyzer`, `psalm`, `has-real-dependency`, `phpstan-not-psalm`,
`phpstan-baseline-empty`).

## Is Safety Net fulfilled?

The answer is `detected["structural-scan"]["fulfilled"]`, the computed state of the aggregation node
every Safety Net leaf feeds. `tracks["Safety Net"]["fulfilled"]` answers another question — whether every Safety Net node is done — and decides nothing in a run.

Within one run a node is judged once, and the result is reused. Where this run's Safety Net scan judged the whole Track, read the answer from that call. Otherwise:

1. Write a seed that takes the best case: every recorded rejection as `rejected`, and every Safety Net and
   recognition-only node without an open ticket as `fulfilled`. The answer comes back unfulfilled → it
   stands.
2. It came back fulfilled → judge those nodes for real (`track-scan.md`, *Judging a node*), write the
   seed from the judgements, and read the answer again.

## Without `python3`

Work the same answers out by hand from the two edge tables, in table order, with these rules:

- `required` — the child waits until the parent is fulfilled; a rejected parent closes the child.
- `required-any` — the child waits until one parent of that group is fulfilled.
- `recommended` — the child waits until the parent is decided: fulfilled, rejected, or closed by a
  rejection.
- `resolved` — the child is an aggregation node, fulfilled once every such parent is fulfilled, rejected,
  or closed by a rejection.
- Guardrails holds the nodes that have an aggregation node among their required ancestors; Safety Net
  holds the other nodes a ticket can be filed for.
- A node is below the PHP floor when the target's `require.php` in `composer.json` allows a PHP older
  than the node's minimum: 5.3 for `php-cs-fixer`, `phpunit` and `test-runner-if-missing`, 7.0 for
  `phpstan-level-0`, 7.2 for `composer-audit`.
