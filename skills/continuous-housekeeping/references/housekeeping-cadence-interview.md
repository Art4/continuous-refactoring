# Reference: the Housekeeping Track's own cadence interview

Optional, human-initiated only — the Housekeeping Track's own `Cadence` field
(`skills/continuous-refactoring/references/refactoring-bookkeeping.md`'s `## Housekeeping` section)
defaults to `7` (days) silently on this Track's first-ever scheduler-driven run
(`skills/continuous-housekeeping/references/housekeeping-track.md`'s own *First-run cadence* section) —
this interview never blocks that. Run it any time a human wants to reconsider the interval through a
guided question instead of hand-editing the number directly; mirrors `loop-config-interview.md`'s shape
(`skills/continuous-refactoring/references/loop-config-interview.md`) at a much smaller scale: one
question, not three.

## Ask

`❓ **Q1** - **How often should housekeeping run?**: A recurring sweep — dependency currency, tooling-deprecation fixes, documentation sync — checks whatever the adopted tooling has registered since the last one. Pick an interval, in days.`

- **7 (weekly)** — recommended default, and what a fresh target already gets without asking.
- **30 (monthly)** — lighter touch, fewer interruptions; a real backlog (dependency drift, unreviewed audit findings) accumulates for longer between sweeps.
- **A different number of days** — the human names one directly.

Recommendation: **7**. Nothing about this interview blocks on anything else — ask it standalone, a single `AskUserQuestion` call when available, the same numbered-prose shape otherwise (`skills/refactor-design/references/grilling-fallback.md`'s convention).

## Record

Write `**Cadence:** <answer>` into the Refactoring Notes' `bookkeeping.md`'s `## Housekeeping` section
(creating the section, with `Last scan` left as whatever it already was, if it already exists — this
interview only ever touches `Cadence`), in the same place `refactoring-bookkeeping.md`'s own `## Structure`
shows it. A day count, not free text — unlike the old standalone skill's own `Housekeeping cadence` field,
`## Housekeeping`'s `Cadence` participates in the Track scheduler's numeric `overdue_ratio` comparison
(`skills/continuous-refactoring/references/track-scheduler.md`) the same way `## Safety Net`'s/
`## Guardrails`' own `Cadence` already does, so it has to be a real number of days, never prose.
