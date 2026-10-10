# Reference: Track choice

Names the Track this run works, or ends the run. Reads the worklist (`worklist.md`). The fixed order is
**Safety Net, Guardrails, Housekeeping, Investigation**.

## What a Track has to offer

| Track | It has something when |
| --- | --- |
| Safety Net, Guardrails | it has a workable ticket; or it has no open ticket at all, which makes its scan due |
| Housekeeping | its open ticket's stated due date is reached; or its mechanism is missing: no **Housekeeping** operation, no template, or no open ticket |
| Investigation | always — with open tickets it works them, without it explores |

A Track this run already **tried** — its scan left nothing to file, nothing was filed, or selection found
nothing workable — has nothing for the rest of the run.

## The recommendation

The first Track in the fixed order that has something.

**Safety Net comes first while it is unfinished.** When Safety Net has nothing, read whether it is
fulfilled from the parser (`tooling-tree-parser.md`, *Is Safety Net fulfilled?*); the answer is computed:

- **Fulfilled** → the recommendation moves on down the order.
- **Not fulfilled** → the recommendation is to end the run. An autonomous run ends here with "Safety Net is
  waiting for merges", followed by the tickets in review with their merge requests and the tickets that
  cannot be worked with their reasons. A human may choose another Track instead.

No Track has anything → the run ends: nothing is workable.

## The decision point

- **Findings:** per Track, how many tickets are workable, in review, blocked and waiting; whether a scan is
  due; for Housekeeping the due date or what is missing; for Safety Net, once it was read, whether it is fulfilled.
- **Options:** every Track, and ending the run.
- **Recommendation:** as above.

The call named a Track or a ticket → the choice is answered: say in one sentence which Track the run works,
and lay out nothing.

## Coming back here

Steps 5 and 7 return here when the chosen Track turned out to have nothing workable. Mark it as tried.

- **The call named the Track or the ticket** → the run ends: nothing is workable in what was asked for.
- **Otherwise** → decide again by the same rules: with Safety Net fulfilled the next Track in the order is
  recommended within this same run; with Safety Net unfinished the run ends as above.

Track choice is done when one Track is named or the run has ended.
