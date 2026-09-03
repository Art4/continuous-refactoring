# Reference: `bookkeeping.md`, in the target repo's Refactoring Notes

The config file the suite reads and writes. It doesn't exist on a fresh target repo: `refactor-scan` proposes it (the `loop-config` node, `skills/refactor-scan/references/tooling-tree.md`), `refactor-design` runs a human interview instead of copying the tree doc's generic spec (`skills/continuous-refactoring/references/loop-config-interview.md`) and files the recorded decisions as a single `refactor:candidate` issue, and `refactor-implement` creates the file when that candidate is implemented — the same path any other tooling-tree node takes.

## Where the Refactoring Notes live

The **Refactoring Notes** are the target repo's own folder holding the loop's state — `bookkeeping.md` (this file), `merge-requests.md`, `out-of-scope/`. Default `docs/refactoring/`; overridable per target, decided once during `loop-config`'s own interview (`skills/continuous-refactoring/references/loop-config-interview.md`, Q3) and recorded, by that name, in the target's `AGENTS.md`/`CLAUDE.md`.

**Resolution rule**, followed independently by every lifecycle skill (and by the deterministic parser, `skills/refactor-scan/references/tooling_tree.py`) wherever it needs the Refactoring Notes, the same way the suite already resolves "does the tracker support native labels" from `docs/agents/issue-tracker.md` — not a value threaded through the orchestrator's carried-data chain: read the target's `AGENTS.md`, and if that doesn't exist or doesn't name one, `CLAUDE.md` — whichever names a line matching `` Refactoring Notes: `<path>` `` (path backtick-quoted, trailing slash optional) wins. Neither names one → the Refactoring Notes default to `docs/refactoring/`.

Every other skill in this suite refers to this folder by name — "the Refactoring Notes" — never by restating or assuming the concrete path; this section is the one place the resolution rule itself is defined.

## Structure

```markdown
# Refactoring Loop Config

**Create-mode:** autonomous

**Focus areas:** order intake, billing

**Pending candidates:**
- none

**Skip streak:**
- php-cs-fixer: 3

**Fulfilled nodes:**
- loop-config
- composer (#77)
- ci-runner (#78)
```

`Fulfilled nodes` sorts last, not alphabetically or by write-frequency — it's the field most likely to grow long as the tree gets worked through, and the only-ever-growing one; keeping it below every other field means `Create-mode`, `Focus areas`, `Pending candidates`, and `Skip streak` stay visible together without scrolling past it.

## Fields

| Field | Meaning | Written by |
|---|---|---|
| `Create-mode` | How merge requests get opened: `autonomous`, `ask-each-time`, or `human-opens` | `refactor-implement`, once, during `loop-config`'s own interview (`skills/continuous-refactoring/references/loop-config-interview.md`) — hand-editable after that, same as `Focus areas` |
| `Focus areas` | Areas scans should target first | you, any time |
| `Pending candidates` | A one-item list (a bullet under the header, `- none` when empty) holding the issue `refactor-design` just filed, not yet delivered as a merge request. Written as a list purely for formatting consistency with `Fulfilled nodes` and easier diffing — it still holds at most one entry; the suite tracks exactly one thing in flight at a time (`refactor-scan`/`refactor-prioritize`), this is not a multi-pending queue. | `refactor-design` sets it when it files; `refactor-learn` clears it once the merge request is remembered (`merge-requests.md`) or the candidate is resolved another way |
| `Skip streak` | Tooling-tree node slugs paired with a consecutive-skip count (`- <slug>: <N>`), omitted entirely when empty (no bullet at all, not even `- none` — an empty field and a field that's never had an entry look the same, and that's fine: both mean "nothing has ever been skipped"). One of `refactor-prioritize`'s five ranking factors — see *Skip streak* below | `refactor-learn`, every closing call — see *Skip streak* below |
| `Fulfilled nodes` | Tooling-tree node **slugs** (never Names — internal bookkeeping stays keyed by the slug) already confirmed fulfilled, one per bulleted line, each carrying the delivering issue # (`- <slug> (#<issue>)`) when known — see *Fulfilled nodes* below. Sorts last — see the note above the table. | `refactor-learn`, every closing call — see *Fulfilled nodes* below |

`Pending candidates` exists so a pass interrupted between design and implement doesn't get re-proposed as fresh work by the next `refactor-scan` — scan reads this field before walking the tree, and if it names an issue, that pending issue is the only thing it proposes this pass.

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
  a pass has parser access, whenever that is. Reads the file as currently committed first, so the
  overwrite carries forward every already-known `(#N)` annotation, keyed by slug — the parser itself
  never produces issue numbers, only slugs. When this pass ran the fallback instead, `refactor-learn`
  only adds newly-confirmed slugs from this pass's own walk, each with this pass's delivering issue #
  if one exists — it does not attempt to verify or prune entries it didn't itself just check.
- **Per-entry metadata: only the delivering issue #**, `- <slug> (#<issue>)` — omitted for an entry
  that predates this convention or whose delivering issue is otherwise unknown (never invented). No
  other per-entry metadata (no timestamp, no "as of which pass") — that kind of field in a versioned,
  repeatedly-rewritten file invites merge conflicts for no operational benefit; an issue # is worth
  the small conflict surface because it answers a real question ("which change delivered this node")
  a timestamp doesn't.
- A node **never appears in `Fulfilled nodes` and the Refactoring Notes' `out-of-scope/` at the same
  time** — fulfilled and rejected are different, mutually exclusive states for a node; rejection state
  lives entirely in `out-of-scope/` (one file per rejected node), never duplicated here. A node moves from
  rejected to fulfilled only through the normal reversal path (an out-of-scope entry removed, then the
  node adopted for real) — see `skills/refactor-scan/references/php-tooling-tree.md`'s Nodes intro and
  `skills/refactor-learn/SKILL.md`.

**`loop-config` exception:** for the `loop-config` candidate itself, this file doesn't exist yet when `refactor-design` would normally write `Pending candidates` — `refactor-implement` sets it directly when it creates the file instead, alongside `Create-mode` (already decided by the interview `refactor-design` ran for this candidate) — leaving only the first `Fulfilled nodes` entry (`loop-config (#<its own issue>)`, at minimum) for `refactor-learn`'s own follow-up commit. Because the file only exists on that candidate's own (not yet merged) branch, `refactor-learn`'s writes land there too, the one time bookkeeping doesn't go straight to the default branch. Every pass after that, once the file is on the default branch, all of this is as described in the table above.

## `Skip streak`

A per-node counter — how many consecutive passes proposed this node without choosing it — that exists purely to feed `refactor-prioritize`'s fifth ranking factor of the same name: a `required` tooling-tree sibling that never wins on Heat/Leverage/Tooling pressure/Risk alone can otherwise be proposed and passed over indefinitely, one round at a time, forever.

- **Read:** only by `refactor-prioritize`, as one input among five — never a forcing rule, never read by anything else.
- **Write:** `refactor-learn`, every closing call, alongside `Fulfilled nodes`. Re-derive the set of `required` tooling nodes that were proposable this pass but not chosen the same way `Fulfilled nodes` is re-derived — via the deterministic parser's current unblocked set when `python3` is available — rather than threading a new value through `refactor-design`/`refactor-implement`'s handoff chain. Increment each of those by 1; reset the node that was chosen (or newly fulfilled) to 0, which in practice means dropping its entry — a node at 0 isn't written at all (see below).
- **Omit zero entries.** A node with no skip streak (never proposed-and-passed-over, or just reset to 0) gets no bullet — don't write `- <slug>: 0`. This keeps the field's size proportional to how many nodes are actually starving, not to the tree's total size.
- **No cross-pass ordering metadata** (no timestamp, no "as of which pass") — same reasoning as `Fulfilled nodes`: a versioned, repeatedly-rewritten field gains nothing operationally from it and only adds merge-conflict surface.
- **Depends on suite MRs always stacking, never branching parallel off the default branch, while one is open** (`skills/continuous-refactoring/SKILL.md`'s merge-request-opening guidance). A per-node counter rewritten by every closing call is exactly the shape that caused repeated bookkeeping-merge-request conflicts before, back when a single `Pending candidates`-style field could be touched by two concurrently open branches at once. With every suite branch serialized behind whatever's currently open, only one write to this field is ever in flight at a time.

There is deliberately no `Cadence` field: the loop never triggers itself — you kick it off whenever it's due, whether that's you running `/continuous-refactoring` by hand or a scheduler you set up outside the suite. Nothing here would read a stored cadence, so nothing stores one.

## Rules

- **`Pending candidates`, `Fulfilled nodes`, and `Skip streak` are `refactor-learn`-written — never by hand.** `Create-mode` and `Focus areas` you can edit by hand any time — that's what they're for. Nobody is expected to hand-edit `Fulfilled nodes` or `Skip streak`; if either drifts wrong, the next pass with parser access re-derives it.
- The file travels with the repo. Loop state does not live in the agent's own conversation but here (create-mode, focus areas, pending candidates, fulfilled nodes), in the issue tracker (backlog), in the Refactoring Notes' `merge-requests.md` (open suite merge requests — only when `docs/agents/issue-tracker.md` names no native-label tracker; otherwise that state lives directly on the tracker, as every open `refactor:candidate` issue's own native link to its delivering pull request), and in the Refactoring Notes' `out-of-scope/` (learned rejections).
- If the file is missing, that's the `loop-config` tooling-tree node — see above. Ordinary in every way except who writes which field and which branch it lands on for that one candidate — see the `loop-config` exception above.
