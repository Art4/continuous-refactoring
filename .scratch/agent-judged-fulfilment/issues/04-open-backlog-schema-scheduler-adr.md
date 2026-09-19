# 04: `Open` as the complete backlog — schema, scheduler rules, ADR

Spec: `agent-judged-fulfilment`.

**What to build:** Record the new model in the documentation and the decision log, so every later ticket implements against one written definition. A node-based Track's `Open` becomes its complete, ordered backlog: every node of the Track's scope that is neither fulfilled nor out-of-scope, blocked ones included, in the script's order, hand-reorderable, carrying an issue number only while the node is being worked. `Open` empty means the Track is done. The scheduler rules follow from that: the Safety Net Track blocks every other Track while its `Open` is non-empty; Guardrails is selected ahead of Investigation while it has a workable node, yields when nothing is workable, and Housekeeping can preempt it for one pass when due; Investigation's structural-scan gate reads "Safety Net section present and `Open` empty". `Fulfilled nodes` is retired from the schema and ignored where it still exists. This ticket documents the target; the skills adopt it in tickets 06 to 09.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] The bookkeeping schema documentation describes `Open` (complete, ordered, hand-reorderable, issue number only while worked) and `Out-of-scope` (unchanged), marks `Fulfilled nodes` as retired and ignored, and states that existing files are not migrated (a section written under the old meaning is corrected by the Track's next scan, or an immediate scan via the Track override).
- [ ] The scheduler documentation states the Safety Net blockade (also when no node is currently workable, the wait is reported), Guardrails' workable-versus-stalled behavior, Housekeeping's one-pass preemption when due, Investigation waiting behind a Guardrails backlog with workable nodes, and that at most one Track is selected per pass.
- [ ] The one-time bootstrap exception's documentation is corrected: it does not wait for Guardrails' `Open`, and the claim that ordinary eligibility keeps Guardrails selected after its first scan is removed.
- [ ] Investigation's gate is documented as the Safety Net section being present with `Open` empty, plus the existing rule that a recorded rejection counts as resolved.
- [ ] A new ADR records the decisions, states which earlier decisions it replaces (the parser with detection shipping under the scan) or amends (pre-filing for Track nodes; `Open` and `Fulfilled nodes` in the purpose-based fulfilment decision), and briefly lists the alternatives considered and rejected.
- [ ] The domain glossary is updated: the **Track** entry (blockade and yielding), the **Proposals** entry (no pre-filing for Track nodes), the **Fulfilment check** entry (agent-judged for every node), and a new entry for the recognition-only gate node.
- [ ] The repo's documentation validation passes.
