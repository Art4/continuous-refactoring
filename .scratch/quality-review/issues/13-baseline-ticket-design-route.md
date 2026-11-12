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

## Comments

**2026-11-12 — Decided** (Q59–Q61). A baseline ticket with no plan that stands goes on to *Who plans*, then steps 3
to 5; `planning-a-baseline-ticket.md` names steps 1 and 3. Interactive, *Who plans* recommends the suite's own
planning for a baseline ticket, a target's skill found staying an option; a target's skill gets no rule for cutting
a part. Autonomous, the suite plans unless the call names a skill: probe p1 (both modes, 93k player, 47k judge,
pass) showed that a call naming the skill already works through `SKILL.md`'s rule that the call answers a choice,
so no row is added, and step 3's sentence on an autonomous run stays.
