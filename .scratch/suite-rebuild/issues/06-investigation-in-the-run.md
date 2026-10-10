# 06: Investigation in the run

**What to build:** When the run reaches the Investigation Track, open tickets there are the worklist:
structural candidates the suite filed and tickets a human wrote. With none open, the run explores the
code, shows everything it found in order of signal, and recommends filing the three strongest.

Spec: `../spec.md` (sections *Track choice*, *Tickets as the worklist*). Written new with the
`writing-for-agents` skill as a reference of the entry skill; the signals catalogue and the structural
candidate search are carried over as content.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] A ticket matching no tooling-tree node and not the Housekeeping ticket counts as Investigation
- [ ] A ticket a human wrote is found through the **Candidate** hint or by being named in the call; the
      reference states this limit in one sentence
- [ ] With open tickets, selection follows the signals, a **Priority** hint first
- [ ] With none, the run explores; all findings are shown, the three strongest are the recommendation for
      filing, an autonomous run files those three; nothing else is stored
- [ ] The project lines `Focus areas` and `Refactoring goal` shape the exploration and its order
- [ ] No cap and no "one candidate per run" rule appears
- [ ] No test is written or changed
