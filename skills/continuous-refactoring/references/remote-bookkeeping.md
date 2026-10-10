# Reference: remote bookkeeping — the bookkeeping kept outside the working tree

Where `refactoring-bookkeeping.md`'s Bookkeeping pointer is anything other than the path of a local `bookkeeping.md`, the
bookkeeping lives there — a tracker issue, a wiki page, whatever the target chose — and the local files are a
working copy. It is what lets the state be picked up from another machine without anything being committed.
Every skill still works on the same local files it always did; **fetch** and **store** (below) are the only
difference.

Where the bookkeeping lives, what the pointer's value means, and how fetching and storing are done there belong
to the target. Read the pointer and interpret it with what the target's own files say — normally the
**Bookkeeping** bullet under `## Refactoring operations` in `docs/agents/issue-tracker.md`
(`refactoring-operations.md`).

## The working copy

The Refactoring Notes are `.scratch/refactor/`, always, with remote bookkeeping: `bookkeeping.md`,
`out-of-scope/` and `merge-requests.md` there are what every skill, and the parser, read and write. None of it
is authoritative and the suite never commits it. The config file (`config.md`) is not part of the working copy —
it stays exactly as it is.

## Fetch the bookkeeping

Before a pass reads any state, its entry point fetches: `refactor-loop`, `continuous-housekeeping`, the
dispatcher's Track selection, and a lifecycle skill invoked on its own.

Fetching replaces the working copy with what the remote holds, so nothing stale survives. It can't be fetched —
the place is gone or out of reach, or nothing in the target says what the pointer means → **stop**: "the
bookkeeping can't be fetched: <reason>". Nothing runs and nothing is created in its place.

A working copy with changes that were never stored (a pass was cut short) is stored first when the changes are
the suite's own; otherwise ask.

## Store the bookkeeping

Every skill that wrote the working copy stores before it returns: `refactor-learn`, and `refactor-design` for
its `## Investigation` `Open` write. **The last write wins**: the suite doesn't fetch and merge, so a human edit
made while a pass runs is overwritten.

Report it as one line (`reporting-progress.md`): the bookkeeping was stored. Text that lands where people read
it follows `forge-facing-writing.md`.

`Ticket-create-mode` doesn't apply: the bookkeeping is not a ticket, and the loop never creates its place.

## Only onboarding creates the place

With a human present, the onboarding interview (`onboarding-setup-interview.md`) creates the place the
bookkeeping lives in — when the target's description says how — or records one that already exists. No other
skill, in any circumstance, creates a replacement.
