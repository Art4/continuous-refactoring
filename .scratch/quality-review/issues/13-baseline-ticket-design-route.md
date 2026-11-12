# 13 — Where the design point goes for a baseline ticket without a plan

Type: task
Status: open
Blocked by: —

**What the plays showed** (r7 and r8 on 2026-11-11, named by both, so a ticket under Q54). `design-point.md` step 1
has the row "is a baseline ticket → `planning-a-baseline-ticket.md` decides whether its newest plan still stands".
When there is no plan yet, or the newest one no longer stands, the row does not say where the run goes next:
straight into `planning-a-baseline-ticket.md` (skipping step 2, *Who plans*), or on to step 2, whose suite planning
then routes back to the same reference. That reference opens with "(`design-point.md`, steps 1 and 2)", which hints
at both. Nor is it said that steps 4 and 5 (the Openers and the plan's decision point) still follow. Both players
went 1 → 2 → 3 → 4 → 5, which is presumably meant; no wrong decision was forced.

**To decide**

- Whether a baseline ticket's new part goes through *Who plans* like any other ticket, or whether the suite always
  plans a part itself because the Tool file fixes how a part is cut.
- Where the route is stated: in the row of step 1, or in the opening of `planning-a-baseline-ticket.md`.

**Done when** the route reads one way in both files, the scenarios that cover them (r7, r8) pass, and tests and
validator are green.
