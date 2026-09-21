---
name: continuous-housekeeping
description: Runs one Housekeeping Track cycle — reconcile, checklist, quality gate, deliver — then records its Last scan; aborts on a target that isn't onboarded. Internal — invoked by continuous-refactoring only, not a user entry point.
---

# Continuous Housekeeping

The **Housekeeping** Track (`CONTEXT.md`) as one loop pass. Unlike the other three Tracks, Housekeeping isn't a tooling-tree scan: its own reconcile → checklist-assembly → quality-gate → deliver process is a complete pipeline in itself, in `skills/continuous-housekeeping/references/housekeeping-track.md`. This skill runs it directly and never calls `refactor-loop` — the generic pass (scan → prioritise → design → implement) doesn't apply to it. Its own merge request (or, on a cycle with zero code changes, a direct issue close) is the pass's entire delivery.

Invoked by `continuous-refactoring` once its Track scheduler selects Housekeeping. Not a user entry point — a human who wants this Track runs `/continuous-refactoring housekeeping`. Housekeeping's *trigger* stays centrally scheduled; only its process lives here.

**Direct invocation is a full manual override.** However this skill is reached — by `continuous-refactoring`, by naming the Track, or typed directly — it runs the Housekeeping Track without consulting the scheduler, bypassing the Safety Net blockade and the one-time exception exactly as `skills/continuous-refactoring/references/track-scheduler.md`'s *Manual override* section describes for a named Track. This skill knows only its own Track and never reads another Track's state.

The Track's own reference files live beside this skill: `references/housekeeping-track.md` (the process), `references/housekeeping-cadence-interview.md` (the human-run cadence interview), `references/housekeeping-template-file-format.md` (the checklist file's format).

## Process

0. **Onboarded target.** The Refactoring Notes' `bookkeeping.md` must exist (`skills/continuous-refactoring/references/refactoring-bookkeeping.md` says where the Refactoring Notes live). Missing → abort now: nothing runs, not even step 2. Report "This repo isn't onboarded yet — the Refactoring Notes have no `bookkeeping.md`. Run `/continuous-refactoring` first; its onboarding step sets the repo up, then rerun." Never create the file here — this skill doesn't go through `refactor-loop`, so it makes this check itself.

1. **Housekeeping cycle.** Follow `skills/continuous-housekeeping/references/housekeeping-track.md` to completion — reconcile `housekeeping-template.md`, open this cycle's issue, work the checklist, run the quality gate, deliver. It resumes an in-progress cycle rather than opening a second one. Nothing registered to check yet → it reports that and stops; that still counts as this Track's process having run.
2. **Learn, closing call — always.** Run `/refactor-learn` with the Housekeeping Track's process having actually run this pass, whichever way it ended. Records `## Housekeeping`'s `Last scan` (`skills/refactor-learn/references/housekeeping-write.md`) via `refactor-learn`'s ordinary dedicated bookkeeping branch. `refactor-learn` writes it only when the process was actually reached.

## Fallback

The suite must keep working in a target repo with none of the global skills installed. `refactor-learn`'s own `## Fallback` covers step 2, and `housekeeping-track.md` names its own tool and forge fallbacks; this skill engages no global skill itself.

## Closing report

Wherever the pass ends, close with exactly two lines to the human:

- **Status:** one line, what happened this pass, e.g. "Status: housekeeping sweep delivered (MR #7); ...". Every claim reflects state freshly confirmed this pass; when it can't be confirmed (no forge/remote, CI status unreadable), say so explicitly rather than reporting an assumed outcome.
- **Next:** one line, what the human can or should do now.

## Completion criterion

One Housekeeping cycle's process ran per `housekeeping-track.md` and `refactor-learn`'s closing call recorded `## Housekeeping`'s `Last scan`, and the outcome is reported: a delivered merge request (or a direct issue close on a zero-change cycle), a cycle resumed, or "due, but nothing registered to check yet".
