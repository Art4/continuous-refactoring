# 05: Investigation Track wired into the scheduler

**What to build:** The already-existing structural-scan candidate search (hot-spot discovery, deepening
work) gets its own `Cadence`/`Last scan` bookkeeping and participates in the Track scheduler as the
fourth option — always eligible, lowest tie-break priority, no fixed cadence interval. No new
fulfilment-check logic: Investigation was never dependency-name-driven to begin with.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] `bookkeeping.md` gains an `Investigation` section carrying `Cadence`/`Last scan` only — no
      `Open`/`Out-of-scope` lists; that state stays on the issue tracker / `merge-requests.md` as today.
- [ ] Investigation is always eligible (no "`Open` must be empty" precondition) and has no fixed cadence
      interval — it is the scheduler's fallback whenever nothing else outranks it.
- [ ] Existing structural-scan candidate-search behavior is otherwise unchanged.
