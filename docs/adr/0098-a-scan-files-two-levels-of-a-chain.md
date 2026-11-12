# A scan files two levels of a chain

> Amends [ADR-0073](0073-a-run-is-a-chain-of-decision-points.md): "no caps" holds, except that a scan files a chain of
> blocked Stages only two levels deep.

A scan turned every Stage of the backlog into a proposal. On a target with PHPStan Level 6 in review it filed Levels
7 to 10 at once, each blocked behind the one before, and the PHPMD rollout before PHPMD itself; one play filed eleven
tickets in a run. A tracker full of tickets that cannot start for months reads as noise, and the human has to wade
through them to find the one that can.

## Decision

- **Levels.** A Stage with no unfulfilled blocker is on level 1; every other is one level deeper than its deepest
  blocker. Blockers are its `requires`, its `waits_for` that are not decided, and a required Role that is not filled;
  an any-of group and a Role count through their nearest Stage that could still be fulfilled. Levels are counted
  across both tooling Tracks and over the whole tracker: an open ticket's Stage keeps its own level, whoever filed it.
- **The horizon is two levels.** A scan proposes a Stage only on level 1 or 2. A deeper one is **beyond the horizon**:
  no ticket yet, and its line in the scan report says what it is behind.
- **The parser computes it.** It returns `beyond_horizon` per Track, `{node, level, behind}`, from the seed it is
  handed; the run does not count levels by hand.
- **The trace accounts for it.** A Stage beyond the horizon that has no ticket does not make a scan due. Once what
  blocks it is fulfilled, it moves within the horizon, the trace finds it not known, and the next scan files it.
- **A call that names it files it,** with each Stage between it and the horizon that has no ticket.
- **The number is fixed**, not a setting, for the reason ADR-0073 gave against caps as settings.

## Considered Options

- **Keep filing the whole chain** (ADR-0073 as it was). Rejected: the noise is the problem; "file some" at the
  decision point leaves the trimming to the human every time, and an autonomous run never trims.
- **Only the next member of each chain.** Rejected: the tracker would no longer show what comes after, and the scan
  would be due after every merge.
- **A maximum number of blocked tickets per Track.** Rejected: which tickets fill it would depend on the order, and
  parallel chains (PHPStan, PHPMD, Rector) would crowd one another out.
- **Two levels as a default the target's tracker file can change.** Deferred: the tracker file could hold it, but
  nobody has asked for another number yet.

## Consequences

- A Track is not fulfilled while Stages lie beyond its horizon; they stay in its backlog.
- A rollout Stage is titled as its Tool file names its ticket, also when it is filed before its adoption, which the
  horizon still allows (level 2).
- The scan report gains a line, *Later*, beside *Available on request*.
