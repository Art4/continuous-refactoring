# Orchestrator passes explicit data between skills; scan detects, design searches, learn writes

> Amends [ADR-0005](0005-tooling-tree-not-baseline-skill.md): "Scan files missing-tool and structural candidates together" no longer holds — `refactor-scan` files nothing at all; it proposes tree nodes, and issues for a chosen node are filed by `refactor-design`.
>
> Amends [ADR-0006](0006-loop-delivers-remembered-merge-requests.md) (itself amended by [ADR-0009](0009-merge-request-outlook-and-delivered-label.md)): the pass no longer *starts* from remembered merge-request state inline in the orchestrator. `refactor-scan` detects it (comments arrived, merged, closed); `refactor-learn` acts on it (follow-up-commit note, `done`, `wontfix` + out-of-scope entry).
>
> Amends [ADR-0008](0008-generic-tool-tree-and-structural-scan-gate.md): `structural-scan`'s "MR scope" changes. It no longer resolves inline inside `refactor-scan`'s own codebase walk; once the gate opens, `structural-scan` is proposed like any other node, and the codebase walk that finds an actual candidate happens in `refactor-design`, only for the node actually chosen.

Testing the loop end-to-end surfaced a structural problem, not a bug: `refactor-scan` files candidates as issues, and every downstream skill (`refactor-prioritize`, `refactor-design`, `refactor-implement`, `refactor-review`) re-derives its own context by querying the same shared state (the issue tracker, `docs/refactoring/merge-requests.md`, `docs/refactoring/config.md`) independently. Nothing hands a skill what it needs; every skill goes and finds it. That makes the pass hard to reason about — there is no single place that shows what flows from one step to the next — and it duplicates work: `refactor-scan` already walks the codebase for `structural-scan` candidates on every pass once the gate is open, whether or not any of them will be chosen this pass.

This ADR turns the orchestrator into an actual data pipe. Each lifecycle skill takes explicit input from the orchestrator and returns explicit output; the orchestrator's only job is to carry that output to the next skill's input. State documents (`config.md`, `merge-requests.md`, tooling-tree docs) stay readable by any skill directly — reading local project state is not the problem this ADR fixes. What changes is which skill is responsible for turning that state into a *decision*, and which skill is responsible for *writing* it back.

Two roles concentrate work that used to be scattered:

- **`refactor-scan` only detects, it never writes.** It proposes up to five tree nodes derived from `config.md` and the active tooling tree(s) — no codebase walk, no issue filed. Separately, it checks whether any issue/MR remembered in `merge-requests.md`/`config.md` has since been merged or closed on the external tracker, and hands that finding straight to `refactor-learn` rather than acting on it itself.
- **`refactor-learn` (new) is the only skill that writes suite bookkeeping.** It replaces two things that used to live inline in the orchestrator: the pass's opening merge-request pickup (ADR-0006) and its closing "Learn" step. It takes two kinds of input — scan's reconciliation findings, and `refactor-implement`'s freshly opened MR — and is the sole owner of `merge-requests.md`, `docs/refactoring/out-of-scope/`, ADRs, `CONTEXT.md`, `config.md`'s last-run stamp, and issue labels.

`structural-scan` stops being a special case `refactor-scan` resolves by walking code inline. Per ADR-0008 it is still gated behind every tooling leaf being resolved, but once open it is just another node scan can propose — a name, not a candidate. The actual codebase walk — hot spots, module/interface/depth/seam vocabulary — moves to `refactor-design`, and only runs for the node the human actually picked, not speculatively on every pass.

`refactor-review` retires as a standalone lifecycle skill. The suite already depends on `mattpocock/skills`' implement skill (`setup-matt-pocock-skills`, `README.md`) for `refactor-implement`, and that skill already embeds review. Keeping a separate top-level review step duplicated a check the installed dependency already performs. `refactor-implement` calls into review as part of its own step now, the same way it already calls into `/tdd`; a small inline fallback covers the case where `mattpocock/skills` isn't installed.

## Considered Options

- **Keep `refactor-scan` filing issues immediately, status quo.** Rejected — this is the friction that prompted the redesign: every downstream skill has to rediscover what scan found instead of receiving it.
- **Leave every skill free to query the tracker/state independently, status quo.** Rejected — implicit coupling with no single place to see the data flow, and no way to enforce that only one skill actually writes suite bookkeeping.
- **Keep `structural-scan` resolved inline by `refactor-scan`'s own codebase walk (ADR-0008 status quo).** Rejected — `refactor-scan` pays the cost of a full structural walk on every pass regardless of whether the gate just opened and regardless of whether any candidate found will be chosen; moving the walk to `refactor-design` means it only runs for the node actually selected.
- **Keep `refactor-review` as its own top-level pass step.** Rejected — the suite already relies on `mattpocock/skills`' implement skill, which embeds review; a redundant separate step re-does a check the installed dependency already makes, and the suite is not meant to work without that dependency's core review behavior (only a small fallback covers its absence).
- **Introduce a third skill for tracker reconciliation, separate from both scan and learn.** Considered, rejected for now — there is no independent decision this third skill would make beyond "detect" (scan's job) and "write" (learn's job); it would only add an orchestrator hop.
- **Let `refactor-scan` write reconciliation results itself instead of handing them to `refactor-learn`.** Rejected — it would leave two skills writing suite bookkeeping (scan for reconciliation, learn for everything else), reintroducing the "who owns this write" ambiguity this ADR removes.

## Consequences

The pass becomes: `refactor-scan` → `refactor-prioritize` → `refactor-design` → `refactor-implement` → `refactor-learn`, with the orchestrator passing each skill's output as the next skill's input.

`refactor-scan`'s output is always the same shape — up to five tree-node names derived from `config.md` and the active tooling tree(s), `structural-scan` included once it is open — plus, separately, any reconciliation findings (merged/closed issues+MRs) for `refactor-learn`. It files no issues and performs no codebase walk.

`refactor-prioritize` reads `config.md`/`merge-requests.md`/tooling-tree docs directly (this is not exclusive to scan), ranks the up-to-five node names, and returns one chosen node plus rationale — or "nothing to do" with a reason, which the orchestrator can end the pass on. It still recognizes two-suite-MRs-open as a reason to stop.

`refactor-design` turns the chosen node into a spec and files the issue itself — the point at which a node first gets an issue at all. For an ordinary tooling node the spec is the tree doc's existing Tool/Purpose/Fulfilment/MR-scope entry (unchanged from ADR-0008). For `structural-scan`, design now performs the codebase walk that `refactor-scan` used to do, picks one candidate, and specs it.

`refactor-implement` executes the design and is responsible for the MR, including the review check that used to be `refactor-review`'s own pass step — delegated to `mattpocock/skills`' implement skill where installed, with a small inline fallback otherwise.

`refactor-learn` is the pass's only writer of suite bookkeeping: `merge-requests.md`, `docs/refactoring/out-of-scope/`, ADRs and `CONTEXT.md` (via `/domain-modeling`), `config.md`'s last-run stamp, and issue labels (`done`, `wontfix`, `refactor:delivered`). It runs up to twice, never more: an early call right after `refactor-scan`, only when scan produced findings, so the ledger is current before `refactor-prioritize` reads it to check whether two merge requests are already open; and a closing call, always, at the end of the pass. A single end-of-pass call was the first draft of this ADR — dry-run testing (below) found it lets `refactor-prioritize` read a stale ledger in the same pass a finding was discovered but not yet written back.

`docs/tooling-tree.md`'s `structural-scan` node description changes: its "MR scope" no longer says the codebase walk is `refactor-scan`'s; it becomes `refactor-design`'s, run only for the chosen candidate once this node is selected.

`docs/agents/skill-references.md`'s audit table needs updating once skills are rewritten: the `refactor-review` row drops, `refactor-implement` gains its `mattpocock/skills` dependency, and `refactor-learn` gains a row for its `/domain-modeling` reference (crash-safe, same as `continuous-refactoring`'s entry today).

Node-detail data (what a given tooling node's fulfilment unlocks next, e.g. what reaching `phpstan-level-1` opens up) is out of scope here — deferred, to be filled in per node as it comes up, consistent with ADR-0005's "policy numbers are not defaults on the parent node — they are child candidates, specified when that child is designed."

## Validation

Dry-run against an isolated copy of a real target repo, three passes on a minimal synthetic tree (`git → loop-config → composer → structural-scan`), each pass driven by a fresh subagent following only the rewritten skill texts: pass 1 (`loop-config` from empty state), pass 2 (reconciling `loop-config`'s merge, delivering `composer`), pass 3 (`structural-scan` open, `refactor-design` searching real application code for a candidate). Found and fixed two real bugs this design surfaced, beyond wording:

- `scripts/lib/tooling_tree.py`'s new `next_candidates()` had gated `structural-scan` behind the same "already fulfilled, skip" check every ordinary node uses — but `structural-scan`'s `fulfilled` flag means the gate is *open*, not that the node is delivered and done, so that check made the node permanently unreachable the moment its gate opened. Fixed by checking it on its own terms first.
- The single end-of-pass `refactor-learn` call (this ADR's first draft) let `refactor-prioritize` read a stale `merge-requests.md` in the same pass a finding was resolved but not yet written back, risking an incorrect "two merge requests already open" stop. Fixed by splitting `refactor-learn` into an early call (findings, right after `refactor-scan`) and a closing call (always, at the end) — see `refactor-learn`'s `SKILL.md` and the pass order above.

Also surfaced, and fixed directly in the affected skill: a `loop-config` bootstrap gap (`refactor-design` can't set `Pending issue` in a `config.md` that doesn't exist yet, since `loop-config` is the candidate that creates it) — see the `loop-config` exception in `refactor-design`, `refactor-implement`, and `refactor-learn`.
