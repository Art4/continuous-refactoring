# 04: Orchestrator Track scheduler — staleness ratio and fixed tie-break order

**What to build:** Real competition between Tracks. Given Safety Net and Guardrails both carry real
`Cadence`/`Last scan` data (from tickets 01/02) at different staleness levels, the orchestrator selects
the correctly most-overdue eligible Track instead of ticket 01's temporary "just run Safety Net" rule.

**Blocked by:** 01, 02

**Status:** ready-for-agent

- [ ] The orchestrator computes `(today − Last scan) / Cadence` for each due, eligible Track and selects
      the highest.
- [ ] Safety Net/Guardrails are only eligible when their own `Open` is empty; a Track with non-empty
      `Open` has its existing items worked (propose → design → implement → learn) instead of being
      rescanned.
- [ ] Ties, and which Track's open work gets design/implement effort when several hold `Open`
      simultaneously, both fall back to the fixed order Safety Net > Guardrails > Housekeeping >
      Investigation.
- [ ] A manual override (naming a specific Track directly) bypasses selection but still respects the
      "Open non-empty → work it, don't rescan" rule.
- [ ] The suite-wide open-MR cap applies once, across all Tracks combined, not duplicated per Track.
