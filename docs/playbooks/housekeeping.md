# Playbook: The Housekeeping Track

The playbook for humans. `skills/continuous-housekeeping/references/housekeeping-track.md` covers the
step-by-step; this document explains how you steer it as a person — cadence, reading a sweep, and what
a housekeeping mention on an ordinary refactoring merge request means.

## What it is, and why it's a Track of its own

A periodic maintenance sweep — dependency currency, tooling-deprecation fixes, documentation sync — on
its own cadence, one of the four **Tracks** (Safety Net, Guardrails, Housekeeping, Investigation) that
`/continuous-refactoring` chooses between on each pass ([Track playbook](tracks.md)). Unlike the other
three, it isn't part of the ordinary scan → prioritise → design → implement → learn pipeline: that
pipeline ranks and delivers one candidate at a time, but Housekeeping works through a standing checklist
instead, on a calendar interval rather than competing for priority against a proposal. It has its own
skill (`continuous-housekeeping`) with its own process: reconcile the checklist, open one issue for the
cycle, work it, run the quality gate, deliver.

## Cadence

Nothing to opt into — a fresh target already gets weekly Housekeeping (`Cadence: 7` days) the first time
the Track scheduler selects it, the same silent default `Safety Net`'s 90 days and `Guardrails`' 60 days
already use. Read or change the interval directly in the Refactoring Notes' `bookkeeping.md`'s
`## Housekeeping` section — hand-edit `Cadence` any time, or ask for a guided one-question prompt instead
of a bare number by running the Housekeeping Track's own cadence interview.

## When its first cycle runs

Once Safety Net's open items are all done, a target gets one dedicated turn each for Investigation, then
Guardrails, then Housekeeping before ordinary cadence-based scheduling takes over — so Housekeeping's
first cycle can arrive earlier than its 7-day interval alone would suggest. After that, it's scheduled by
cadence like any other Track.

## Invoking it manually

Name the Track directly when invoking `/continuous-refactoring` (e.g. "run the Housekeeping Track") to
force a cycle on demand, bypassing the scheduler's own staleness comparison — the same pattern that
works for Safety Net, Guardrails, and Investigation.

## Reading a sweep

Each due cycle is one issue, titled `Housekeeping — <date>`, its checklist assembled from whatever's
accumulated in the Refactoring Notes' `housekeeping-template.md` plus one standing item (an
AGENTS.md/skills/rules sync check, every cycle, tied to no single tool). Review it like any other merge
request: CI green, the reported findings actually addressed or explicitly escalated back to you — not
silently decided — for anything without a clean fix.

## Housekeeping mentions on ordinary merge requests

An unrelated tooling-adoption merge request (say, adopting `composer-audit` for the first time) may also
mention that it registered a housekeeping check — that's the node's own `Housekeeping` field reaching
`housekeeping-template.md`, described in the merge request's own plain-facts section. Nothing to review
differently there; it's a factual note about what else that merge request touched, not a second decision
to make. It's picked up automatically the next time the Housekeeping Track runs — no separate opt-in step.

## Common mistakes

- **Expecting a stored "last run" date to require manual bookkeeping.** `## Housekeeping`'s `Last scan`
  is written by the loop itself, every time the Track's own process runs (even when it finds nothing to
  do) — the same discipline every other Track's own `Last scan` already follows; nothing here for you to
  maintain by hand beyond `Cadence` itself.
- **Treating a housekeeping finding with no clean fix as something to force through.** Document it on the
  issue and let the human decide — same bar the rest of this suite already holds itself to.
