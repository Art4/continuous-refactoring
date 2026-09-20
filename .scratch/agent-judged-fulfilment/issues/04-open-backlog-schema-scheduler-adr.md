# 04: `Open` as the complete backlog — schema, scheduler rules, ADR

Spec: `agent-judged-fulfilment`.

**What to build:** Record the new model in the documentation and the decision log, so every later ticket implements against one written definition. A node-based Track's `Open` becomes its complete, ordered backlog: every node of the Track's scope that is neither fulfilled nor out-of-scope, blocked ones included, in the script's order, hand-reorderable, carrying an issue number only while the node is being worked. `Open` empty means the Track is done. The scheduler rules follow from that: the Safety Net Track blocks every other Track while its `Open` is non-empty; Guardrails is selected ahead of Investigation while it has a workable node, yields when nothing is workable, and Housekeeping can preempt it for one pass when due; Investigation's structural-scan gate reads "Safety Net section present and `Open` empty". `Fulfilled nodes` is retired from the schema and ignored where it still exists. This ticket documents the target; the skills adopt it in tickets 06 to 09.

**Blocked by:** None (can start immediately).

**Status:** done — PR #106

- [x] The bookkeeping schema documentation describes `Open` (complete, ordered, hand-reorderable, issue number only while worked) and `Out-of-scope` (unchanged), marks `Fulfilled nodes` as retired and ignored, and states that existing files are not migrated (a section written under the old meaning is worked like any other `Open`, and corrected by the scan that runs once it is empty; naming a Track never forces a scan while its `Open` has entries).
- [x] The scheduler documentation states the Safety Net blockade (also when no node is currently workable, the wait is reported), Guardrails' workable-versus-stalled behavior, Housekeeping's one-pass preemption when due, Investigation waiting behind a Guardrails backlog with workable nodes, and that at most one Track is selected per pass.
- [x] The one-time bootstrap exception's documentation is corrected: it does not wait for Guardrails' `Open`, and the claim that ordinary eligibility keeps Guardrails selected after its first scan is removed.
- [x] Investigation's gate is documented as the Safety Net section being present with `Open` empty, plus the existing rule that a recorded rejection counts as resolved.
- [x] A new ADR records the decisions, states which earlier decisions it replaces (the parser with detection shipping under the scan) or amends (pre-filing for Track nodes; `Open` and `Fulfilled nodes` in the purpose-based fulfilment decision), and briefly lists the alternatives considered and rejected.
- [x] The domain glossary is updated: the **Track** entry (blockade and yielding), the **Proposals** entry (no pre-filing for Track nodes), the **Fulfilment check** entry (agent-judged for every node), and a new entry for the recognition-only gate node.
- [x] The repo's documentation validation passes.

## Comments

**PR:** [#106](https://github.com/Art4/continuous-refactoring/pull/106)

- Verified against `refactoring-bookkeeping.md` (Fields table, `## Safety Net`/`## Guardrails`
  sections, `## Fulfilled nodes` marked retired), `track-scheduler.md` (Safety Net blockade, Eligibility,
  Selection incl. Housekeeping preemption and "at most one Track", One-time exception, Manual override),
  `investigation-track.md` (gate), `docs/adr/0056-agent-judged-fulfilment.md` and `CONTEXT.md` (Track,
  Proposals, Fulfilment check, Recognition-only gate node). `validate_skills.py` passes.
- Two imprecisions found, both left for ticket 11 / a follow-up rather than reopening this ticket:
  - ADR-0056 says it replaces "the earlier, unnumbered decision" that shipped the parser with detection; that
    decision is numbered, ADR-0014 (`0014-tooling-tree-parser-ships-under-refactor-scan.md`), which
    carries no "replaced by" note (see ticket 11).
  - The `CONTEXT.md` **Recognition-only gate node** entry uses `structural-scan` as its example, but
    `structural-scan` is proposed as a candidate by the Investigation Track, which contradicts the entry's
    own "never proposed" definition. `is-php-project` or the three gate nodes from ticket 01 fit.
