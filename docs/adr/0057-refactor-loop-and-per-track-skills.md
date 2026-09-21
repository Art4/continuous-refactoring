# `continuous-refactoring` splits into a thin dispatcher, a track-agnostic `refactor-loop`, and four per-Track skills

> Superseded in part by [ADR-0058](0058-onboarding-is-a-dispatcher-step.md): `continuous-refactoring/SKILL.md` no longer does Track selection and dispatch only — it also onboards a target with no `bookkeeping.md` as step 0 before selecting a Track.
>
> Amends [ADR-0055](0055-purpose-based-fulfilment-and-scheduled-tracks.md): "The scheduler lives in
> `continuous-refactoring/SKILL.md`, at the start of a pass; `refactor-scan` becomes Track-aware" stays
> true for the scheduler itself, but the pass pipeline (scan → learn → prioritize → design → implement
> → learn) it dispatched into no longer lives inline in the same file — see Decision below. Housekeeping's
> trigger stays centrally scheduled exactly as ADR-0055 decided; only its *process* regains a dedicated
> skill identity, echoing
> [ADR-0037](0037-continuous-housekeeping-skill-and-node-housekeeping-contributions.md)'s retired
> standalone `continuous-housekeeping` skill for its mechanism, not its triggering.

Raised during a `/grill-with-docs` session: `continuous-refactoring/SKILL.md` had grown to carry both
the Track-selection algorithm (step 0b) and the entire generic pass pipeline (steps 1–6), plus a
Housekeeping-only special case (step 0c) that skips steps 1–5 entirely whenever Housekeeping wins
selection. Track-conditional branching had started leaking into a file whose only job should be
deciding *which* Track runs, not running one.

## Considered Options

- **Parking the pass pipeline under `refactor-scan`'s or `refactor-learn`'s own `references/`.**
  Rejected — the pipeline orchestrates all five lifecycle skills (scan, prioritize, design, implement,
  learn) equally; nesting it under any single one of them would suggest a false ownership (why would
  `refactor-design`'s caller live inside `refactor-scan`'s own folder?).
- **Inlining the three thin Track skills (Safety Net, Guardrails, Investigation) directly into
  `continuous-refactoring`'s own dispatch step**, since they'd otherwise carry almost no content beyond
  naming their Track. Rejected — it would put Track names back inside the dispatcher, exactly the
  leakage this split exists to remove, and forgoes symmetry with `continuous-housekeeping` (which does
  need its own skill) and any future Track that might need its own pre/post logic.
- **A hard technical gate preventing direct invocation of the four Track skills**, via
  `disable-model-invocation: true`. Rejected after verification (Claude Code's own docs plus a
  reproduced GitHub issue): the flag doesn't distinguish "the model decided on its own" from "another
  skill's own prose said to invoke this by name" — a gated skill invoked via the Skill tool from
  anywhere but the literal first user-typed command in a turn is refused outright, which would break
  `continuous-refactoring`'s own dispatch into these skills. Only `continuous-refactoring` itself keeps
  the flag.

## Decision

### `refactor-loop`, a new track-agnostic skill, replaces `continuous-refactoring/SKILL.md`'s inline steps 1–6

Houses the pass pipeline (scan → learn-early → prioritize → design → implement → learn-closing) plus
its supporting sections (Opening a merge request, Fallback, Closing report, Completion criterion),
carried over unchanged in substance. Takes a mandatory Track input and does no Track-name branching of
its own — the branching that already lived in `refactor-scan`'s and `refactor-learn`'s own per-Track
reference files (`safety-net-track.md`, `guardrails-track.md`, `investigation-track.md`,
`safety-net-write.md`, `guardrails-write.md`, `investigation-write.md`) is untouched and stays there.
Fails closed — aborts with a clear error — when invoked without a valid Track, rather than guessing
one.

### Four new per-Track skills: `continuous-safety-net`, `continuous-guardrails`, `continuous-investigation`, `continuous-housekeeping`

The first three each name their own Track and delegate unconditionally to `refactor-loop`; none reads
any other Track's state, matching the suite's existing no-cross-Track-knowledge discipline.
`continuous-housekeeping` keeps Housekeeping's own already-distinct process (never the generic
pipeline, unchanged since ADR-0037) and receives its three reference files
(`housekeeping-track.md`, `housekeeping-cadence-interview.md`, `housekeeping-template-file-format.md`),
moved out of `continuous-refactoring/references/` into its own. None of the four carries
`disable-model-invocation`.

### `continuous-refactoring/SKILL.md` shrinks to Track selection and dispatch only

`track-scheduler.md`'s algorithm is unchanged and stays under `continuous-refactoring/references/`,
alongside six other files that were never Track-selection material to begin with and predate the
Track concept: `loop-config-interview.md`, `refactoring-bookkeeping.md`, `opening-a-merge-request.md`,
`local-issue-tracker-template.md`, `forge-facing-writing.md`, `foundational-refactoring-rules.md`.
`continuous-refactoring` remains the only skill in this set carrying `disable-model-invocation: true`
and the only one documented in README as a user entry point.

### Direct invocation of a Track skill is a full manual override, same as naming a Track today

`/continuous-safety-net` (or any of its three siblings), invoked directly, behaves identically to
`/continuous-refactoring safety-net` — bypasses the Safety Net blockade and the one-time bootstrap
exception, exactly as `track-scheduler.md`'s existing Manual override section already specifies for a
named Track. No hard technical barrier stops this (see Considered Options); the boundary is
documentation only — narrow, explicitly-internal `description:` fields, and omission from README's
skill table.

## Consequences

Every live citation of `continuous-refactoring/SKILL.md` steps 1, 2, 5, or 6 across the suite
(`refactor-learn/SKILL.md`, `refactor-design/references/decision-gate.md`,
`refactor-scan/references/track-open-processing.md`, `README.md`, `fixtures/README.md`, and the
`php-scheduler-*`/`php-track-open-hand-adopted` fixtures) needs repointing to `refactor-loop`;
citations of steps 0b/0c stay put. Historical ADRs (0050, 0051, 0053) and archived `.scratch/` tickets
are left exactly as written, per this repo's own convention of treating them as an immutable record
amended by new ADRs, never rewritten. `CONTEXT.md` is untouched — the Track vocabulary itself doesn't
change, only its implementation's file organization.
