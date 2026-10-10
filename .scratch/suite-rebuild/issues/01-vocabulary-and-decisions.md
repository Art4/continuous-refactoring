# 01: Vocabulary and decisions

**What to build:** A reader of the glossary and the ADRs finds the rebuilt suite described: a run as a chain
of decision points with an interactive and an autonomous mode, state kept in the tracker instead of a
bookkeeping document, one skill with references that prefers the target's own skills, and the standing
Housekeeping ticket. Every later ticket writes with these words.

Spec: `../spec.md` (sections *Solution*, *Vocabulary*, and the decisions each ADR records).

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `CONTEXT.md` defines **Run**, **Decision point**, **Interactive / Autonomous**, **Worklist**,
      **Housekeeping ticket**, **Housekeeping template**
- [ ] `CONTEXT.md` no longer defines Loop pass, Ticket-create-mode, MR-create-mode, Refactoring Notes,
      Bookkeeping document, Bookkeeping pointer, Local/Remote bookkeeping, Config file; entries that
      mention them or the cadence (Track, Onboarding, Refactoring operations, Housekeeping, Candidate,
      Fulfilled at pick-up, Flagged candidate) read true against the spec
- [ ] One ADR each for: the run as decision points with two modes and no caps; state in the tracker,
      found by search, instead of bookkeeping; one skill with references and the target's own skills
      first; the standing Housekeeping ticket and its template
- [ ] Each ADR names the earlier ADRs it supersedes, and those are marked superseded
- [ ] No test is written or changed
