# Housekeeping Track process

`continuous-refactoring/SKILL.md`'s own Housekeeping-specific process — run directly by the orchestrator
once the Track scheduler selects this Track, not handed to `refactor-scan` the way Safety Net,
Guardrails, and Investigation are (`skills/refactor-scan/references/safety-net-track.md`,
`guardrails-track.md`, `investigation-track.md`). This Track isn't a tooling-tree scan: it's a complete
due-check → reconcile → checklist-assembly → quality-gate → deliver pipeline in itself, the same shape
the now-retired standalone `continuous-housekeeping` skill always ran — preserved here **verbatim**
except for *how it gets triggered*, which is now this file's own first section, replacing that skill's
former steps 1–2 (its own setup interview and its own tracker-history due-check). Vocabulary:
`CONTEXT.md` (**Track**, **Housekeeping**, **Tooling tree**'s own **Housekeeping** field).

## Is the Track due this pass?

Decided once, before this file's own process starts — the orchestrator's own Track-selection step
(`skills/continuous-refactoring/references/track-scheduler.md`, `skills/continuous-refactoring/SKILL.md`
step 0b) computes every wired Track's `overdue_ratio` against `bookkeeping.md`'s `## Housekeeping`
section (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`) and hands the winner down
as this pass's selected Track. This section covers only what this Track does with that decision — it
never re-derives due-ness itself:

- **This Track wasn't the one step 0b selected** → nothing in this file runs this pass; the orchestrator
  continues with whichever Track was actually selected instead (or with its ordinary scan/prioritise/
  design/implement/learn pipeline, if none was due).
- **This Track is the one that was selected** → continue below. Housekeeping carries no `Open` precondition
  (`refactoring-bookkeeping.md`'s own `## Housekeeping` section) — always eligible the moment it's due,
  the same "no `Open` concept" shape `## Investigation` already has (`track-scheduler.md`'s own
  Eligibility section). Unlike Investigation, though, Housekeeping *does* carry a real numeric `Cadence`
  that competes in ratio comparison the same way `## Safety Net`'s/`## Guardrails`' own does — see
  *First-run cadence*, next.

## First-run cadence

`## Housekeeping` section absent (never run for this target) → this pass creates it, `Cadence: 7` —
the same default the old skill's own setup interview always recommended (`weekly`), applied silently
here instead: no interview question blocks an orchestrator-driven pass, the same "no first-run interview
at all" discipline `## Safety Net`'s 90-day default and `## Guardrails`' 60-day default already use
(`skills/refactor-learn/references/safety-net-write.md`, `guardrails-write.md`). A human who wants a
different interval either hand-edits `## Housekeeping`'s `Cadence` field directly — hand-editable, same
as `## Safety Net`'s/`## Guardrails`' own — or runs
`skills/continuous-refactoring/references/housekeeping-cadence-interview.md` themselves, any time, for a
guided one-question prompt instead of a bare number edit. That reference file is preserved for this
optional, human-initiated use; it no longer gates the Track's very first run the way it used to gate the
old skill's own first invocation.

## Resuming an in-progress cycle

Find the most recently created issue whose title starts with `Housekeeping — ` (via whatever
`docs/agents/issue-tracker.md` names — the same tracker abstraction every other skill in this suite
reads, never assumed or hardcoded here).

- **One exists, still open** → resume it: skip straight to *Work the checklist*, below — skip
  *Reconcile* and *Open this cycle's issue* entirely, continuing the open cycle exactly as it already
  stands.
- **None exists yet, or the most recent one is closed** → a fresh cycle: continue at *Reconcile*, below.

Tracked by the tracker's own history, same as before this Track was scheduler-driven — `## Housekeeping`
carries no `Open` list of its own (`refactoring-bookkeeping.md`), so this resume check reads the tracker
directly rather than a bookkeeping field, the same "detect, never duplicate" discipline the suite's
remembered-MR tracking already uses elsewhere.

## Reconcile, then read the accumulated checklist

**New cycle only** (skip this reconciliation when resuming an open cycle above — that one continues
exactly as it already stands): a node's own delivering merge request is the *ordinary* way a
`Housekeeping` line reaches `housekeeping-template.md`
(`skills/continuous-refactoring/references/housekeeping-template-file-format.md`), but it's not the only
way a line can be missing — a node fulfilled before this target's `bookkeeping.md` ever gained a
`## Housekeeping` section gets no second chance at a delivering MR to piggyback on, and the same is true
the very first time this Track ever runs for a target that already has a worked-through tree. Before
reading the checklist, reconcile: read `bookkeeping.md`'s `Fulfilled nodes`, and for each listed slug
whose own tree-doc names a `Housekeeping` field, append that line to `housekeeping-template.md` if it
isn't already there verbatim (creating the file fresh if this is the first line ever). Cheap and run
every cycle, not just once — `Fulfilled nodes` is itself a self-healing cache that can lag briefly, so
checking every cycle catches a slug this reconciliation missed on an earlier run rather than missing it
forever. Don't commit this edit yet — *Open this cycle's issue*, next, creates the branch it belongs on.

Then read `housekeeping-template.md`. Missing, or present but empty of contributed lines even after
reconciling → nothing has ever been registered to check yet. Report "due, but nothing registered to
check yet" and stop — don't open an empty issue. This still counts as this Track's own process having
run this pass (`skills/refactor-learn/references/housekeeping-write.md` writes `Last scan` regardless).

## Open this cycle's issue

File an issue titled `Housekeeping — <today's date>`, body = every line from `housekeeping-template.md`
as an unchecked checkbox, in the file's own order, plus the standing item from *Work the checklist*,
below, as one more checkbox (always present, not sourced from the template file).

Branch `chore/housekeeping-<today's date>` (existing → reuse, don't reset) — the reconciliation commit
above, if it changed anything, lands here as this cycle's first commit.

## Work the checklist

Standing item, every cycle, regardless of what the template file names: **check whether
`AGENTS.md`/`CLAUDE.md`, this repo's own skills, or its own house rules need updating** for anything the
other checklist items are about to touch (a dependency bump, a tooling version change). Adjust, or note
"no adjustment needed" directly on the issue — either way, check the box.

For every other item (each one a `Housekeeping` line some tooling-tree node contributed): do the work the
line names, update the issue body with the result (check the box; append a short report if the line
calls for one — output worth keeping, not a restated checkbox), then commit. Batch related items into
one commit each rather than one commit per checkbox if that reads more naturally.

**Judgement calls, not silent decisions:**
- A finding with no clean fix (an audit advisory with no available patched version, a breaking update
  that can't be made green within this cycle's own scope) → document it on the issue and ask the human
  rather than deciding unilaterally; never ship a broken result to look "done."
- Don't invent new skills, rules, or tooling-tree adoptions while doing housekeeping — this Track keeps
  what's already adopted current, it doesn't adopt anything new (that's the Safety Net/Guardrails Tracks'
  own job).

## Quality gate

Whatever this target repo's own full quality-check command is (composer/npm/etc. script, or the
equivalent CI job run locally) must pass before *Deliver*, below — same bar any other suite merge
request already holds itself to.

## Deliver

**Any code change made:** open the merge request per
`skills/continuous-refactoring/references/opening-a-merge-request.md` (same create-mode, basing, and
description rules every other suite MR already follows) — referencing this cycle's issue so it closes on
merge, per that document's own conventions. Do not close the issue directly.

**Zero code changes** (every item this cycle turned out to be already current) — no MR to gate a close
behind; close the issue directly, with a comment saying so, and stop.

## Completion criterion

Either the sweep wasn't due this pass (this file's process never ran, per *Is the Track due this pass?*
above), nothing was registered to check and that's reported, or this cycle's issue has every item
checked (with its report/decision recorded) and is either delivered via merge request or closed directly
(zero changes) — never left half-checked with the pass reported as finished. Whenever this file's own
process is reached at all this pass — whether it resumed a cycle, opened a fresh one, or found nothing
registered — `refactor-learn`'s closing call records that (`## Housekeeping`'s `Last scan`,
`skills/refactor-learn/references/housekeeping-write.md`).
