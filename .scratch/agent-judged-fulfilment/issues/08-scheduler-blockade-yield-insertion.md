# 08: Scheduler — Safety Net blockade, Guardrails yield, Housekeeping insertion

Spec: `agent-judged-fulfilment`.

**What to build:** The orchestrator's Track selection implements the rules recorded in ticket 04. While the Safety Net Track's `Open` is non-empty, it is selected and nothing else runs, even if no node is currently workable; what it waits on is reported. Guardrails with at least one workable `Open` node is selected ahead of Investigation, and Housekeeping preempts it for one pass when due. Guardrails with `Open` non-empty but nothing workable is stalled: it yields, its `Open` stays as it is, and the pass report lists every stalled node with its reason. Investigation's structural-scan gate is "Safety Net section present and `Open` empty" plus recorded rejections. The one-time bootstrap exception keeps its three one-Track turns in order and does not wait for Guardrails' `Open`. At most one Track is selected per pass; the fixed tie-break order and the manual Track override are unchanged.

**Blocked by:** 04 (`Open` as the complete backlog), 06 (A Track scan fills `Open`; `refactor-learn` maintains it).

**Status:** implemented — PR #110, open items listed in Comments

- [x] Safety Net `Open` non-empty: only Safety Net is selected, also when nothing is workable, and the wait is reported.
- [x] Guardrails with a workable node is selected ahead of Investigation; a due Housekeeping runs for one pass and Guardrails resumes afterwards.
- [ ] Guardrails stalled (only stop-condition, PHP-floor or `needs-info`-flagged nodes left): the ordinary ratio and tie-break rules pick among the other Tracks, and the report lists each stalled node with its reason.
- [x] `structural-scan` is proposable only when the Safety Net section exists and its `Open` is empty (a recorded rejection counts as resolved).
- [x] The one-time exception still runs Investigation, then Guardrails, then Housekeeping, one Track per pass, without waiting for Guardrails' `Open`.
- [x] Advisory agent fixtures cover: the Safety Net blockade with nothing workable, Guardrails stalled, Housekeeping preempting a Guardrails backlog, and the bootstrap sequence with a non-empty Guardrails `Open`.

## Comments

**PR:** [#110](https://github.com/Art4/continuous-refactoring/pull/110)

- Verified: `track-scheduler.md` (Safety Net blockade incl. nothing workable and "reports the wait",
  Eligibility/Selection for Guardrails workable vs yielding, Housekeeping preemption, Investigation
  waiting, "at most one Track", One-time exception without waiting on Guardrails' `Open`),
  `investigation-track.md` (Safety Net section present and `Open` empty, plus recorded rejections). The four
  fixtures exist under `fixtures/php` with `expected/behavior.md` and are wired in `run.sh` (scheduler
  tier): `php-scheduler-safety-net-blockade`, `php-scheduler-guardrails-stalled`,
  `php-scheduler-housekeeping-preempts-guardrails`, `php-scheduler-bootstrap-guardrails-open`. Not executed
  here (need opencode and model credentials).
- Item 3 not met: the "report lists each stalled node with its reason" half is only in the fixture's
  `behavior.md`. No skill text instructs it: `track-scheduler.md` and `continuous-refactoring/SKILL.md`
  step 0b never say how "workable" is decided at selection time (the definition lives in
  `track-open-processing.md`, not referenced from the scheduler) or that a yielded Guardrails Track's
  non-workable nodes go into the pass report; the Status line only covers nodes skipped during an `Open`
  walk that actually ran. The ratio/tie-break-among-the-others half is documented.
