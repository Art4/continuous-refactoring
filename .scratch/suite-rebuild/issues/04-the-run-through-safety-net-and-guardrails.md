# 04: The run, through Safety Net and Guardrails

**What to build:** A developer calls `/continuous-refactoring` and is led through one run as a chain of
decision points — reconcile, Track choice, scan, file tickets, select — each with findings, options and
one recommendation. With the autonomous hint the suite takes its own recommendations. The call's free
text can name a Track, a restriction, a ticket or the mode. For the two tooling Tracks the run reaches a
selected, workable ticket and hands it to the design point.

Spec: `../spec.md` (sections *The run*, *Track choice*, *Tickets as the worklist*, *Rejections*, and
*Shape of the suite*). The entry skill and its references are written new with the `writing-for-agents`
skill. Scan and selection are references of this skill, not skills.

Design and implement are named here as hand-over points; ticket 05 writes them. Investigation's own
scan is ticket 06. The Housekeeping Track is the reference `housekeeping-track.md` of
`continuous-housekeeping`, written by ticket 07; this ticket points to it by that name.

**Blocked by:** 01, 02, 03

**Status:** ready-for-agent

- [ ] The entry skill checks for the `## Refactoring operations` section first and goes to onboarding when
      it or **Search** is missing
- [ ] Interactive is the default; the autonomous mode is taken from the call's free text or from the human
      saying so mid-run; one chain serves both
- [ ] Without the hint and with nobody answering, the run ends at the first decision point with a report
      and has written nothing
- [ ] Reconcile: merged and closed merge requests of the suite are found by search and laid out with what
      follows (close the ticket, record a rejection, ask); a rejection whose blocker is now met is offered
      for reversal
- [ ] Track choice: open tickets are searched and assigned to Tracks through the parser's per-Track node
      list; the recommendation follows the fixed order; an autonomous run stops at an unfinished Safety Net
      with nothing workable, a human may choose otherwise; later Tracks are tried within the same run once
      Safety Net is fulfilled
- [ ] Scan runs only when the Track has no tickets, all are done, or it was asked for; it hands the node
      state to the parser and offers a ticket for every node neither fulfilled nor rejected, blocked ones
      marked through **Blocked by** or a sentence in the ticket
- [ ] A ticket names its subject in plain words; before filing, existing tickets on the subject, open or
      closed, are searched and shown
- [ ] Selection follows the tree's order, a **Priority** hint first; the node's fulfilment check runs again
      before the hand-over, and a fulfilled node's ticket is closed with a note
- [ ] Declining a node records a rejection where **Rejected** says, or proposes a place; dependents are a
      decision point following the kind of edge
- [ ] No cap on open merge requests or open candidates appears anywhere
- [ ] Nothing reads or writes a bookkeeping document, a config file or a cadence
- [ ] Text to the human says "skill suite" and "run"
- [ ] No test is written or changed
