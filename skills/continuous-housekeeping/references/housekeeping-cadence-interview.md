# Reference: the Housekeeping Track's own cadence interview

Optional, human-initiated only — the Housekeeping Track's own `Cadence` field
(`../../continuous-refactoring/references/refactoring-bookkeeping.md`'s `## Housekeeping` section)
defaults to `7 days` silently on this Track's first-ever scheduler-driven run
(`housekeeping-track.md`'s own *First-run cadence* section) —
this interview never blocks that. Run it any time a human wants to reconsider the interval through a
guided question instead of hand-editing the number directly; mirrors `onboarding-setup-interview.md`'s shape
(`../../continuous-refactoring/references/onboarding-setup-interview.md`) at a much smaller scale: one
question, not three.

## Ask

`❓ **Q1** - **How often should housekeeping run?**: A recurring sweep — dependency currency, tooling-deprecation fixes, documentation sync — checks whatever the adopted tooling has registered since the last one. Pick an interval or a calendar day.`

- **7 days (weekly)** — recommended default, and what a fresh target already gets without asking.
- **1 month** — lighter touch, fewer interruptions; a real backlog (dependency drift, unreviewed audit findings) accumulates for longer between sweeps.
- **monthly on the 1st** — a fixed calendar day instead of an elapsed interval (any day 1–28 works).
- **A different value** — the human names a number with a unit (`12 hours`, `3 days`, `2 weeks`, `3 months`) or another `monthly on the <N>th`.

Recommendation: **7 days**. Nothing about this interview blocks on anything else — ask it standalone, a single `AskUserQuestion` call when available, the same numbered-prose shape otherwise (`../../refactor-design/references/grilling-fallback.md`'s convention).

## Record

Write `**Cadence:** <answer>` into the Refactoring Notes' `bookkeeping.md`'s `## Housekeeping` section
(creating the section, with `Last scan` left as whatever it already was, if it already exists — this
interview only ever touches `Cadence`), in the same place `refactoring-bookkeeping.md`'s own `## Structure`
shows it. A value in one of the forms `refactoring-bookkeeping.md`'s *Cadence values* defines (number with unit, or a monthly anchor), never free text — unlike the old standalone skill's own `Housekeeping cadence` field,
`## Housekeeping`'s `Cadence` participates in the Track scheduler's numeric `overdue_ratio` comparison
(`../../continuous-refactoring/references/track-scheduler.md`) the same way `## Safety Net`'s/
`## Guardrails`' own `Cadence` already does, so it has to be one of those forms, never prose. Write the unit even for the default (`7 days`, not `7`).
