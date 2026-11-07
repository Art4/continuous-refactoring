# d11 — The human asks for changes on a mergeable merge request

Played as a walk-through.

Covers: `skills/continuous-refactoring/SKILL.md`, `skills/continuous-refactoring-run/SKILL.md`

## Situation

An onboarded project, settings `review only`, five rounds, in an environment with a timer. Round 1 opened merge
request !12 for ticket #5, the review found it mergeable, the Driver commented that, and it waited out the cadence.
During the wait the human posted a review on !12 that requests changes: "The new helper swallows the exception from
the database layer, so a failed save looks like a success to the caller. Please keep the failure visible." Ticket #6
is blocked by #5; nothing else is open. The wake-up has just arrived.

## Call

`/continuous-refactoring`, with the first round done and the wake-up just arrived.

## Expected

- [ ] Round 2 takes !12 first and names #5 in the call of its run.
- [ ] The run reworks !12 for the human's request, with its reasoning, and pushes to the same merge request.
- [ ] The review runs again on the reworked merge request, and the round ends mergeable, with the human, or in a
      further rework, counted as reworks of this round.
- [ ] The Driver does not pause with !12 still listed as waiting for the human's merge.
- [ ] It posts no answer to the human's request in the human's place.

## Results

2026-11-02, skill commit 9c02368: pass, every line, as a walk-through. It named one gap: whether a rework for the human counts
among the round's two. 057d1cb says it does.

2026-11-07, on 0e29b63, the first playing of every scenario with the runner and a separate judge: pass, every line, as a walk-through.
