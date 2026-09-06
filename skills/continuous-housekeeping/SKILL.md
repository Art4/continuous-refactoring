---
name: continuous-housekeeping
description: Run one recurring maintenance sweep when due — dependency currency, tooling-deprecation fixes, documentation sync. Separate from the continuous-refactoring loop; triggers on its own configurable cadence.
disable-model-invocation: true
---

# Continuous Housekeeping

A periodic maintenance sweep, deliberately **separate** from the continuous-refactoring loop's own scan → prioritise → design → implement → learn pipeline — not a tooling-tree node, never proposed by `refactor-scan`, never ranked by `refactor-prioritize`. Nothing about housekeeping is a one-time adoption with a stable Fulfilment check; it's the same handful of maintenance concerns, revisited on a timer, for as long as the target repo exists.

Run this on demand, or via your own recurring trigger — same posture as `continuous-refactoring` itself: this skill has no schedule of its own either, only a **cadence it checks against**, so a trigger firing early or late just means the next check reports "not due yet" or "due" accordingly.

## Process

### 1. First-run setup

Read the Refactoring Notes' `bookkeeping.md`. `Housekeeping cadence` already set → skip to step 2.

Missing → run `skills/continuous-housekeeping/references/cadence-interview.md` (one question, default `weekly`), record the answer in `bookkeeping.md`, then continue with step 2 in this same run — no need to stop and wait for a second trigger.

`bookkeeping.md` itself missing entirely (the target hasn't adopted `loop-config` yet) → stop here and say so; this skill depends on the Refactoring Notes existing, same as everything else in the suite.

### 2. Is a sweep due?

Find the most recently created issue whose title starts with `Housekeeping — ` (via whatever `docs/agents/issue-tracker.md` names — the same tracker abstraction every other skill in this suite reads, never assumed or hardcoded here).

- **None exists yet** → due now (first-ever sweep).
- **One exists, still open** → resume it (step 4), don't compute due-ness again.
- **Most recent one is closed** → due once its creation date plus `Housekeeping cadence` has passed; not due yet → stop and report when it next becomes due.

No stored "last run" date anywhere — the tracker's own history is the record, same as it already is for every other kind of loop state this suite keeps on the forge rather than duplicating into a file.

### 3. Read the accumulated checklist

Read the Refactoring Notes' `housekeeping-template.md` (`skills/continuous-housekeeping/references/template-file-format.md` for its exact shape). Missing, or present but empty of contributed lines → nothing has ever been registered to check yet (no tooling-tree node has delivered its own `Housekeeping` line — see `CONTEXT.md`'s **Tooling tree** entry). Report "due, but nothing registered to check yet" and stop — don't open an empty issue.

### 4. Open (or resume) this cycle's issue

New sweep: file an issue titled `Housekeeping — <today's date>`, body = every line from `housekeeping-template.md` as an unchecked checkbox, in the file's own order, plus the standing item from step 5 as one more checkbox (always present, not sourced from the template file). Resuming: use the existing open issue from step 2 as-is.

Branch `chore/housekeeping-<today's date>` (existing → reuse, don't reset).

### 5. Work the checklist

Standing item, every cycle, regardless of what the template file names: **check whether `AGENTS.md`/`CLAUDE.md`, this repo's own skills, or its own house rules need updating** for anything the other checklist items are about to touch (a dependency bump, a tooling version change). Adjust, or note "no adjustment needed" directly on the issue — either way, check the box.

For every other item (each one a `Housekeeping` line some tooling-tree node contributed): do the work the line names, update the issue body with the result (check the box; append a short report if the line calls for one — output worth keeping, not a restated checkbox), then commit. Batch related items into one commit each rather than one commit per checkbox if that reads more naturally.

**Judgement calls, not silent decisions:**
- A finding with no clean fix (an audit advisory with no available patched version, a breaking update that can't be made green within this sweep's own scope) → document it on the issue and ask the human rather than deciding unilaterally; never ship a broken result to look "done."
- Don't invent new skills, rules, or tooling-tree adoptions while doing housekeeping — this sweep keeps what's already adopted current, it doesn't adopt anything new (that's `continuous-refactoring`'s own job).

### 6. Quality gate

Whatever this target repo's own full quality-check command is (composer/npm/etc. script, or the equivalent CI job run locally) must pass before step 7 — same bar any other suite merge request already holds itself to.

### 7. Deliver

**Any code change made:** open the merge request per `skills/continuous-refactoring/references/opening-a-merge-request.md` (same create-mode, stacking, and description rules every other suite MR already follows) — referencing this cycle's issue so it closes on merge, per that document's own conventions. Do not close the issue directly.

**Zero code changes** (every item this cycle turned out to be already current) — no MR to gate a close behind; close the issue directly, with a comment saying so, and stop.

## Completion criterion

Either the sweep wasn't due and that's reported, nothing was registered to check and that's reported, or this cycle's issue has every item checked (with its report/decision recorded) and is either delivered via merge request or closed directly (zero changes) — never left half-checked with the pass reported as finished.
