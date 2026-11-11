# 11 — A workable ticket keeps the rest of a tooling Track from being filed

Type: task
Status: open
Blocked by: —

**What the plays showed** (r8 B on 2026-11-08, r7 and r8 on 2026-11-11; named three times, so a ticket under Q54).
`worklist.md` asks for a Track's trace only when the Track has no workable ticket. While one is workable, no trace is
asked and no scan runs, so Stages nobody filed yet stay unfiled. A long-lived ticket makes this lasting: a rollout or
baseline ticket that stays open across many merge requests keeps the Guardrails Stages behind it (PHPMD, the coverage
floor, …) from ever being proposed, and nothing tells the human.

**To decide**

- Whether the trace is asked even beside a workable ticket, as it already is beside one in review, blocked or
  waiting; or only beside a long-lived one (rollout, baseline); or every so many runs.
- What the cost is: the trace's search per Stage on every run of that Track.
- Whether the Housekeeping re-check of the tooling Tracks already covers it well enough, and the report only has to
  say that Stages may be unfiled.

**Done when** the rule is decided, written in `worklist.md` (and `track-scan.md` where it moves), r8 B and r7 play it,
and tests and validator are green.
