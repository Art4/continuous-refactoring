# 07: One-time bootstrap exception — Investigation, then Guardrails, then Housekeeping

**What to build:** The pass right after the Safety Net Track's `Open` first transitions from non-empty
to empty runs Investigation once (one candidate, fully delivered), then the following pass runs
Guardrails once (its own first scan-and-clear cycle), then the pass after that runs Housekeeping once
(its own first cycle) — each overriding the ordinary staleness-ratio/tie-break selection for exactly that
one turn, so a target sees one real piece of delivered refactoring value before being asked to adopt more
tooling or sit through maintenance. Ordinary scheduling (ticket 04) resumes permanently for that repo
once Housekeeping's first turn completes.

**Blocked by:** 05, 06

**Status:** ready-for-agent

- [ ] The pass immediately following Safety Net's `Open` transitioning from non-empty to empty, for the
      first time, selects Investigation — overriding the ordinary staleness-ratio/tie-break order.
- [ ] The following pass selects Guardrails, not Investigation again.
- [ ] The pass after that selects Housekeeping.
- [ ] Once Housekeeping's first cycle completes, ordinary staleness-ratio scheduling governs every
      subsequent pass permanently for that repo — including Safety Net's own later, rarer rescans.
- [ ] The exception fires exactly once per repo, tracked implicitly from the Track sections' own
      `Last scan`/`Open` state — no new stored flag.
