---
name: continuous-refactoring
description: Run one pass of the continuous refactoring loop — pick the Track due this pass (Safety Net, Guardrails, Housekeeping, Investigation) and run it. Use to keep a codebase under continuous refactoring, on demand or via your own recurring trigger.
disable-model-invocation: true
---

# Continuous Refactoring

One **loop pass**: picks the **Track** (`CONTEXT.md`) this pass spends itself on and hands it to that Track's own skill, which does only the work due since the last pass and records what it learned so the next pass starts from state, not from zero.

This skill decides one thing — *which* Track — and nothing else. It never runs the pass itself: `refactor-loop` (via `continuous-safety-net`, `continuous-guardrails`, `continuous-investigation`) runs the generic pass — scan → prioritise → design → implement → learn — and `continuous-housekeeping` runs Housekeeping's own process. Git is the only hard requirement of a pass.

Run this on demand, or via your own recurring trigger — the loop has no schedule of its own.

## The pass

Two steps: select a Track, then dispatch to its skill.

0b. **Track selection.** Decide which **Track** (`CONTEXT.md`) this pass spends itself on — real competition between every currently-wired Track (today: **Safety Net**, **Guardrails**, **Housekeeping**, **Investigation**), replacing each Track's own earlier standalone "is my Track due?" check with one shared decision. Full algorithm — the one-time exception, `overdue_ratio` staleness comparison, the `Open`-non-empty eligibility rule, the fixed tie-break order, manual override — lives in `skills/continuous-refactoring/references/track-scheduler.md`; read it in full before implementing this step. **First, check the one-time exception**: if Safety Net's own `Open` is currently empty and Investigation/Guardrails/Housekeeping haven't each had their one dedicated turn yet (in that order) since it emptied, select whichever of the three is still owed, overriding everything below — see `track-scheduler.md`'s own "One-time exception" section for the exact, implicitly-tracked condition (no stored flag). **Otherwise**, compute `(today − Last scan) / Cadence` for every due, eligible wired Track and select the highest-ratio one; a tie, or no ratio to compare (two Tracks both never-run, or Investigation, which never carries a numeric `Cadence` at all), falls back to the fixed order Safety Net > Guardrails > Housekeeping > Investigation — which is what makes Investigation the scheduler's own permanent fallback: always due and always eligible, but always last in line. The human invoking this pass may instead name a specific Track directly (e.g. "run the Guardrails Track"), bypassing this whole computation, the one-time exception included — the named Track still respects the `Open`-non-empty rule in `track-scheduler.md`. Invoking a `continuous-<track>` skill directly is the same override.

0c. **Dispatch.** Invoke the selected Track's skill via the Skill tool, with no other input — each one names its own Track:

    | Selected Track | Skill |
    |---|---|
    | Safety Net | `/continuous-safety-net` |
    | Guardrails | `/continuous-guardrails` |
    | Housekeeping | `/continuous-housekeeping` |
    | Investigation | `/continuous-investigation` |

    Then stop: the invoked skill runs the entire pass, records what it learned, and gives the closing report — relay it unchanged. No wired Track is both due and eligible → nothing to dispatch; report that and end the pass (in practice unreachable now that Investigation is wired — see `track-scheduler.md`'s own Selection section).

## Completion criterion

A Track was selected (or named by the human) and its skill ran to completion, or no Track was due and that was reported. Track selection itself writes nothing.
