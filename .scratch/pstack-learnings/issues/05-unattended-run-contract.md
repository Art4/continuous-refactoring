# 05 — Unattended run: exit predicate, discard, decision trail

Type: task
Status: open

For scheduled/unattended runs: a checkable exit predicate stated up front and never relaxed, smallest justified change per iteration, discard what did not help, a decision trail one row per decision, stop and write up on a real dead end. Check how this fits the run's decision points and the final report.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

**Tooling-tree table, open question 3** (autonomous run with an unfinished Safety Net: end, or move on?): the exit-predicate contract answers it — a plateau pivots, only a real dead end stops, so the run continues while any node with met prerequisites remains and ends on an empty worklist. Build this before or together with the table.

## Comments

### 2026-10-16 — gap check against `skills/`: partial

Autonomous mode, the findings message as record and `reporting-progress.md` exist. A run is one chain ending in one merge request, so an iterating exit predicate fits poorly. What is missing is a stop rule for the loops that exist: `implement-point.md` step 4 (red check → fix → run again) and step 5 (finding → back to 3) have no bound, no dead-end write-up, no rule against relaxing the check. See also `.scratch/purpose-based-fulfilment-and-scheduled-tracks`.

### 2026-10-16 — grilled; decisions

One chain, one merge request stays (ADR 0073); no iterating exit predicate — the plan's `Done when` is the predicate and repeated calls make more merge requests. A **dead end** is not a count: the same red check or the same review finding survives a fix and a second attempt (implement steps 4 and 5). Outcome: branch local, no push or merge request; interactive run lays out a decision point (open question on the ticket recommended / the human takes the branch / end), autonomous takes the recommendation; the open question names the branch and says in plain words what was tried. New hard rule in the foundational rules: a check is never weakened without the human's allowance (pin and reader-load review included; the baseline ignore is a case of it). Unchanged: the stop at an unfinished Safety Net (decided with the tooling-tree table; the earlier note above that said "carry on" is withdrawn), the Housekeeping track, `design-point.md`; no new decision trail (findings messages and `Decisions` suffice); no ADR, no new glossary word. Built in PR "Dead end after two failed fixes".
