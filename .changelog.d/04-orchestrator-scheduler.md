- Track scheduler: the orchestrator now runs real competition between every currently-wired **Track**
  (Safety Net, Guardrails) instead of each Track deciding on its own whether it's due — a new
  Track-selection step (`skills/continuous-refactoring/SKILL.md` step 0b,
  `skills/continuous-refactoring/references/track-scheduler.md`) computes each due, `Open`-empty Track's
  `overdue_ratio = (today − Last scan) / Cadence` and hands the highest-ratio one to `refactor-scan` as
  an explicit input; a tie (or two Tracks that have never run) falls back to the fixed order Safety Net
  > Guardrails > Housekeeping > Investigation. A Track with non-empty `Open` still always has its
  existing work worked instead of being rescanned, and a human can still name a Track directly to bypass
  selection entirely. Written generically over every Track carrying a bookkeeping section, so
  Housekeeping and Investigation slot into the same mechanism later without another rework. The
  suite-wide open-MR cap (`refactor-prioritize` step 1) was already Track-agnostic and needed no change.
