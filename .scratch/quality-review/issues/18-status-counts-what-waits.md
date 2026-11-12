# 18 — What the Status line counts as waiting for the human

Type: task
Status: open
Blocked by: —

**What the plays showed** (r8 on 2026-11-11, r7 A on 2026-11-12; named twice, so a ticket under Q54). The run's
closing **Status** "opens with how many things wait for the human" (`continuous-refactoring-run/SKILL.md`). It is
not said whether a merge request in review that this run did not touch (#52 beside the run's own) counts, nor
whether a Housekeeping ticket that is not due does. r8 counted #52; r7 A was unsure.

**To decide**

- Whether "what waits" is what this run left for the human (its merge request, an open question it asked), or
  everything open that needs a human now (every merge request in review, every unanswered question), with the
  Driver's pause list as the model.
- How a not-due Housekeeping ticket counts: presumably not at all.

**Done when** the **Status** line says what it counts, `docs/playbooks/run.md` agrees, the scenarios whose expected
lines read the closing lines pass, and tests and validator are green.
