# 05: Investigation Track wired into the scheduler

**What to build:** The already-existing structural-scan candidate search (hot-spot discovery, deepening
work) gets its own `Cadence`/`Last scan` bookkeeping and participates in the Track scheduler as the
fourth option — always eligible, lowest tie-break priority, no fixed cadence interval. No new
fulfilment-check logic: Investigation was never dependency-name-driven to begin with.

**Blocked by:** 04

**Status:** done

- [x] `bookkeeping.md` gains an `Investigation` section carrying `Cadence`/`Last scan` only — no
      `Open`/`Out-of-scope` lists; that state stays on the issue tracker / `merge-requests.md` as today.
- [x] Investigation is always eligible (no "`Open` must be empty" precondition) and has no fixed cadence
      interval — it is the scheduler's fallback whenever nothing else outranks it.
- [x] Existing structural-scan candidate-search behavior is otherwise unchanged.

## Comments

Implemented as PR [#95](https://github.com/Art4/continuous-refactoring/pull/95), stacked on
`tickets/04-orchestrator-scheduler` (#94, merged).

**What changed:**

- `skills/continuous-refactoring/references/refactoring-bookkeeping.md` — new `## Investigation`
  section doc (`Cadence`/`Last scan` only, `Cadence` always the literal `continuous`, never
  hand-edited), the `## Structure` example, the section-ordering note, and the `## Rules`/old-schema
  bullets all updated to include it alongside `## Safety Net`/`## Guardrails`.
- `skills/continuous-refactoring/references/track-scheduler.md` — "Which Tracks compete" now lists
  `## Investigation`; the "Due" bullet gained a third clause (`Cadence` with no day-count → always due,
  no ratio to compute); the "Selection" section now explains explicitly *why* this makes Investigation
  the scheduler's permanent fallback (last in the fixed tie-break order, but only reachable at all once
  every other wired Track fails to be both due and eligible) and notes the "no wired Track due+eligible"
  branch is now unreachable in practice.
- `skills/refactor-scan/references/investigation-track.md` (new) — mirrors
  `safety-net-track.md`/`guardrails-track.md`'s shape, but far shorter: no Fulfilment judgement (spec's
  own "Out of Scope" — Investigation was never dependency-name-driven), no `Open`. Gates
  `structural-scan`'s own proposal behind Track selection — this is the actual behavior change: before
  this ticket, `structural-scan` was proposed unconditionally every pass, the instant its resolved-edge
  parents cleared, with zero Track gate.
- `skills/refactor-learn/references/investigation-write.md` (new) — writes only `## Investigation`'s
  `Last scan`, whenever `investigation-track.md`'s own *Proposing* step actually ran this pass (whether
  or not `structural-scan` itself was proposable) — never on a pass that merely resumed an already-filed
  structural candidate via the ordinary `Pending candidates` field.
- `skills/refactor-scan/SKILL.md`, `skills/refactor-learn/SKILL.md`, `skills/continuous-refactoring/
  SKILL.md`, `CONTEXT.md`'s **Track** entry — pointers into the two new reference files, updated Track
  lists/counts, one clarified sentence about Investigation never carrying `Open` (so it can never be one
  of the Tracks in the "several `Open`s at once" tie-break scenario).
- New fixture `fixtures/php/php-scheduler-investigation-fallback` under the existing `scheduler` harness
  tier (`fixtures/harness/run.sh`, `fixtures/README.md`) — Safety Net and Guardrails both fully resolved
  (same deterministic node inventory as `php-clean`) but neither due (`overdue_ratio ≈ 0.2`/`≈0.15`);
  Investigation, with no numeric `Cadence`, is the only due-and-eligible Track. Confirms both halves of
  this ticket in one run: the scheduler picks Investigation as fallback, and `refactor-scan` (via
  `investigation-track.md`) actually proposes `structural-scan` once handed that Track.
- `.changelog.d/05-investigation-track.md`.

**Judgement calls:**

- **`Cadence: continuous` as the literal value**, rather than a large number or an omitted field. Ticket
  01/02/04's own bookkeeping shape always carries a real `Cadence`, and the spec's Implementation
  Decisions section names default cadences per Track including, verbatim, "Investigation continuous (no
  fixed interval — the lowest-priority fallback)" — the word already used in the design's own prose, not
  invented for this ticket.
- **How ticket 04's mechanism actually handles a Track with no numeric `Cadence`** — confirmed by reading
  `track-scheduler.md` directly rather than assuming: ticket 04 built "no ratio to compare numerically"
  handling only for a *never-run* Track (absent section). Investigation needed a second, distinct case
  added to the same "Due"/"Selection" logic — a Track whose section *exists* but whose `Cadence` simply
  has no day-count, permanently, not only before a first scan. Both cases now fall into the same
  tie-break bucket, and since Investigation sits last in the fixed order (`Safety Net > Guardrails >
  Housekeeping > Investigation`), it only ever wins when nothing else with a real ratio is due —
  confirmed live: the new fixture seeds Safety Net/Guardrails both genuinely not-due (ratios `<1`, not a
  tie), and the scheduler still correctly picked Investigation as the sole eligible Track, never framing
  it as "out-ranking" the other two.
- **No CONTEXT.md dedicated "Investigation" glossary entry added.** ADR-0055's own Decision text is
  explicit that Investigation "names the existing structural-scan/Deepening/Hot-spot search activity...
  rather than renaming any of those terms" — unlike Safety Net/Guardrails/Housekeeping, which were new
  terms each getting their own entry, Investigation deliberately reuses existing vocabulary (**Hot
  spot**, **Deepening**). Only the existing **Track** entry got a small clarifying clause about
  Investigation's own `Cadence`.
- **`structural-scan`'s own Fulfilment-check/gate mechanism is untouched** — confirmed by reading
  `tooling-tree/structural-scan.md` directly: its resolved-edge gate, MR scope, and its own role as a
  required parent of `secret-detection` are all unchanged. Only *when* it gets proposed to
  `refactor-prioritize` changed (gated behind Investigation Track selection); the actual candidate-search
  walk once it wins ranking (`refactor-prioritize`'s Select mode,
  `structural-candidate-search.md`) is completely untouched, per the ticket's own scope.

**Testing:** `python3 -m unittest discover -s scripts -p 'test_*.py'` (339 tests, green),
`python3 scripts/validate_skills.py .` (clean — only the same pre-existing size/duplication advisories
the base branch already carries). New fixture run live end-to-end on the first try via
`OPENCODE_TIMEOUT=280 fixtures/harness/run.sh scheduler php-scheduler-investigation-fallback --opencode`
(`opencode/muse-spark-1.2-contributor-free`): the transcript shows the model correctly computing Safety
Net's (`0.2`) and Guardrails' (`0.15`) ratios, correctly noting Investigation's `continuous` `Cadence`
has no ratio to compute, correctly selecting Investigation as the sole due-and-eligible Track, then
correctly walking `refactor-scan`'s preconditions/step 2/step 4 and proposing `structural-scan` by name
before stopping as instructed — both harness assertions passed.
