# Reference: the `continuous-housekeeping` cadence interview

Runs once, the first time `continuous-housekeeping` is triggered for a target repo with no `Housekeeping cadence` already recorded — mirrors `loop-config-interview.md`'s shape (`skills/continuous-refactoring/references/loop-config-interview.md`) at a much smaller scale: one question, not three.

## Ask

`❓ **Q1** - **How often should housekeeping run?**: A recurring sweep — dependency currency, tooling-deprecation fixes, documentation sync — checks whatever the adopted tooling has registered since the last one. Pick an interval.`

- **Weekly** — recommended default.
- **Monthly** — lighter touch, fewer interruptions; a real backlog (dependency drift, unreviewed audit findings) accumulates for longer between sweeps.
- **A different interval** — the human names one (e.g. "every two weeks", "daily").

Recommendation: **Weekly**. Nothing about this interview blocks on anything else — ask it standalone, a single `AskUserQuestion` call when available, the same numbered-prose shape otherwise (`skills/refactor-design/references/grilling-fallback.md`'s convention).

## Record

Write `**Housekeeping cadence:** <answer>` into the Refactoring Notes' `bookkeeping.md`, in the same place `refactoring-bookkeeping.md`'s own `## Structure` shows it. Free text is fine (`weekly`, `monthly`, `every 2 weeks`) — nothing parses this field with calendar arithmetic beyond "has at least this much time passed since the last sweep's issue was created," which tolerates prose.
