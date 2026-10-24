# Reference: the tooling-tree parser

The parser holds the tooling tree's graph logic. It is handed what an agent judged — which Packs apply,
which Stages are fulfilled, which subjects are rejected, the runtime the target allows — and answers what
that means: the Stages per Track, their order, what holds each back, and whether the Safety Net is
fulfilled. It reads the Packs and the target's tracker file, and writes nothing. The rules it follows are
in `tooling-model.md`.

- **Script:** `tooling_tree.py`, beside this file.
- **Data:** `roles.json` and `packs/<pack>/pack.json`, beside it too, and the target's own Pack where it has
  one. Each Tool's `details` file, named relative to its Pack's directory, holds the **Fulfilment check** and
  **MR scope** of its Stages.

## Calling it

```
python3 <script> [--seed <seed file>] [--own-pack <dir>] [--packs <dir>] <target repo>
```

Where the target's `## Refactoring operations` section has a **Tooling Pack** bullet (`refactoring-operations.md`),
`--own-pack` is handed the directory it names, relative to the target. The parser then reads that Pack after
the suite's own, with its Roles. A Pack that redefines a slug of the suite's, or a Role, ends in exit code 2
and names both places.

`--packs` replaces the directory of the suite's Packs; it is for tests. Without `--seed` nothing is decided and every Pack applies, the target's own included: the call for the Stages and the tree's
order. The seed is a JSON file written to a temporary directory outside the target:

```json
{"fulfilled": ["<stage>", "..."],
 "rejected": {"<role, tool or stage>": null, "<role, tool or stage>": {"php": "7.4"}},
 "packs": ["generic", "php"],
 "not_applicable": ["<stage>"],
 "runtime": {"php": "7.4"}}
```

| Key | Holds |
| --- | --- |
| `fulfilled` | the Stages judged fulfilled |
| `rejected` | each rejected Role, Tool or Stage, with its blocker: `null`, or the minimum runtime whose arrival lifts the rejection (`rejection.md`) |
| `packs` | the Packs whose *Applies when* holds; missing means all of them |
| `not_applicable` | the Stages whose own *Applies when* does not hold |
| `runtime` | the lowest version of each runtime the target allows, read from its manifest and written as a string: for PHP the lowest version `require.php` allows, or `config.platform.php` where that is set. Left out where it is unclear: a missing or unreadable version blocks nothing |

A Stage in none of the lists is undecided. `git` and `onboarding-setup` are settled by the parser itself and
ignored where handed in. A seed or a Pack it cannot use ends in exit code 2: correct the file and run
again.

## What it returns

| Key | Holds |
| --- | --- |
| `tracks["Safety Net"]`, `tracks["Guardrails"]` | `nodes`: every Stage of the Track a ticket can be filed for, as `{node, name, tool, search}` in the order of the Packs · `backlog`: the slugs among them that are neither fulfilled nor closed by a rejection, blocked ones included · `workable`: the backlog without what waits · `withheld`: `{node, reason}` for each Stage of the Track that cannot be worked now, those closed by a rejection included, with what they hang on · `fulfilled`: the backlog is empty |
| `safety_net_fulfilled` | the Safety Net's backlog is empty: every Stage is fulfilled or closed by a rejection |
| `runtime_blocked` | `{node, reason}` for each Tool whose runtime is below its minimum, at the Tool's first Stage, a rejected one included; the reason names both versions |
| `closed_by_rejection` | the Stages closed because a Role, a Tool or a required Stage is rejected, or because a rejection left a required Role or an any-of group nothing that could be fulfilled |
| `reversals` | rejections whose runtime blocker the target now meets |
| `roles`, `tools` | each Role, in each scope its Tools are in, as `{role, name, scope, filled_by}` with the Tool that fills it; each Tool with its Roles, its status (recommended or recognized), and whether another Tool took its place |
| `prerequisites`, `packs` | whether `git` and `onboarding-setup` hold; the Packs that applied |
| `tree.stages` | every Stage with its Tool, Roles, Pack, Track, `requires` and `waits_for` |

A Stage of a recognized Tool, or of a Tool another Tool took the place of, is in no `nodes` list and gets
no ticket.

## Is Safety Net fulfilled?

The answer is `safety_net_fulfilled`. Within one run a Stage is judged once, and the result is reused.
Where this run's Safety Net scan judged the whole Track, read the answer from that call. Otherwise the
Track has a trace (`worklist.md`, *A Track's trace*): read the answer from a call with the seed from the
trace.

## The seed from the trace

For a tooling Track that has a trace, its tickets are the state. The seed holds:

- every recorded rejection as `rejected`, with its blocker (`rejection.md`, *Finding rejections*), of a
  Role, Tool or Stage the Packs still have; a rejection of one the suite has since dropped is left out;
- every Stage of the Track that is *known* — a ticket of it exists in some state, or a rejection of it is
  on record — and has no open ticket as `fulfilled`, taken as done and not judged. A Stage that is not
  known stays undecided, and its Track's scan is due (`worklist.md`);
- the Packs and Stages the *Applies when* sentences hold for, and the runtime, judged this run
  (`track-scan.md`, *Judging*). No ticket stands for them, so the tracker says nothing about them.

Every step that calls the parser outside a scan uses this seed: the gate question above, and the calls
that follow a rejection (`rejection.md`).

## Without `python3`

Work the same answers out by hand with the steps of `tooling-model.md`, *Working it out by hand*.
