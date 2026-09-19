# 08: One-time exception can hand the pass to Housekeeping while Guardrails still has open work

**What to build:** Make the one-time bootstrap exception (`skills/continuous-refactoring/references/
track-scheduler.md`'s "One-time exception" section) wait for Guardrails' own turn to actually finish
before Housekeeping's turn (condition 3) can fire, the same way condition 1 already waits for
Investigation's in-flight `Pending candidates` to clear. Today it doesn't, and the file's own text
claims it does.

**Why:** Found while analysing a simulated Safety Net loop run. The exception is evaluated **before**
Eligibility/Selection, and its precondition reads only Safety Net's `Open`. Condition 2's justification
(the file's own text under condition 2) says that once Guardrails' first scan fills `## Guardrails`'
`Open`, "the ordinary Eligibility rule below … already keeps Guardrails selected on its own, every
subsequent pass, for as long as it takes to clear." That can't happen, because the ordinary Eligibility
rule is never reached while the exception still matches:

1. Guardrails' first scan (turn 2) writes `## Guardrails` with a **non-empty** `Open`.
2. Next pass: precondition holds (Safety Net `Open` empty). Condition 1 doesn't match (Investigation
   done). Condition 2 doesn't match (`## Guardrails` now exists).
3. **Condition 3 matches** (`## Housekeeping` still absent) → Housekeeping is selected, overriding
   Eligibility, while Guardrails' entries are still in flight (propose → design → implement → learn).

Guardrails' `Open` is then only worked again once Housekeeping's turn has produced its section. This
contradicts the spec's "Guardrails (one scan-and-clear cycle)" and `CONTEXT.md`'s **Track** entry ("one
turn each in that order").

The same shape may exist for a non-empty `Pending candidates` after turn 1 has already handed over, and
for the more general question of what "Guardrails' turn is finished" means when the section exists but
`Open` isn't empty. Decide it deliberately rather than by accident.

Not covered by any fixture today: `php-scheduler-bootstrap-housekeeping` seeds `## Guardrails` with
`Open: none` only, and `php-scheduler-bootstrap-guardrails` stops after Guardrails' scan without a
following pass.

**Blocked by:** none — touches `track-scheduler.md` (and the matching sentences in
`skills/continuous-refactoring/SKILL.md` step 0b and `CONTEXT.md`'s **Track** entry, if the wording
changes), plus one new fixture.

**Status:** needs-triage

- [ ] Condition 3 doesn't select Housekeeping while `## Guardrails`' `Open` is non-empty; Guardrails'
      own entries keep being worked until `Open` is empty.
- [ ] The explanation under condition 2 in `track-scheduler.md` is corrected to match the real
      evaluation order (exception first, Eligibility second).
- [ ] A new `php-scheduler-bootstrap-*` fixture seeds the missing case — Safety Net `Open` empty,
      `## Investigation` present with `Pending candidates: none`, `## Guardrails` present with a
      **non-empty** `Open`, no `## Housekeeping` — and its `expected/behavior.md` requires Guardrails
      (not Housekeeping) to be selected.
- [ ] Everything else the exception already guarantees still holds: fires exactly once per repo, no new
      stored flag, at most one Track per pass (`php-scheduler-bootstrap-*` fixtures unchanged).
