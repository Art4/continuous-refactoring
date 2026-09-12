---
name: refactor-design
description: Turn a chosen or already-selected candidate into a concrete refactoring plan — file it fresh for a tooling-tree node, or add the plan as a comment on an issue refactor-prioritize already filed.
---

# Refactor Design

Turn what `refactor-prioritize` handed forward into a **plan** concrete enough to implement. An ordinary tooling-tree node, `loop-config`, or an externally-labeled candidate: this is where it first becomes an issue (or gets updated), same as always. A gate-shaped candidate (`structural-scan`, a PHPStan baseline-shrink family): `refactor-prioritize`'s own Select mode already picked it and filed a minimal issue — this skill grounds and grills it, then adds the plan as a comment on that same issue, never filing a second one. `/grilling` sharpens a structural design; `/domain-modeling` keeps the domain model current as decisions land.

## Process

### 1. Check whether it's already fully specified

An ordinary **tooling tree** node (`skills/refactor-scan/references/tooling-tree.md`, or a language specialization's tree) is fully specified by definition — Tool, Purpose, Fulfilment check, MR scope are already written in the tree doc. Skip straight to step 5 and file/write the plan from that spec — no grounding, no grilling.

**`loop-config` exception:** not fully specified by the tree doc alone — its MR scope names a human interview, not a fixed spec. Run `skills/continuous-refactoring/references/loop-config-interview.md` in full (explore, ask, summarize, record) before filing anything; skip step 5's usual "carry the tree doc's spec over precisely" move for this node only — file the interview's recorded decisions instead (step 5). Steps 3–4 (grounding, grilling) still don't apply — this stays a tooling-tree node in every other way.

**An externally-labeled candidate** (`refactor-scan` step 3b — an issue a human or another process labeled `refactor:candidate` directly, not one this loop selected): not fully specified by definition, even if its body already reads like a complete request — confirm it names a concrete module/seam/interface before skipping ahead. Run steps 3–4 (grounding, grilling — `skills/refactor-design/references/structural-candidate.md`) using the issue's own stated request as the starting friction signal in place of a fresh codebase search's, then continue at step 5, adding the sharpened plan as a comment on that same issue. Already fully specified as written → skip straight to step 5 like any other pre-specified candidate.

**A structural candidate** — `refactor-prioritize`'s Select mode already picked one and filed it minimally (Where/Problem/Signal); this skill never sees the bare `structural-scan` gate name. Steps 3–4 (ground in it, grill toward the seam) live at `skills/refactor-design/references/structural-candidate.md` — run them in full, then return here for step 5.

**A PHPStan baseline-shrink candidate** — same shape: `refactor-prioritize`'s Select mode already picked the group and filed it minimally (`refactor-scan` step 4b's proposal, refined). Run `skills/refactor-design/references/phpstan-baseline-shrink.md` step 3 (plan the fix), then continue here at step 5. Steps 3–4 above (the structural-candidate reference) don't apply — this candidate's own reference file is the whole procedure.

### 5. File the issue, or add the plan as a comment

**Tooling-tree node:** check first whether an issue titled exactly `Tooling tree: <Name>` (never the slug) is already open. Open but still minimal (Purpose line only, no Fulfilment check/MR scope — `refactor-prioritize`'s own pre-filing, step 2, hasn't won a ranking until now) → that's the issue, update its body now rather than filing a second one. Open and already carrying the full content (a prior pass got this far and was interrupted) → that's the issue, nothing to write here either. Neither found → file one fresh, titled that way, label **`refactor:candidate`**. Writing the body either way: the tree doc's content directly (Purpose, Fulfilment check, MR scope carried over precisely — they're load-bearing, that scope *is* the plan) — never introduced as a quotation or naming the tree doc's file path; it reads as its own plan. Skip `Name:` (already the title); skip `Tool` when `none`.

`docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab) → **skip writing `Pending candidates`** — nothing needs it. `refactor-implement` running later this same pass opens a branch/MR that `refactor-scan` step 3's native-tracker reconciliation already discovers on its own; the pass ending here instead means a future pass simply rediscovers this same issue via step 3b (still open, still `refactor:candidate`, not yet accounted for) and re-proposes it normally — this step's own dedupe above already stops it from being refiled. No native-label tracker → unchanged: set the Refactoring Notes' `bookkeeping.md`'s `Pending candidates` to this issue (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`) via the dedicated bookkeeping branch — lets a future `refactor-scan` resume this exact work if the pass stops here; `refactor-learn` clears it once a merge request exists.

**`loop-config` exception:** chosen node *is* `loop-config` → the issue body isn't the tree doc's generic spec, it's what `skills/continuous-refactoring/references/loop-config-interview.md`'s `## Record` names (the interview's decisions, each with its one-line rationale). And `bookkeeping.md` doesn't exist yet, so no `Pending candidates` to write here either — `refactor-implement` records it directly when it creates the file.

**Externally-labeled candidate:** add the sharpened plan (deepened module, seam and interface, surviving tests, slice ordering) as a comment on the existing issue — never edit its body, never file a second issue. `Pending candidates` handling is the same as the tooling-tree node's above (native tracker skips it; otherwise set it) — this is still the first time this skill has touched the field for this candidate.

**Structural candidate, or PHPStan baseline-shrink candidate:** add the plan as a comment on the issue `refactor-prioritize`'s Select mode already filed — deepened module, seam and interface, surviving tests, slice ordering (structural); the planned fix for this MR's slice of the group (baseline-shrink, per `phpstan-baseline-shrink.md` step 3). Don't touch `Pending candidates` here — Select mode already set it when it filed, and it stays set until `refactor-learn` clears it once a merge request exists, same as any other candidate.

The plan follows the foundational refactoring rules: `skills/continuous-refactoring/references/foundational-refactoring-rules.md`.

## Output

The candidate issue, now carrying the plan (freshly filed here, or already filed by `refactor-prioritize`'s Select mode and now commented) → `refactor-implement`.

## Fallback

- **`/grilling`**: installed → use it. Otherwise mechanics (design tree, frontier, rounds) inlined at `skills/refactor-design/references/grilling-fallback.md`.
- **`/domain-modeling`**: installed → use its discipline. Otherwise the same reference file inlines these side effects — also inline at `structural-candidate.md` (step 4), and run regardless of whether this skill is installed.

## Completion criterion

The candidate has an issue (newly filed, or already filed by `refactor-prioritize` and now commented) with a written plan. For a fresh filing (tooling-tree node, `loop-config`, externally-labeled candidate) — no native-label tracker only — `bookkeeping.md`'s `Pending candidates` names it (a native-label tracker deliberately skips this write; see step 5); for a structural/baseline-shrink candidate, `Pending candidates` was already set by `refactor-prioritize`'s Select mode, nothing new to check here. Structural: module, seam, interface, surviving tests, slice order — design survives grilling (no open frontier). Tooling tree node: the tree doc's Purpose/Fulfilment check/MR scope, carried onto the issue as its own plan (`loop-config`: the interview's recorded decisions instead — see step 5's exception). PHPStan baseline-shrink: a fix planned for this MR's slice of the group `refactor-prioritize` already picked — see `phpstan-baseline-shrink.md`.
