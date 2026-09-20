- `continuous-refactoring` is now a thin dispatcher: it only selects a Track (`references/track-scheduler.md`,
  unchanged) and invokes that Track's own skill. The pass itself (scan → prioritise → design → implement →
  learn) moved into a new track-agnostic `refactor-loop` skill that requires a Track and aborts without one;
  `continuous-safety-net`, `continuous-guardrails` and `continuous-investigation` delegate to it, and
  `continuous-housekeeping` owns Housekeeping's own process with its three reference files. Only
  `continuous-refactoring` is a user entry point (`/continuous-refactoring`, with or without a Track name,
  behaves as before); the new skills are internal. See ADR-0057.
