# Reference: selecting a ticket

Picks the one ticket of a tooling Track this run works, and makes sure its Stage still needs the work.
Reads the worklist (`worklist.md`), the parser's seedless call for the tree's order, and a call whose seed holds
the Packs and the runtime judged this run (`worklist.md`, *5. Judge what applies*) for what the runtime blocks
(`tooling-parser.md`).

Decision points here are laid out as `../SKILL.md`, *Decision points*, says.

## 1. Order the workable tickets

Take the Track's workable tickets, within the call's restriction.

1. Tickets carrying the **Priority** mark come first, where the target has that operation.
2. Then the tree's order: the position of each ticket's Stage in the Track's `nodes`. A baseline ticket
   stands at its level's position.

The call named a ticket → that ticket is the only one in the list, whatever its state, and step 3 is laid
out only where step 2 found something to write. One in review is handed on with its merge request and the
review's comments.

## 2. Pick-up check

Starting with the first ticket, judge its Stage's Fulfilment check again (`track-scan.md`, *Judging a
Stage*), together with its Pack's and its own *Applies when* — as the worklist judged them this run
(`worklist.md`, *5. Judge what applies*), judged here where it did not — and which Tool fills the Role of its Tool. For
a baseline ticket the check is the baseline: with no entries left the ticket is fulfilled, otherwise it is
the one to work.

| The check finds | The ticket |
| --- | --- |
| the Stage fulfilled — typically set up by hand since the ticket was filed | **fulfilled at pick-up**: to be closed with a note saying what serves the Stage now; go to the next ticket |
| its Pack's or its own *Applies when* no longer holding, or another Tool filling its Tool's Role | not workable now, named with the reason (the ticket's Stage no longer applies, or Psalm now fills Static Analysis); go to the next ticket |
| the Stage in `runtime_blocked` of that call | not workable: a rejection with the runtime version as blocker is proposed (`rejection.md`, *Below the runtime floor*); go to the next ticket |
| the Stage unfulfilled and free | the one to work |

Step 2 is done at the first ticket that is the one to work, or when the list is used up.

## 3. The decision point

- **Findings:** the tickets fulfilled at pick-up, each with what serves its Stage; the tickets that are not
  workable, with their reasons; the remaining workable tickets in order.
- **Options:** close the fulfilled ones with their note and work the first remaining ticket (the
  recommendation); work another of the remaining ones; decline a ticket's Stage, its Tool or its Role, which records a rejection
  (`rejection.md`); end the run.
- A ticket the human chooses that step 2 has not checked gets its pick-up check before the hand-over.

Close each fulfilled ticket per **Done** with its note — no merge request belongs to it — and report each.

## 4. Hand over

- **A ticket to work** → assign it per **Claim**, where the target has that operation, and hand it to the
  design point with: the ticket, its Stage's slug and its Tool's `details` file, the Track, the run's mode and the
  call's restriction.
- **None** — every ticket was closed, declined or not workable → say so with the reasons and return to
  Track choice with the Track marked as tried.

Selection is done when one ticket whose Stage is unfulfilled is handed over, or the Track is marked as
tried.
