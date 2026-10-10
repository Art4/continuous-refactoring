# 07: Housekeeping

**What to build:** A developer calls `/continuous-housekeeping` and the suite works the open Housekeeping
ticket: the recurring tasks from the template, the refactoring ideas left as comments, the secret scan
over new history — and, as the last task, creates the next ticket. Where the mechanism is missing, the
run offers to set it up, after which the call works without further explanation.

Spec: `../spec.md` (section *Housekeeping*, user stories 34–44). Written new with the
`writing-for-agents` skill. The process lives in the reference `housekeeping-track.md` of
`continuous-housekeeping`; the entry skill of ticket 04 points to it by that name when its Track choice
lands on Housekeeping.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] `continuous-housekeeping` is user-invocable, runs the Housekeeping Track without a Track choice, and
      follows the same interactive and autonomous modes as the run
- [ ] The open Housekeeping ticket and the template are found through the **Housekeeping** operation; the
      Track is due when the ticket's stated date is reached
- [ ] Mechanism missing → the run proposes the template (rhythm chosen by the human, with a recommendation
      drawn from the target), the first ticket, and the `AGENTS.md` line; the `AGENTS.md` line is written
      only after a human agreed, in an autonomous run too
- [ ] The template holds the recurring tasks, the rhythm, and the last item "create the next Housekeeping
      ticket"; the next ticket states from when it is due; several templates may exist side by side
- [ ] Each comment proposing a refactoring is carried out in one or more commits of its own; one too big
      is proposed for a ticket of its own
- [ ] The `AGENTS.md` line tells agents to propose ideas as a comment on the open Housekeeping ticket
      after the human allowed it, and, with two open, to let the human choose with the younger recommended
- [ ] The secret scan over history is a template task: whole history the first time, afterwards the
      commits since the last Housekeeping ticket
- [ ] Tooling-tree nodes still contribute their Housekeeping line to the template through their own merge
      request, and a fulfilled node whose line is missing gets it added
- [ ] The target's quality checks pass before the merge request opens; a cycle without changes closes its
      ticket with a comment
- [ ] No cadence, `Last scan` or bookkeeping is read or written
- [ ] No test is written or changed
