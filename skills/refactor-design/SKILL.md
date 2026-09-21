---
name: refactor-design
description: Turn a chosen or already-selected candidate into a concrete refactoring plan — file it fresh for a tooling-tree node, or add the plan as a comment on an issue refactor-prioritize already filed.
---

# Refactor Design

Turn what `refactor-prioritize` handed forward into a **plan** concrete enough to implement. An ordinary tooling-tree node or an externally-labeled candidate: this is where it first becomes an issue (or gets updated), same as always. A gate-shaped candidate (`structural-scan`, a PHPStan baseline-shrink family): `refactor-prioritize`'s own Select mode already picked it and filed a minimal issue — this skill grounds and grills it, then adds the plan as a comment on that same issue, never filing a second one. `/grilling` sharpens a structural design; `/domain-modeling` keeps the domain model current as decisions land. Grilling that settles live also leaves a **Decision trail** on the issue (`structural-candidate.md` step 4) — separate from and unrelated to the decision gate below: the trail only records an already-resolved decision, the gate blocks an unresolved one.

## Process

### 1. Check whether it's already fully specified

An ordinary **tooling tree** node (`skills/refactor-scan/references/tooling-tree.md`, or a language specialization's tree) is fully specified by definition — Tool, Purpose, Fulfilment check, MR scope are already written in the tree doc. Skip straight to step 5 and file/write the plan from that spec — no grounding, no grilling.

**An externally-labeled candidate** (`refactor-scan` step 3b — an issue a human or another process labeled `refactor:candidate` directly, not one this loop selected): not fully specified by definition, even if its body already reads like a complete request — confirm it names a concrete module/seam/interface before skipping ahead. Run steps 3–4 (grounding, grilling — `skills/refactor-design/references/structural-candidate.md`) using the issue's own stated request — and any existing comments on it — as the starting friction signal in place of a fresh codebase search's, then continue at step 5, adding the sharpened plan as a comment on that same issue. Already fully specified as written → skip straight to step 5 like any other pre-specified candidate.

**A structural candidate** — `refactor-prioritize`'s Select mode already picked one and filed it minimally (Where/Problem/Signal); this skill never sees the bare `structural-scan` gate name. Steps 3–4 (ground in it, grill toward the seam) live at `skills/refactor-design/references/structural-candidate.md` — run them in full, then return here for step 5.

**A PHPStan baseline-shrink candidate** — same shape: `refactor-prioritize`'s Select mode already picked the group and filed it minimally (`refactor-scan` step 4b's proposal, refined). Run `skills/refactor-design/references/phpstan-baseline-shrink.md` step 3 (plan the fix), then continue here at step 5. Steps 3–4 above (the structural-candidate reference) don't apply — this candidate's own reference file is the whole procedure.

### 5. File the issue, or add the plan as a comment

**Decision gate first.** Grounding/grilling (structural, externally-labeled) or planning a fix
(PHPStan baseline-shrink) may have turned up a decision needing human confirmation, or a genuine
breaking change — `skills/refactor-design/references/decision-gate.md`. A breaking change → stop
here entirely; nothing below applies to this candidate this pass (`refactor-learn`'s closing call
handles it instead). A flagged decision → continue below exactly as usual, writing the plan and the
open question together — the difference from an ordinary candidate is the labels: `decision-gate.md`
handles those itself (`needs-info` added, `ready-for-agent` removed if present), so skip this step's
own "Set `ready-for-agent`, last" below for this candidate this pass.

**Tooling-tree node:** check first whether an issue titled exactly `Tooling tree: <Name>` (never the slug) is already open. Open but still minimal (Purpose line only, no Fulfilment check/MR scope — `refactor-prioritize`'s own pre-filing, step 2, hasn't won a ranking until now) → that's the issue, update its body now rather than filing a second one. Open and already carrying the full content (a prior pass got this far and was interrupted) → that's the issue, nothing to write here either. Neither found → file one fresh, titled that way, label **`refactor:candidate`**. Writing the body either way: the tree doc's content directly (Purpose, Fulfilment check, MR scope carried over precisely — they're load-bearing, that scope *is* the plan) — never introduced as a quotation or naming the tree doc's file path; it reads as its own plan. Skip `Name:` (already the title); skip `Tool` when `none`.

`docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab) → **skip writing `Pending candidates`** — nothing needs it. `refactor-implement` running later this same pass opens a branch/MR that `refactor-scan` step 3's native-tracker reconciliation already discovers on its own; the pass ending here instead means a future pass simply rediscovers this same issue via step 3b (still open, still `refactor:candidate`, not yet accounted for) and re-proposes it normally — this step's own dedupe above already stops it from being refiled. No native-label tracker → unchanged: set the Refactoring Notes' `bookkeeping.md`'s `Pending candidates` to this issue (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`) via the dedicated bookkeeping branch — lets a future `refactor-scan` resume this exact work if the pass stops here; `refactor-learn` clears it once a merge request exists.

**Externally-labeled candidate:** add the sharpened plan (deepened module, seam and interface, surviving tests, slice ordering) as a comment on the existing issue — never edit its body, never file a second issue. `Pending candidates` handling is the same as the tooling-tree node's above (native tracker skips it; otherwise set it) — this is still the first time this skill has touched the field for this candidate.

**Structural candidate, or PHPStan baseline-shrink candidate:** add the plan as a comment on the issue `refactor-prioritize`'s Select mode already filed — deepened module, seam and interface, surviving tests, slice ordering (structural); the planned fix for this MR's slice of the group (baseline-shrink, per `phpstan-baseline-shrink.md` step 3). Don't touch `Pending candidates` here — Select mode already set it when it filed, and it stays set until `refactor-learn` clears it once a merge request exists, same as any other candidate.

The plan follows the foundational refactoring rules: `skills/continuous-refactoring/references/foundational-refactoring-rules.md`.

**Set `ready-for-agent`, last, unconditionally.** Reaching this point at all already means the
decision gate above (where it applies) found neither a flagged decision nor a breaking change this
pass — for a tooling-tree node, the gate never runs at all, so this step is the only
label handling they ever get. Once the writes above are done — freshly written, updated, or already
complete from an earlier interrupted pass — add `ready-for-agent` (`docs/agents/triage-labels.md`) if
the issue doesn't already carry it; leave it if it does. This is design's own explicit confirmation
that the candidate is ready to implement, not merely its silence — and it's what lets a later pass
(`refactor-scan/SKILL.md` steps 2 and 3b), or a human running these skills by hand, recognize a
fully-designed issue on sight, whether its plan lives in the body (tooling-tree node)
or a comment (everything else). A flagged candidate never reaches this step this pass — `decision-gate.md` already handled its labels instead.

## Output

The candidate issue, now carrying the plan (freshly filed here, or already filed by `refactor-prioritize`'s Select mode and now commented) → `refactor-implement`.

## Fallback

- **`/grilling`**: installed → use it. Otherwise mechanics (design tree, frontier, rounds) inlined at `skills/refactor-design/references/grilling-fallback.md`.
- **`/domain-modeling`**: installed → use its discipline. Otherwise the same reference file inlines these side effects — also inline at `structural-candidate.md` (step 4), and run regardless of whether this skill is installed.

## Completion criterion

The candidate has an issue (newly filed, or already filed by `refactor-prioritize` and now commented) with a written plan — and, unless the decision gate flagged it (`needs-info` instead) or found a breaking change (no plan at all), `ready-for-agent` set. For a fresh filing (tooling-tree node, externally-labeled candidate) — no native-label tracker only — `bookkeeping.md`'s `Pending candidates` names it (a native-label tracker deliberately skips this write; see step 5); for a structural/baseline-shrink candidate, `Pending candidates` was already set by `refactor-prioritize`'s Select mode, nothing new to check here. Structural: module, seam, interface, surviving tests, slice order — design survives grilling (no open frontier). Tooling tree node: the tree doc's Purpose/Fulfilment check/MR scope, carried onto the issue as its own plan. PHPStan baseline-shrink: a fix planned for this MR's slice of the group `refactor-prioritize` already picked — see `phpstan-baseline-shrink.md`.
