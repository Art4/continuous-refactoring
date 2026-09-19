# 08: Scheduler — Safety Net blockade, Guardrails yield, Housekeeping insertion

Spec: `agent-judged-fulfilment`.

**What to build:** The orchestrator's Track selection implements the rules recorded in ticket 04. While the Safety Net Track's `Open` is non-empty, it is selected and nothing else runs, even if no node is currently workable; what it waits on is reported. Guardrails with at least one workable `Open` node is selected ahead of Investigation, and Housekeeping preempts it for one pass when due. Guardrails with `Open` non-empty but nothing workable is stalled: it yields, its `Open` stays as it is, and the pass report lists every stalled node with its reason. Investigation's structural-scan gate is "Safety Net section present and `Open` empty" plus recorded rejections. The one-time bootstrap exception keeps its three one-Track turns in order and does not wait for Guardrails' `Open`. At most one Track is selected per pass; the fixed tie-break order and the manual Track override are unchanged.

**Blocked by:** 04 (`Open` as the complete backlog), 06 (A Track scan fills `Open`; `refactor-learn` maintains it).

**Status:** ready-for-agent

- [ ] Safety Net `Open` non-empty: only Safety Net is selected, also when nothing is workable, and the wait is reported.
- [ ] Guardrails with a workable node is selected ahead of Investigation; a due Housekeeping runs for one pass and Guardrails resumes afterwards.
- [ ] Guardrails stalled (only stop-condition, PHP-floor or `needs-info`-flagged nodes left): the ordinary ratio and tie-break rules pick among the other Tracks, and the report lists each stalled node with its reason.
- [ ] `structural-scan` is proposable only when the Safety Net section exists and its `Open` is empty (a recorded rejection counts as resolved).
- [ ] The one-time exception still runs Investigation, then Guardrails, then Housekeeping, one Track per pass, without waiting for Guardrails' `Open`.
- [ ] Advisory agent fixtures cover: the Safety Net blockade with nothing workable, Guardrails stalled, Housekeeping preempting a Guardrails backlog, and the bootstrap sequence with a non-empty Guardrails `Open`.
