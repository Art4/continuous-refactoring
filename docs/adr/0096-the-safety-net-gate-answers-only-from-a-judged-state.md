# The Safety Net gate answers only from a judged state

> Amends [ADR-0079](0079-tooling-model-roles-tools-stages-in-packs.md): an autonomous run with the Safety Net open
> still ends, but only once its open tickets account for every Stage left, and its report names the Safety Net's
> tickets alone.

An autonomous run ended with "Safety Net is waiting for merges" on a target whose Safety Net was met; a scan with a
judged seed then found it fulfilled with an empty backlog. The rule for the question was right — read it from this
run's scan or from the seed from the trace — but three things made the wrong answer easy. The parser's seedless
call, made in every run before Track choice, carried `safety_net_fulfilled: false` and a full backlog, because
without a seed every Stage is undecided. The seed from the trace needs the Packs and Stages that apply judged this
run, and outside a scan no step asked for that; unjudged, a Stage out of scope stayed undecided. And the stop took
any false answer as final, listing merge requests of every Track.

## Decision

- **No seed, no verdict.** The parser called without a seed returns the tooling tree's structure — Stages, their
  order, Tools, Roles, Packs — and nothing about fulfilment: no `safety_net_fulfilled`, no backlog, nothing
  workable or withheld. Selection orders by `nodes`.
- **What applies is judged once, in the worklist.** Before the trace check, the worklist judges each Pack's
  *Applies when*, the Stages' own *Applies when* in both tooling Tracks, and the runtime. The trace, its seed, the
  scan and the pick-up check take that result. A run that names a ticket skips it; a run without a worklist judges
  where it did before.
- **The stop checks itself.** An answer "not fulfilled" from the seed from the trace ends the run only when every
  Stage of the Safety Net backlog has an open ticket. A Stage without one is not known: the Track has no trace and
  its scan is due. An answer from this run's scan needs no check.
- **The stop names what it waits for.** "Safety Net is unfinished", followed by the Safety Net's tickets in review
  with their merge requests, blocked with the reason, waiting with the reason.

## Considered Options

- **Sharpen the prose only.** Rejected: the prose already said which call answers, and the seedless verdict still
  won.
- **Judge what applies in Track choice, right before the question.** Rejected: the trace check in the worklist
  needs the same judging earlier.
- **Keep "waiting for merges", limited to the Safety Net.** Rejected: once only blocked or waiting tickets are
  left, there is no merge to wait for.

## Consequences

- A step that wants a verdict has to hand in a seed; a seedless verdict can no longer be read by mistake.
- A run judges *Applies when* once even when it ends up working Investigation; the Housekeeping re-check still
  judges on its own.
- On a target whose Safety Net was in place from the start, nothing changes: no Stage of it is known, so its scan
  is due in every run, as before.
