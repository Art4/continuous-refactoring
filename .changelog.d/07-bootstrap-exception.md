- The Track scheduler gains a one-time exception, checked first, before any `overdue_ratio`/tie-break
  computation: the pass right after Safety Net's own `Open` first empties runs **Investigation** once
  (one candidate, fully delivered), then the following pass runs **Guardrails** once (its own first
  scan-and-clear cycle), then the pass after that runs **Housekeeping** once (its own first cycle) —
  each overriding ordinary selection for exactly that one turn, so a target sees one real piece of
  delivered refactoring value before being asked to adopt more tooling or sit through maintenance.
  Ordinary staleness-ratio scheduling resumes permanently once Housekeeping's turn completes — including
  Safety Net's own later, rarer rescans. Tracked entirely from the existing Track sections'
  `Last scan`/`Open`/`Pending candidates` state — no new stored flag: each of Investigation's/Guardrails'/
  Housekeeping's own "have I ever run" section-presence, plus (for Investigation only, which carries no
  `Open` of its own) whether `Pending candidates` still names its in-flight candidate, is what makes the
  exception fire exactly once per repo (`skills/continuous-refactoring/references/track-scheduler.md`'s
  own "One-time exception" section).
