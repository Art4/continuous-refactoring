---
name: continuous-housekeeping
description: One Housekeeping run of the skill suite — works the open Housekeeping ticket, its recurring tasks and the refactoring ideas left on it as comments, and offers to set the mechanism up where it is missing. Made to be scheduled.
disable-model-invocation: true
---

# Continuous Housekeeping

One **run** that works the Housekeeping Track alone: no worklist, no Track choice, no other ticket.

The run is made of **decision points**, and it is **interactive** or **autonomous**. Both are defined in
`../continuous-refactoring/SKILL.md` — how the call states the mode in *The call*, the rules in *Decision
points* — and hold here as written; read those two sections before step 1.

## The call

Beside the mode, the call's free text may state any of these; say back in one sentence what was
understood.

| The call states | Effect |
| --- | --- |
| a **Housekeeping ticket** or a **template** | that ticket is the one worked, due or not |
| **now** ("although it is not due") | the next ticket is worked before its date |
| a **further template** ("a monthly one beside the weekly") | the run sets that template up |
| the **line for `AGENTS.md`** that a setup left out | the cycle proposes it |

Nothing stated → the run works the ticket that is due.

## The run

Read `../continuous-refactoring/references/reporting-progress.md` before the first sentence to the human.

1. **Ready.** Carry out step 1 of *The run* in `../continuous-refactoring/SKILL.md`; its `references/`
   folder is the one beside that file.
   *Done when* the target's `## Refactoring operations` section carries the three required operations,
   or the run has ended.

2. **Housekeeping.** Follow `references/housekeeping-track.md`.
   *Done when* that reference's last step is, or it has ended the run.

## The end of a run

Close as `../continuous-refactoring/SKILL.md`, *The end of a run*, says: the two lines **Status** and
**Next**. A run that found nothing due names the date from which the next ticket is due.
