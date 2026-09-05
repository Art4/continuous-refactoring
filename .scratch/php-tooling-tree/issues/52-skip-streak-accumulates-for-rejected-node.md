# 52 — Skip streak keeps accumulating for an already-rejected node

**What to build:** Stop `Skip streak` from accumulating an entry for a node that's already rejected
(has its own `docs/refactoring/out-of-scope/<node>.md` entry) — a rejected node isn't a proposable
candidate being passed over, so it shouldn't carry a skip streak at all. Root cause is a staleness
gap in the bookkeeping-write step, not a parser bug: `next_candidates()` already correctly excludes a
rejected node from `next` when run fresh, but a candidate branch created *before* a rejection lands
on `main` computes its own `Skip streak` against whatever local state it happens to have, not a fresh
fetch — so the rejected node still looks "proposable but skipped" from that branch's point of view.

**Why:** Live reviewer-loop finding (`Art4/legacy-todo`, 2026-09-05 —
`.scratch/legacy-todo-loop-observation/findings.md`, Round 8): the maintainer rejected
`phpstan-level-6` (PR #146 landed the out-of-scope entry on `main`). Two subsequent candidate
branches (`refactor/rector-type-coverage` PR #149, stacked `refactor/psalm-taint-analysis` PR #151)
were both created *before* that merge and wrote `Skip streak: phpstan-level-6: 1` and then `: 2` —
compounding with every pass, exactly the kind of silent, harmless-looking bookkeeping drift nobody
would think to question later if it had been merged. Caught by the reviewer before merging, not by
the suite itself.

**Blocked by:** none.

**Priority:** medium — not merged (reviewer caught it), but would keep recurring for any node rejected
mid-run while other candidate branches are already in flight; a real, structural gap in the write
step, not a one-off.

**Status:** done

- [x] Fix lives in `skills/refactor-learn/references/fulfilled-nodes-write.md`: a new "Read fresh, not
  stale" section — `git fetch origin` then `git checkout origin/main -- docs/refactoring/out-of-scope/
  docs/refactoring/bookkeeping.md` (working-tree sync only, no merge/rebase/commit) before computing
  either field. Plus the defense-in-depth rule: a node with an `out-of-scope/<node>.md` entry never
  gets a `Skip streak` entry, regardless of the raw parser result.
- [x] `Fulfilled nodes` has a worse version of the same risk, not just a moot one: its "overwrite the
  whole field" rule could silently drop a sibling PR's already-landed entry if this branch predates
  it — same fresh-sync fix closes this too, not just the skip-streak symptom.
- [x] Scoped broadly (grilling decision): fix the root cause (stale comparison inputs) generally,
  not just the rejected-node case narrowly — closes both the observed `Skip streak` bug and the
  not-yet-observed `Fulfilled nodes` risk with one change.

## Comments

> **2026-09-05:** Filed from the `Art4/legacy-todo` reviewer-loop findings log (Round 8), caught live
> before either PR merged. Same treatment as tickets 48–51: grill it, then implement on its own
> branch/PR.

> **2026-09-05 (later):** Design settled via a `/grill-me` session (in German), one round. Scoped
> broadly per the human's answer — fix the staleness root cause (fresh-sync before any bookkeeping
> write), not just the narrow rejected-node symptom — after discovering mid-grilling that
> `Fulfilled nodes`' own overwrite rule has a worse, not-yet-observed version of the same risk
> (silently dropping a sibling PR's already-landed entry). Mechanism: working-tree-only sync via
> `git checkout origin/main -- <paths>`, no merge/rebase, keeping the candidate branch's own history
> untouched. Implemented on branch `tickets/52-fetch-fresh-before-bookkeeping-write`: rewrote
> `fulfilled-nodes-write.md`, new ADR-0034. No `tooling_tree.py` change (pure skill-prose fix).
> Validator clean (same 5 pre-existing warnings after fixing one incidental new glossary hit from a
> since-removed target-repo-name mention); 251/251 tests unaffected (no Python behavior changed).
