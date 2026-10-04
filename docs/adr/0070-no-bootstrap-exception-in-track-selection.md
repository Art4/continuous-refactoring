# Track selection is one cascade — the one-time bootstrap exception is removed

> Amends [ADR-0055](0055-purpose-based-fulfilment-and-scheduled-tracks.md) and
> [ADR-0056](0056-agent-judged-fulfilment.md): the one-time bootstrap exception (Investigation, then
> Guardrails, then Housekeeping, one forced turn each once Safety Net's `Open` first empties) is removed.
>
> Amends [ADR-0065](0065-investigation-gets-its-own-open.md): Investigation's `Open` no longer takes
> part in selecting the Track, and the "at most one `Open` non-empty at a time" argument is withdrawn.

The exception was meant to fire once per target. It didn't: its first condition — "`## Investigation`'s
`Open` names an issue → select Investigation" — carried no one-time guard and matched on every pass an
Investigation candidate was in flight, for the life of the repo. That made it the only rule resuming
in-flight Investigation work, and it let a candidate waiting on review take every pass ahead of a due
Housekeeping and a workable Guardrails backlog. The ordinary rules meanwhile said nothing about a
non-empty Investigation `Open` at all, and justified that with a claim the tree contradicts: Guardrails'
nodes are children of `php-safety-net`, not parents of `structural-scan`, so Guardrails' and
Investigation's `Open` can both be non-empty.

## Decision

The exception is removed. Selection is one ordered cascade, first match wins:

1. Safety Net's `Open` is non-empty → Safety Net (the blockade, unchanged).
2. Safety Net, Guardrails or Housekeeping is due with nothing in flight → highest `overdue_ratio`, ties
   by the fixed order Safety Net > Guardrails > Housekeeping > Investigation. Housekeeping preempting a
   Guardrails backlog for one pass is this step, no longer a separate rule; a due Safety Net rescan
   takes the pass the same way.
3. Guardrails' `Open` holds a workable node → Guardrails.
4. Otherwise Investigation. Its `Open` decides only whether that pass resumes or scans.

A fresh target therefore runs Guardrails' first scan, Housekeeping's first cycle, then Guardrails'
backlog; Investigation first runs once that backlog is done or stalled. Instead of forcing an early
Investigation turn, the Safety Net pass that ends with `Open` empty tells the human that the other
three Tracks can now be run at will by naming them — `continuous-safety-net` adds that line to its
closing report. It repeats after a later rescan that ends empty; nothing is stored to suppress it.

## Considered

- **Keep the exception, add a real one-time guard.** Rejected — needs a stored flag or a second
  mechanism for resuming Investigation's `Open`, to protect an ordering the human can get by naming a
  Track.
- **Move Investigation ahead of Guardrails in the fixed order.** Rejected — Investigation is always
  due, so it would starve Guardrails permanently rather than once.

## Consequences

The first structural refactoring arrives later on a target left to the scheduler; a human who wants it
earlier runs `/continuous-refactoring investigation`. An in-flight Investigation candidate no longer
outranks a due Track or a workable Guardrails node. `track-scheduler.md` loses the exception section
and the snapshot caveat that came with it; `CONTEXT.md`'s **Track** entry and the Track playbook follow.
Fixtures `php-scheduler-bootstrap-guardrails`, `-housekeeping`, `-resumes` and `-guardrails-open` are
deleted; `php-scheduler-bootstrap-investigation` becomes `php-scheduler-never-run-tie-break` and now
expects Guardrails.
