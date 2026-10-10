# A run is a chain of decision points, with an interactive and an autonomous mode and no caps

> Supersedes [ADR-0063](0063-loop-creates-tickets-and-ticket-create-mode.md),
> [ADR-0059](0059-cadence-carries-a-unit.md),
> [ADR-0070](0070-no-bootstrap-exception-in-track-selection.md), and
> [ADR-0067](0067-tooling-tree-default-never-tilts-against-an-issue-backed-candidate.md) (a ranking that
> no longer exists): there is no `Ticket-create-mode`, no
> `MR-create-mode`, no `Cadence` and no scheduler cascade. How much the suite does without asking is said
> per call, and the Track is a decision point with a recommendation in a fixed order.
>
> Supersedes in part [ADR-0006](0006-loop-delivers-remembered-merge-requests.md) (the limit of two open
> merge requests), [ADR-0039](0039-batch-filing-and-priority-backlog-admission.md) (the backlog cap and
> its two admission tiers), [ADR-0024](0024-loop-config-interview-decides-tracker-create-mode-storage.md)
> and [ADR-0025](0025-agents-md-gets-a-create-mode-pointer-not-the-value.md) (the create-mode question and
> its pointer line), and [ADR-0055](0055-purpose-based-fulfilment-and-scheduled-tracks.md) with
> [ADR-0056](0056-agent-judged-fulfilment.md) (scheduling by cadence, the blockade, yielding and
> preemption rules, one Track per pass). Agent-judged fulfilment, the four Tracks and their fixed order
> stand.

How much of a pass happened without asking was fixed per machine: two settings in a config file, answered
once in the onboarding interview. A developer could not say "show me what you would do next" on one call
and "do it yourself" on the next. The suite also braked on its own — at two open merge requests and at
five open candidates it stopped proposing work, whatever the developer wanted — and chose its Track by a
staleness ratio over stored cadences that nobody could predict without reading the state.

## Decision

One **run** is a chain of **decision points**: reconcile → Track choice → scan (only when the Track needs
one) → file tickets → select → design → implement → merge request. At each one the suite lays out what it
found, the options, and one recommendation.

- **Interactive** is the default: the human decides at every point.
- **Autonomous** is said in the call, in free words, or mid-run ("carry on yourself from here"): the suite
  takes its own recommendation at every point. It is the same chain, so there is one path to maintain.
- The mode is never stored. Without the autonomous hint and with nobody answering, the run ends at the
  first decision point with a report and has written nothing.
- One write needs a human even in an autonomous run: changing the target's `AGENTS.md`.

The call takes free text the suite interprets: a Track, a restriction ("only the Rector nodes"), a ticket,
the mode.

A run ends when the merge request is open, when the design cannot proceed without a human answer, or when
nothing is workable. More work is another call, not a longer run.

**Track choice** is a decision point. The recommendation follows a fixed order — Safety Net, Guardrails,
Housekeeping, Investigation — and names the first Track with something workable. While Safety Net is not
fulfilled, an autonomous run that finds nothing workable there ends with "Safety Net is waiting for
merges"; a human may choose another Track. Once Safety Net is fulfilled, a Track with nothing workable is
skipped within the same run.

**No caps.** The limits on open merge requests and on open candidates are removed. How much runs in
parallel is the developer's decision. The one place a number remains is a recommendation, not a limit: an
Investigation run with no open tickets shows everything it found and recommends filing the three strongest.

## Considered

- **Keep the stored modes and add a per-call override.** Rejected — two sources for the same answer, and
  the stored one is the one a developer forgets.
- **A separate autonomous path.** Rejected — two flows drift apart; taking the recommendation at each
  point of the one chain cannot.
- **Keep the caps as defaults a developer can raise.** Rejected — a setting needs a place to live, and the
  suite keeps none ([ADR-0074](0074-state-lives-in-the-tracker-found-by-search.md)).
- **Keep cadences for Track choice.** Rejected — they need a stored `Last scan` per Track. A fixed order
  over what is workable right now is predictable from the tracker alone.

## Consequences

`CONTEXT.md` gains **Run**, **Decision point** and **Interactive / Autonomous**; **Loop pass**,
**Ticket-create-mode** and **MR-create-mode** leave it. Text addressed to the human says "skill suite" and
"run". Repeated calls on Safety Net end at "every workable node has a ticket and an open merge request" —
the next step is the developer's: review and merge. Parallel merge requests may conflict; resolving that
is the developer's too.
