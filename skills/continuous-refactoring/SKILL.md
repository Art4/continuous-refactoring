---
name: continuous-refactoring
description: Run one pass of the continuous refactoring loop — onboard a repo that has never run it (one short interview, then stop), otherwise pick the Track due this pass (Safety Net, Guardrails, Housekeeping, Investigation) and run it. Use to keep a codebase under continuous refactoring, on demand or via your own recurring trigger.
disable-model-invocation: true
---

# Continuous Refactoring

One **loop pass**: first **onboards** a target that has never run the loop (step 0 below — a short interview, then the invocation ends); otherwise picks the **Track** (`CONTEXT.md`) this pass spends itself on and hands it to that Track's own skill, which does only the work due since the last pass and records what it learned so the next pass starts from state, not from zero.

This skill decides one thing on an onboarded target — *which* Track — and nothing else. It never runs the pass itself: `refactor-loop` (via `continuous-safety-net`, `continuous-guardrails`, `continuous-investigation`) runs the generic pass — scan → prioritise → design → implement → learn — and `continuous-housekeeping` runs Housekeeping's own process. Git is the only hard requirement of a pass.

Run this on demand, or via your own recurring trigger — the loop has no schedule of its own.

## The pass

Step 0 onboards an un-onboarded target and ends the invocation; on an onboarded target, two steps follow: select a Track, then dispatch to its skill.

0. **Onboarding.** Resolve the Refactoring Notes (`references/refactoring-bookkeeping.md`, *Where the Refactoring Notes live*) and check for its `bookkeeping.md`. **Exists → nothing to onboard: go straight to step 1 and say nothing about onboarding.** **Missing → this invocation onboards, and nothing else** — every invocation, including one where the human named a Track (no Track runs without Refactoring Notes). First tell the human, in one sentence, that this repo hasn't been set up for the loop yet and onboarding is starting (e.g. "This repo has no Refactoring Notes yet — starting onboarding: a few questions, then I write the setup files."). Then run the interview in `references/onboarding-setup-interview.md` in full — **inline, never in a subagent** (it asks the human questions): explore, the one-time setup-gap question when the engineering-skills setup is incomplete, the questions one at a time, an informational summary, the writes (one status line each, `bookkeeping.md` last), the closing text. Then **stop**: no Track selection, no dispatch, no scan, no issue, no merge request, no forge action — the closing text tells the human to commit the new files and run `/continuous-refactoring` again, optionally naming a Track. This is the `onboarding-setup` node of the tooling tree being fulfilled before any Track exists to work it.

1. **Track selection.** Decide which **Track** (`CONTEXT.md`) this pass spends itself on — real competition between every currently-wired Track (today: **Safety Net**, **Guardrails**, **Housekeeping**, **Investigation**), replacing each Track's own earlier standalone "is my Track due?" check with one shared decision. Full algorithm — the one-time exception, `overdue_ratio` staleness comparison, the `Open`-non-empty eligibility rule, the fixed tie-break order, manual override — lives in `references/track-scheduler.md`; read it in full before implementing this step. **First, check the one-time exception**: if Safety Net's own `Open` is currently empty and Investigation/Guardrails/Housekeeping haven't each had their one dedicated turn yet (in that order) since it emptied, select whichever of the three is still owed, overriding everything below — see `track-scheduler.md`'s own "One-time exception" section for the exact, implicitly-tracked condition (no stored flag). **Otherwise**, compute `(today − Last scan) / Cadence` for every due, eligible wired Track and select the highest-ratio one; a tie, or no ratio to compare (two Tracks both never-run, or Investigation, which never carries a numeric `Cadence` at all), falls back to the fixed order Safety Net > Guardrails > Housekeeping > Investigation — which is what makes Investigation the scheduler's own permanent fallback: always due and always eligible, but always last in line. The human invoking this pass may instead name a specific Track directly (e.g. "run the Guardrails Track"), bypassing this whole computation, the one-time exception included — the named Track still respects the `Open`-non-empty rule in `track-scheduler.md`. Invoking a `continuous-<track>` skill directly is the same override.

2. **Dispatch.** First tell the human, in one sentence, which Track was selected and is being started now (e.g. "Selected the Guardrails Track — starting it."; say so too when they named it themselves). Then invoke the selected Track's skill via the Skill tool, with no other input — each one names its own Track:

    | Selected Track | Skill |
    |---|---|
    | Safety Net | `/continuous-safety-net` |
    | Guardrails | `/continuous-guardrails` |
    | Housekeeping | `/continuous-housekeeping` |
    | Investigation | `/continuous-investigation` |

    Then stop: the invoked skill runs the entire pass, records what it learned, and gives the closing report — relay it unchanged. No wired Track is both due and eligible → nothing to dispatch; report that and end the pass (in practice unreachable now that Investigation is wired — see `track-scheduler.md`'s own Selection section).

## Completion criterion

Either the target was un-onboarded and onboarding ran to its closing text (files written, nothing else touched), or a Track was selected (or named by the human) and its skill ran to completion, or no Track was due and that was reported. Track selection itself writes nothing.
