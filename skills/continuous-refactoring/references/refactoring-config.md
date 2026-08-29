# Reference: `docs/refactoring/config.md` in the target repo

The config file the suite reads and writes. It doesn't exist on a fresh target repo: `refactor-scan` proposes it (the `loop-config` node, `skills/refactor-scan/references/tooling-tree.md`), `refactor-design` files it as a single `refactor:candidate` issue, and `refactor-implement` creates the file when that candidate is implemented — the same path any other tooling-tree node takes.

## Structure

```markdown
# Refactoring Loop Config

**Create-mode:** autonomous
**Focus areas:** order intake, billing
**Pending tasks:**
- none
**Fulfilled nodes:**
- loop-config
- composer
- ci-runner
```

## Fields

| Field | Meaning | Written by |
|---|---|---|
| `Create-mode` | How merge requests get opened: `autonomous`, `ask-each-time`, or `human-opens` | `refactor-learn` (first time it writes bookkeeping) |
| `Focus areas` | Areas scans should target first | you, any time |
| `Pending tasks` | A one-item list (a bullet under the header, `- none` when empty) holding the issue `refactor-design` just filed, not yet delivered as a merge request. Written as a list purely for formatting consistency with `Fulfilled nodes` and easier diffing — it still holds at most one entry; the suite tracks exactly one thing in flight at a time (`refactor-scan`/`refactor-prioritize`), this is not a multi-pending queue. | `refactor-design` sets it when it files; `refactor-learn` clears it once the merge request is remembered (`merge-requests.md`) or the candidate is resolved another way |
| `Fulfilled nodes` | Tooling-tree node **slugs** (never Names — internal bookkeeping stays keyed by the slug) already confirmed fulfilled, one per bulleted line | `refactor-learn`, every closing call — see *Fulfilled nodes* below |

`Pending tasks` exists so a pass interrupted between design and implement doesn't get re-proposed as fresh work by the next `refactor-scan` — scan reads this field before walking the tree, and if it names an issue, that pending issue is the only thing it proposes this pass.

## `Fulfilled nodes`

A cache, not a second source of truth — it exists purely to let a pass skip re-deriving what earlier
passes already established, and only matters to the **manual/LLM tree-walk fallback**
(`skills/refactor-scan/references/tree-walk-prompt.md`), which otherwise re-evaluates every node's
Fulfilment check by hand, in tree order, on every single pass. The deterministic parser
(`skills/refactor-scan/references/tooling_tree.py`) never reads this field — plain filesystem detection
is already cheap and always correct there, so there's nothing to gain and a staleness risk to avoid.

- **Read:** only by the tree-walk-fallback prompt — a listed slug is skipped without re-checking its
  Fulfilment check.
- **Write:** `refactor-learn`, every closing call, per its own `## Process`. When this pass ran the
  deterministic parser (`python3` was available), it **overwrites the entire field** with the parser's
  complete current fulfilled-set — cheap ground truth, and this is what makes the cache self-healing:
  any staleness from an out-of-band change (a human revert, a manual edit) gets wiped out the next time
  a pass has parser access, whenever that is. When this pass ran the fallback instead, `refactor-learn`
  only adds newly-confirmed slugs from this pass's own walk — it does not attempt to verify or prune
  entries it didn't itself just check.
- **No per-entry metadata** (no timestamp, no "as of which pass") — that kind of field in a versioned,
  repeatedly-rewritten file invites merge conflicts between bookkeeping writes for no operational
  benefit.
- A node **never appears in `Fulfilled nodes` and `docs/refactoring/out-of-scope/` at the same time** —
  fulfilled and rejected are different, mutually exclusive states for a node; rejection state lives
  entirely in `out-of-scope/` (one file per rejected node), never duplicated here. A node moves from
  rejected to fulfilled only through the normal reversal path (an out-of-scope entry removed, then the
  node adopted for real) — see `skills/refactor-scan/references/php-tooling-tree.md`'s Nodes intro and
  `skills/refactor-learn/SKILL.md`.

**`loop-config` exception:** for the `loop-config` candidate itself, this file doesn't exist yet when `refactor-design` would normally write `Pending tasks` — `refactor-implement` sets it directly when it creates the file instead, leaving `Create-mode` and the first `Fulfilled nodes` entry (`loop-config` itself, at minimum) for `refactor-learn`'s own follow-up commit. Because the file only exists on that candidate's own (not yet merged) branch, `refactor-learn`'s writes land there too, the one time bookkeeping doesn't go straight to the default branch. Every pass after that, once the file is on the default branch, all of this is as described in the table above.

There is deliberately no `Cadence` field: the loop never triggers itself — you kick it off whenever it's due, whether that's you running `/continuous-refactoring` by hand or a scheduler you set up outside the suite. Nothing here would read a stored cadence, so nothing stores one.

## Rules

- **`Pending tasks` and `Fulfilled nodes` are `refactor-learn`-written — never by hand.** `Create-mode` and `Focus areas` you can edit by hand any time — that's what they're for. Nobody is expected to hand-edit `Fulfilled nodes`; if it drifts wrong, the next pass with parser access overwrites it.
- The file travels with the repo. Loop state does not live in agent sessions but here (create-mode, focus areas, pending tasks, fulfilled nodes), in the issue tracker (backlog), in `docs/refactoring/merge-requests.md` (open suite merge requests — only when the target's issue tracker has no native label mechanism; otherwise that state lives directly on the tracker as `refactor:delivered`-labeled issues), and in `docs/refactoring/out-of-scope/` (learned rejections).
- If the file is missing, that's the `loop-config` tooling-tree node — see above. Ordinary in every way except who writes which field and which branch it lands on for that one candidate — see the `loop-config` exception above.
