# Reference: Track choice

Names the Track this run works, or ends the run. Reads the worklist (`worklist.md`). The fixed order is
**Safety Net, Guardrails, Housekeeping, Investigation**.

Every decision point here is laid out as `../SKILL.md`, *Decision points*, says: the findings go into the
conversation as a message of their own, then the question — in an autonomous run, then the recommendation
taken.

## A base update first

A ticket that **needs base update** comes before every Track, whatever Track the call names: the run continues in
`updating-the-base.md` with the first one in that reference's order, and ends where it ends. Skipped there → the
choice below, with that ticket counted as in review.

## What a Track has to offer

| Track | It has something when |
| --- | --- |
| Safety Net, Guardrails | it has a workable ticket; or it has no trace yet, which makes its scan due (`worklist.md`, *A Track's trace*) |
| Housekeeping | an open ticket of it that is not in review states a due date that is reached; or its mechanism is missing: no **Housekeeping** operation, no template, or no open ticket |
| Investigation | always — with open tickets it works them, without it explores |

A Track this run already **tried** — its scan left nothing to file, nothing was filed, selection found
nothing workable, or Housekeeping had nothing to work — has nothing for the rest of the run.

## The recommendation

The first Track in the fixed order that has something.

**Safety Net comes first while it is unfinished.** When Safety Net has nothing, read whether it is
fulfilled from the parser (`tooling-parser.md`, *Is Safety Net fulfilled?*); the answer is computed:

- **Fulfilled** → the recommendation moves on down the order.
- **Not fulfilled, read from the seed from the trace, and a Stage of the Safety Net's `backlog` has no open
  ticket** → that Stage is not known: the Track has no trace after all, its scan is due, and Safety Net has
  something. The recommendation is Safety Net.
- **Not fulfilled** otherwise → the recommendation is to end the run. An autonomous run ends here with
  "Safety Net is unfinished", followed by the Safety Net's tickets alone: those in review with their merge
  requests, those blocked with what blocks them, those waiting with what they wait for. A human may choose
  another Track instead.

The answer read from this run's scan needs no such check: the scan judged every Stage, and a proposal declined
at filing is a rejection.

No Track has anything → the run ends: nothing is workable.

## The decision point

- **Findings:** per Track, how many tickets are workable, in review, blocked and waiting; whether a scan is
  due; for Housekeeping the due date or what is missing; for Safety Net, once it was read, whether it is fulfilled.
- **Options:** every Track, and ending the run.
- **Recommendation:** as above.

The call named a Track or a ticket → the choice is answered: say in one sentence which Track the run works,
and lay out nothing.

## Coming back here

Steps 5 and 7, the Investigation Track and the Housekeeping Track return here when the chosen Track
turned out to have nothing workable. Mark it as tried.

- **The call named the Track or the ticket** → the run ends: nothing is workable in what was asked for.
- **Otherwise** → decide again by the same rules: with Safety Net fulfilled the next Track in the order is
  recommended within this same run; with Safety Net unfinished the run ends as above.

Track choice is done when one Track is named or the run has ended.
