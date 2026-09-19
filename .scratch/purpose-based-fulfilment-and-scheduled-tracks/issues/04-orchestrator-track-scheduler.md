# 04: Orchestrator Track scheduler — staleness ratio and fixed tie-break order

**What to build:** Real competition between Tracks. Given Safety Net and Guardrails both carry real
`Cadence`/`Last scan` data (from tickets 01/02) at different staleness levels, the orchestrator selects
the correctly most-overdue eligible Track instead of ticket 01's temporary "just run Safety Net" rule.

**Blocked by:** 01, 02

**Status:** done

- [x] The orchestrator computes `(today − Last scan) / Cadence` for each due, eligible Track and selects
      the highest.
- [x] Safety Net/Guardrails are only eligible when their own `Open` is empty; a Track with non-empty
      `Open` has its existing items worked (propose → design → implement → learn) instead of being
      rescanned.
- [x] Ties, and which Track's open work gets design/implement effort when several hold `Open`
      simultaneously, both fall back to the fixed order Safety Net > Guardrails > Housekeeping >
      Investigation.
- [x] A manual override (naming a specific Track directly) bypasses selection but still respects the
      "Open non-empty → work it, don't rescan" rule.
- [x] The suite-wide open-MR cap applies once, across all Tracks combined, not duplicated per Track.

## Comments

Implemented in PR [#94](https://github.com/Art4/continuous-refactoring/pull/94), branch
`tickets/04-orchestrator-scheduler`, stacked on `tickets/03-tier3-roadmap-local-only`.

**What was built:** a new `skills/continuous-refactoring/references/track-scheduler.md` (algorithm) plus
a new step 0b in `skills/continuous-refactoring/SKILL.md` (the orchestrator's own Track-selection step),
written generically over "every Track carrying a `Cadence`/`Last scan` bookkeeping section" rather than
hardcoding Safety Net/Guardrails by name — the fixed tie-break order already names all four Tracks, so
Housekeeping/Investigation slot in later (tickets 05/06) without another algorithm change.
`safety-net-track.md`/`guardrails-track.md`'s own "Is the Track due this pass?" sections now point at
this shared step instead of independently re-deriving due-ness, while their `Open`-non-empty
precondition and each Track's own `Cadence`/`Last scan`/`Open`/`Out-of-scope` bookkeeping shape are
unchanged, as required.

**Judgement calls:**

- **Housekeeping's existing standalone opt-in trigger (`bookkeeping.md`'s `Housekeeping cadence` field,
  step 0) is left untouched**, not folded into the new scheduler. The spec's Implementation Decision
  describes the *end state* after all of tickets 04/05/06 land (one step replacing the old step-0
  special case); folding Housekeeping in for real means giving it its own `## Housekeeping`
  `Cadence`/`Last scan` bookkeeping section and wiring its due-check into `track-scheduler.md`'s "which
  Tracks compete" set — explicitly ticket 06's own scope, not this ticket's. Since Housekeeping and
  Investigation currently have no bookkeeping section at all, they structurally never enter this
  ticket's ratio comparison — the mechanism is generic and ready for them, but nothing Housekeeping- or
  Investigation-specific was written, per the ticket's own instruction not to build that yet. Step 0's
  standalone trigger keeps working exactly as before in the meantime — no regression, just not yet
  unified.
- **"Which Track am I told to run" hand-off to `refactor-scan`**: the orchestrator's step 0b computes
  the winner and hands it to `refactor-scan` as an explicit input (prose-level, matching how this
  portable-markdown suite already hands data between steps — no code-level API). `refactor-scan/SKILL.md`
  step 2 and step 4's Safety-Net/Guardrails bullets, and both Track reference files' own "Is the Track
  due this pass?" sections, were reworded so `refactor-scan` reacts to the decision instead of
  re-deriving it — `refactor-scan` no longer reads `bookkeeping.md`'s Cadence/Last scan for itself at
  all.
- **Suite-wide open-MR cap**: verified already correct, no code change. `refactor-prioritize/SKILL.md`
  step 1 counts every open `refactor:candidate` issue with a linked pull request regardless of which
  Track (or no Track) filed it — it was never per-Track to begin with, since Safety Net/Guardrails Track
  candidates are filed and labeled exactly like any other candidate.
- **"Several Tracks hold `Open` simultaneously" (checklist item 3's own scenario)** is structurally
  impossible today with only Safety Net/Guardrails wired: a Guardrails node is never unblocked until
  Safety Net itself is fully resolved, so Safety Net's `Open` can't be non-empty at the same moment
  Guardrails' is (`guardrails-track.md`'s own Scope section — noted explicitly in `track-scheduler.md`
  too). The fixed-order fallback is documented and correct for when Housekeeping/Investigation, which
  carry no such gating relationship, join — just not exercisable by a fixture yet with the current two
  Tracks.

**Testing:** `python3 -m unittest discover -s scripts -p 'test_*.py'` (339 tests, green),
`python3 scripts/validate_skills.py .` (clean — only pre-existing size/duplication advisories). New
fixture `fixtures/php/php-scheduler-staleness-selection` (spec Testing Decision #2, "Track selection
under simple staleness") under a new `scheduler` harness tier — deterministic sanity-checked against
`tooling_tree.py` first, then run live end-to-end via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh
scheduler php-scheduler-staleness-selection --opencode` (`opencode/muse-spark-1.2-contributor-free`):
the model correctly computed both Tracks' `overdue_ratio`, selected Guardrails over Safety Net on
staleness grounds alone (2.5 vs. ~1.05, despite Safety Net's fixed-order priority), and proposed the
correct Guardrails node set. Manual override and the tie-break-order rule are documented but not
separately live-fixture-tested (time budget) — the "Open blocks rescan" eligibility precondition is
unchanged code, still covered by tickets 01/02's own existing fixtures.
