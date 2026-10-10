# 01: Vocabulary and decisions

**What to build:** A reader of the glossary and the ADRs finds the rebuilt suite described: a run as a chain
of decision points with an interactive and an autonomous mode, state kept in the tracker instead of a
bookkeeping document, one skill with references that prefers the target's own skills, and the standing
Housekeeping ticket. Every later ticket writes with these words.

Spec: `../spec.md` (sections *Solution*, *Vocabulary*, and the decisions each ADR records).

**Blocked by:** None (can start immediately)

**Status:** done

- [x] `CONTEXT.md` defines **Run**, **Decision point**, **Interactive / Autonomous**, **Worklist**,
      **Housekeeping ticket**, **Housekeeping template**
- [x] `CONTEXT.md` no longer defines Loop pass, Ticket-create-mode, MR-create-mode, Refactoring Notes,
      Bookkeeping document, Bookkeeping pointer, Local/Remote bookkeeping, Config file; entries that
      mention them or the cadence (Track, Onboarding, Refactoring operations, Housekeeping, Candidate,
      Fulfilled at pick-up, Flagged candidate) read true against the spec
- [x] One ADR each for: the run as decision points with two modes and no caps; state in the tracker,
      found by search, instead of bookkeeping; one skill with references and the target's own skills
      first; the standing Housekeeping ticket and its template
- [x] Each ADR names the earlier ADRs it supersedes, and those are marked superseded
- [x] No test is written or changed

## Comments

Done on `suite-rebuild`: ADR-0073 (the run), ADR-0074 (state in the tracker), ADR-0075 (one skill, the
target's own skills first), ADR-0076 (the standing Housekeeping ticket).

- **Red afterwards, for ticket 09:** `python3 scripts/validate_skills.py .` and with it
  `test_validate_skills.EndToEndTests.test_real_repo_passes` — the glossary is ahead of the skill texts
  (old skills still say "bookkeeping", "loop pass", "ask-each-time", "human-opens", "filed date",
  "checklist file"; the new terms are not used by any skill yet). The other 238 unit tests are green.
  The changelog-fragment check will be red too; the fragment is ticket 08's.
- **Beyond the ticket's list, changed because they named removed things:** **Backlog** (now the parser's
  ordered node list, set apart from **Worklist**), **Ticket**, **Tooling tree**, the three edge entries,
  **Choice**, **Recognition-only gate node**, **Plan**, **Proposals**, **Signal**, **Findings**,
  **Decision trail**. Paths into the removed skills are replaced by plain names (the tooling-tree doc,
  the signals reference), so the glossary stays true when ticket 08 moves the files.
- **Not decided by the spec, kept as it was:** the label mechanics of a **Flagged candidate**
  (`needs-info` / `ready-for-agent`, self-confirmation). Ticket 05 writes the design point and may change
  them.
