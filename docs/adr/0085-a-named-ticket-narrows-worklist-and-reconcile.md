# A named ticket narrows the worklist and reconcile to itself

> Amends [ADR-0074](0074-state-lives-in-the-tracker-found-by-search.md).


A call that names a ticket ("do ticket 68 yourself") answered Track choice and selection, but steps 2 and 3 of the run
had no shortcut for it: the worklist searched every Stage's open tickets and looked up each one's merge request, and
reconcile laid out findings for all of them and for every recorded rejection. A named ticket was not a restriction, so
nothing narrowed those steps. The run spent its first searches on tickets it would never work, and an autonomous run
could close or reject tickets the human had not mentioned.

## Decision

- **A named ticket is the worklist alone.** The worklist reads that ticket and gives it a Track and a state. A ticket it
  names as its blocker is read for the state, not added.
- **Reconcile follows the worklist.** Its findings are the named ticket's merge request and whether its Stage was
  dropped. Rejection reversals and every other ticket are left to a run whose call names no ticket.

## Considered Options

- **Narrow the worklist, keep reconcile whole.** Reconcile reads the worklist: every open ticket with its merge
  request. Keeping it whole needs the full worklist anyway, so almost nothing would be saved. Rejected.
- **Keep both whole and say so.** Keeps the tracker in agreement on every run, at the cost of the searches and of writes
  the call did not ask for. Rejected.

## Consequences

- A run for one ticket starts with one ticket's lookups instead of a search per Stage.
- Merge requests of other tickets merged or closed in the meantime stay unreconciled until a run without a named ticket;
  a ticket whose merge request was merged stays open that long.
- The named ticket's own Track has an open ticket, so no scan becomes due through the narrowing.
