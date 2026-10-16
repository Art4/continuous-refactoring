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
