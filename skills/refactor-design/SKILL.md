---
name: refactor-design
description: Turn a chosen or already-selected candidate into a concrete refactoring plan — write it onto the issue refactor-loop created for a tooling-tree node, or add the plan as a comment on the issue of a gate-shaped or externally-labeled candidate.
---

# Refactor Design

Turn what `refactor-prioritize` handed forward into a **plan** concrete enough to implement. An ordinary tooling-tree node or an externally-labeled candidate: this is where its issue gets the full plan — the issue itself already exists, created by `refactor-loop` as a minimal issue (`../continuous-refactoring/references/filing-a-ticket.md`) and handed to this skill; this skill never creates an issue. A gate-shaped candidate (`structural-scan`, a PHPStan baseline-shrink family): `refactor-prioritize`'s own Select mode already picked it and drafted a minimal issue, which the loop created — this skill grounds and grills it, then adds the plan as a comment on that same issue. `/grilling` sharpens a structural design; `/domain-modeling` keeps the domain model current as decisions land. Grilling that settles live also leaves a **Decision trail** on the issue (`structural-candidate.md` step 4) — separate from and unrelated to the decision gate below: the trail only records an already-resolved decision, the gate blocks an unresolved one.

## Process

### 1. Check whether it's already fully specified

An ordinary **tooling tree** node (`../refactor-scan/references/tooling-tree.md`, or a language specialization's tree) is fully specified by definition — Tool, Purpose, Fulfilment check, MR scope are already written in the tree doc. Skip straight to step 5 and file/write the plan from that spec — no grounding, no grilling.

**An externally-labeled candidate** (`refactor-scan` step 3b — an issue a human or another process labeled `refactor:candidate` directly, not one this loop selected): not fully specified by definition, even if its body already reads like a complete request — confirm it names a concrete module/seam/interface before skipping ahead. Run steps 3–4 (grounding, grilling — `references/structural-candidate.md`) using the issue's own stated request — and any existing comments on it — as the starting friction signal in place of a fresh codebase search's, then continue at step 5, adding the sharpened plan as a comment on that same issue. Already fully specified as written → skip straight to step 5 like any other pre-specified candidate.

**A structural candidate** — `refactor-prioritize`'s Select mode already picked one and `refactor-loop` created its minimal issue (Where/Problem/Signal); this skill never sees the bare `structural-scan` gate name. Steps 3–4 (ground in it, grill toward the seam) live at `references/structural-candidate.md` — run them in full, then return here for step 5.

**A PHPStan baseline-shrink candidate** — same shape: `refactor-prioritize`'s Select mode already picked the group and `refactor-loop` created its minimal issue (`refactor-scan` step 4b's proposal, refined). Run `references/phpstan-baseline-shrink.md` step 3 (plan the fix), then continue here at step 5. Steps 3–4 above (the structural-candidate reference) don't apply — this candidate's own reference file is the whole procedure.

### 5. Write the plan onto the issue, or add it as a comment

**Decision gate first.** Grounding/grilling (structural, externally-labeled) or planning a fix
(PHPStan baseline-shrink) may have turned up a decision needing human confirmation, or a genuine
breaking change — `references/decision-gate.md`. A breaking change → stop
here entirely; nothing below applies to this candidate this pass (`refactor-learn`'s closing call
handles it instead). A flagged decision → continue below exactly as usual, writing the plan and the
open question together — the difference from an ordinary candidate is the labels: `decision-gate.md`
handles those itself (`needs-info` added, `ready-for-agent` removed if present), so skip this step's
own "Set `ready-for-agent`, last" below for this candidate this pass.

**Tooling-tree node:** the issue titled exactly `Tooling tree: <Name>` (never the slug) is handed to this skill — created by `refactor-loop` right after the ranking, or already there from an earlier pass. Still minimal (Purpose line only, no Fulfilment check/MR scope) → update its body now. Already carrying the full content (a prior pass got this far and was interrupted) → nothing to write here. No issue handed forward → stop and report that back to `refactor-loop`; never create one here. Writing the body: the tree doc's content directly (Purpose, Fulfilment check, MR scope carried over precisely — they're load-bearing, that scope *is* the plan) — never introduced as a quotation or naming the tree doc's file path; it reads as its own plan. Skip `Name:` (already the title); skip `Tool` when `none`.

`docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab) → **skip writing `Pending candidates`** — nothing needs it. `refactor-implement` running later this same pass opens a branch/MR that `refactor-scan` step 3's native-tracker reconciliation already discovers on its own; the pass ending here instead means a future pass simply rediscovers this same issue via step 3b (still open, still `refactor:candidate`, not yet accounted for) and re-proposes it normally — the loop's dedupe by title already stops it from being created twice. **Handed forward already marked as self-tracking** (whoever invoked this skill flags a candidate this way when its own admission path already keeps its own resume marker elsewhere — this skill never needs to know which, same treatment as the structural/baseline-shrink case below) → skip this write too, nothing to do here. Neither of the above (an ordinary fresh proposal, non-native tracker) → set the Refactoring Notes' `bookkeeping.md`'s `Pending candidates` to this issue (`../continuous-refactoring/references/refactoring-bookkeeping.md`) — lets a future `refactor-scan` resume this exact work if the pass stops here; `refactor-learn` clears it once a merge request exists. In issue mode, either write is saved to the bookkeeping issue before design returns (`../continuous-refactoring/references/issue-mode.md`, *Save*).

**Externally-labeled candidate:** add the sharpened plan (deepened module, seam and interface, surviving tests, slice ordering) as a comment on the existing issue — never edit its body. `Pending candidates` handling is the same as the tooling-tree node's above (native tracker skips it; otherwise set it) — this is still the first time this skill has touched the field for this candidate.

**Structural candidate, or PHPStan baseline-shrink candidate:** add the plan as a comment on the issue `refactor-loop` created from `refactor-prioritize`'s Select-mode draft — deepened module, seam and interface, surviving tests, slice ordering (structural); the planned fix for this MR's slice of the group (baseline-shrink, per `phpstan-baseline-shrink.md` step 3). **Set `Pending candidates` to this issue first, on every tracker, native-label ones included** — unlike the ordinary design→implement handoff above (which native trackers skip): a pass interrupted before this comment needs `refactor-scan` to resume exactly this issue next pass, not treat it as a fresh externally-labeled candidate and possibly select a different one. `refactor-learn` clears it once a merge request exists. In issue mode, either write is saved to the bookkeeping issue before design returns (`../continuous-refactoring/references/issue-mode.md`, *Save*).

The plan follows the foundational refactoring rules: `../continuous-refactoring/references/foundational-refactoring-rules.md`.

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

Name the writes this call made so the caller can report them — the issue filed, updated or commented, its labels set or removed, `Pending candidates` if written.

The candidate issue, now carrying the plan (its body updated, or the plan added as a comment) → `refactor-implement`.

## Fallback

- **`/grilling`**: installed → use it. Otherwise mechanics (design tree, frontier, rounds) inlined at `references/grilling-fallback.md`.
- **`/domain-modeling`**: installed → use its discipline. Otherwise the same reference file inlines these side effects — also inline at `structural-candidate.md` (step 4), and run regardless of whether this skill is installed.

## Completion criterion

The candidate has an issue (created by `refactor-loop` and updated or commented here) with a written plan — and, unless the decision gate flagged it (`needs-info` instead) or found a breaking change (no plan at all), `ready-for-agent` set. For a tooling-tree node or externally-labeled candidate — no native-label tracker only — `bookkeeping.md`'s `Pending candidates` names it (a native-label tracker deliberately skips this write; see step 5); for a structural/baseline-shrink candidate, `Pending candidates` names it on every tracker (step 5). Structural: module, seam, interface, surviving tests, slice order — design survives grilling (no open frontier). Tooling tree node: the tree doc's Purpose/Fulfilment check/MR scope, carried onto the issue as its own plan. PHPStan baseline-shrink: a fix planned for this MR's slice of the group `refactor-prioritize` already picked — see `phpstan-baseline-shrink.md`.
