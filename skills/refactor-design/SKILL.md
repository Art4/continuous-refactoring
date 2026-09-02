---
name: refactor-design
description: Turn the chosen node into a concrete refactoring plan, filing it as an issue — search the codebase first when the node is structural-scan.
---

# Refactor Design

Turn the **node** `refactor-prioritize` chose into a **plan** concrete enough to implement, and file it as the issue that carries that plan — this is where a node first becomes an issue, not `refactor-scan`. `/grilling` sharpens a structural design; `/domain-modeling` keeps the domain model current as decisions land.

## Process

### 1. Check whether it's already fully specified

An ordinary **tooling tree** node (`skills/refactor-scan/references/tooling-tree.md`, or a language specialization's tree) is fully specified by definition — Tool, Purpose, Fulfilment check, MR scope are already written in the tree doc. Skip straight to step 5 and file/write the plan from that spec — no codebase search, no grilling.

**`loop-config` exception:** not fully specified by the tree doc alone — its MR scope names a human interview, not a fixed spec. Run `skills/continuous-refactoring/references/loop-config-interview.md` in full (explore, ask, summarize, record) before filing anything; skip step 5's usual "carry the tree doc's spec over precisely" move for this node only — file the interview's recorded decisions instead (step 5). Steps 2–4 (structural-candidate search, grilling) still don't apply — this stays a tooling-tree node in every other way.

The **`structural-scan`** node names an open gate, not a candidate. Steps 2–4 (find a candidate, ground in it, grill toward the seam) live at `skills/refactor-design/references/structural-candidate.md` — run them in full, then return here for step 5.

### 5. File the issue and write the plan

**Tooling-tree node:** check first whether an issue titled exactly `Tooling tree: <Name>` (never the slug) is already open — that's the issue, don't file a second one (a prior pass got this far and was interrupted). Otherwise file one titled that way, label **`refactor:candidate`**, body = the tree doc's content directly (Purpose, Fulfilment check, MR scope carried over precisely — they're load-bearing, that scope *is* the plan) — never introduced as a quotation or naming the tree doc's file path; it reads as its own plan. Skip `Name:` (already the title); skip `Tool` when `none`.

**Structural candidate:** file an issue labelled **`refactor:candidate`** naming Where (module/files), Problem (the friction, in the project's domain language), Signal (which step-2 friction signal). Capture the plan on that issue: deepened module, seam and interface, surviving tests, slice ordering (see `refactor-implement`).

Either way: set the Refactoring Notes' `config.md`'s `Pending candidates` to this issue (`skills/continuous-refactoring/references/refactoring-config.md`) — lets a future `refactor-scan` resume this exact work if the pass stops here. `refactor-learn` clears it once a merge request exists.

**`loop-config` exception:** chosen node *is* `loop-config` → the issue body isn't the tree doc's generic spec, it's what `skills/continuous-refactoring/references/loop-config-interview.md`'s `## Record` names (the interview's decisions, each with its one-line rationale). And `config.md` doesn't exist yet, so no `Pending candidates` to write here either — `refactor-implement` records it directly when it creates the file.

The plan follows the foundational refactoring rules: `skills/continuous-refactoring/references/foundational-refactoring-rules.md`.

## Output

The filed issue, carrying the plan → `refactor-implement`.

## Fallback

- **`/codebase-design`**: installed → use its vocabulary for step 2. Otherwise the full vocabulary is inline at `skills/refactor-design/references/structural-candidate.md` (step 2).
- **`/grilling`**: installed → use it. Otherwise mechanics (design tree, frontier, rounds) inlined at `skills/refactor-design/references/grilling-fallback.md`.
- **`/domain-modeling`**: installed → use its discipline. Otherwise the same reference file inlines these side effects — also inline at `structural-candidate.md` (step 4), and run regardless of whether this skill is installed.

## Completion criterion

The candidate has an issue (newly filed, or resumed) with a written plan, and `config.md`'s `Pending candidates` names it. Structural: module, seam, interface, surviving tests, slice order — design survives grilling (no open frontier). Tooling tree node: the tree doc's Purpose/Fulfilment check/MR scope, carried onto the issue as its own plan (`loop-config`: the interview's recorded decisions instead — see step 5's exception).
