# Agent-judged fulfilment, deterministic graph

**Status:** ready-for-agent

Builds on [ADR-0055](../../docs/adr/0055-purpose-based-fulfilment-and-scheduled-tracks.md), which already moved the Safety Net and Guardrails nodes' **Fulfilment check** to agent judgement against each node's **Purpose**, with the parser's own result kept as a "first signal". This spec finishes that move for every node, removes the parser's detection half, and reworks what `Open` means so a Track's own bookkeeping can drive scheduling on its own. A new ADR will record the decisions (see *Further Notes*).

## Problem Statement

A target-repo maintainer gets proposals the loop shouldn't make, or none it should, because the deterministic parser still carries hardcoded tool-name detection for every tooling-tree node. That detection is imprecise, has to be updated for every new tool, and can never recognize a tool the suite doesn't know about. For the Safety Net and Guardrails nodes the agent already overrules it, so the parser's answer is stale ground truth: its own tier of ground-truth tests had to go local-only because of that. Two implementations of the same Fulfilment check (parser code and tree-doc prose) also drift apart.

Around that, several loose ends surface once fulfilment is agent-judged:

- `Fulfilled nodes` survives as a cache with no clear reader: the manual tree-walk fallback reads it, the Housekeeping Track's reconciliation reads it too (undocumented), and its self-healing overwrite depended on the parser. For Guardrails nodes it never holds anything, so the reconciliation can miss a Guardrails node's `Housekeeping` line for a tool the maintainer adopted by hand.
- A Track's `Open` list holds only nodes that are currently unblocked, so "`Open` is empty" does not mean "this Track is done". The one-time bootstrap exception and Investigation's `structural-scan` gate both read it as if it did.
- The parser's graph logic branches on a few special-case flags (no audit without a real dependency, no PHPStan level proposals while the baseline is non-empty, no level chain when Psalm is the analyzer) that no tree doc shows as tree structure.
- Every tooling-tree candidate is pre-filed as an issue the moment it is proposed, which stops scaling once a Track's whole backlog is visible at once.
- The scheduler's own text claims an `Open`-driven guarantee that the exception's evaluation order actually bypasses.

## Solution

Every node's Fulfilment check is judged by the agent against the node's Purpose. The deterministic script keeps only what has to be deterministic: the tree's graph logic (what is unblocked, what is withheld and why, what a rejection closes) plus the PHP-version blocking and reversal it already does. Detection code, the `Fulfilled nodes` cache and the forward-simulating roadmap go away.

Each node-based Track's `Open` becomes the Track's complete, ordered backlog: every node of the Track's scope that is neither fulfilled nor out-of-scope, blocked ones included. One node per loop is worked top to bottom, and a Track is done when its `Open` is empty. The Safety Net Track blocks every other Track until then. Guardrails yields to Investigation and Housekeeping whenever none of its `Open` nodes can currently be worked.

The manual tree-walk fallback stays, for targets where Python is unavailable or the user doesn't allow running the script; it follows the same rules by hand.

## User Stories

1. As a target-repo maintainer, I want the loop to recognize any real tool that serves a node's Purpose, including tools the suite has never heard of, so that I'm never asked to adopt something I already have.
2. As a target-repo maintainer, I want `Open` in `bookkeeping.md` to list every node the Track still has to resolve, blocked ones included, so that I can read the whole remaining backlog in one place.
3. As a target-repo maintainer, I want a Track's `Open` being empty to mean exactly "every node fulfilled or explicitly out-of-scope", so that nothing downstream acts on a half-finished Track.
4. As a target-repo maintainer, I want `Open` to already be in the order the loop will work it, so that I can see what comes next.
5. As a target-repo maintainer, I want to reorder `Open` by hand to change what gets worked next, so that I can prioritize without labels on issues that don't exist yet.
6. As a target-repo maintainer, I want the loop to work one node per pass, top to bottom, so that each pass produces one reviewable change.
7. As a target-repo maintainer, I want no candidate issues for nodes the loop hasn't reached yet, so that my tracker isn't flooded by a whole Track's backlog and the open-candidate backlog limit isn't tripped by it.
8. As a target-repo maintainer, I want a node's issue created only when the loop starts working that node, so that the tracker shows what's actually in flight.
9. As a target-repo maintainer, I want the loop to re-check a node's Fulfilment check right before working it, so that a tool I adopted by hand since the last scan isn't introduced a second time.
10. As a target-repo maintainer, I want a node found already fulfilled at that moment to leave `Open` without a merge request, so that the loop moves on to the next node.
11. As a target-repo maintainer, I want the Safety Net Track to hold back every other Track until its `Open` is empty, so that structural work never starts on an unfinished foundation.
12. As a target-repo maintainer, I want a Safety Net node I must decide on (for example one flagged `needs-info`) to keep the Track open and be reported plainly, so that I know what the loop is waiting for.
13. As a target-repo maintainer, I want Guardrails nodes that currently can't be worked (a stop-condition holds, the PHP floor is too low, a candidate waits on me) not to block Investigation and Housekeeping, so that one stuck node doesn't freeze everything else.
14. As a target-repo maintainer, I want each stalled node reported with its reason at the end of a pass, so that I can decide whether to unblock it or reject it.
15. As a target-repo maintainer, I want Housekeeping to run when it is due even while Guardrails still has workable nodes, so that periodic maintenance doesn't wait weeks behind a backlog.
16. As a target-repo maintainer, I want Investigation to wait behind a Guardrails backlog with workable nodes, so that structural work doesn't compete with finishing the tooling.
17. As a target-repo maintainer, I want the one-time bootstrap sequence (Investigation, then Guardrails, then Housekeeping, one turn each) to keep running in that order right after the Safety Net is done, without waiting for Guardrails' `Open` to empty, so that the sequence stays short and predictable.
18. As a target-repo maintainer, I want Investigation to propose `structural-scan` only once the Safety Net Track is done, so that structural work and deterministic tooling never collide.
19. As a target-repo maintainer, when I removed a tool on purpose, I want it re-proposed at the Track's next scan (at most 90 or 60 days later), so that I can reject it then, or accept it once my reasons have gone away.
20. As a target-repo maintainer, I want rejecting a node to also remove every node that required it from `Open` automatically, so that `Open` can still become empty.
21. As a target-repo maintainer, I want that closing to be derived rather than recorded, so that reversing the rejection later needs no cleanup.
22. As a target-repo maintainer, I want an issue I labeled `refactor:priority` to still be preferred over the top of `Open`, so that my explicit choice wins.
23. As a target-repo maintainer, I want that label not to override the Safety Net blockade or the Track selection, so that a blockade can't be bypassed by accident.
24. As a target-repo maintainer, I want the Housekeeping checklist to contain the lines of tools I adopted by hand, including Guardrails tools, so that periodic sweeps cover everything I actually run.
25. As a target-repo maintainer, I want no `Fulfilled nodes` field to maintain or distrust, so that `bookkeeping.md` states only what is still open or rejected.
26. As a target-repo maintainer with an existing `bookkeeping.md`, I want old fields ignored and nothing migrated, with a manual Track override to force an immediate rescan, so that upgrading needs no repo surgery.
27. As a target-repo maintainer whose machine has no Python, or who doesn't allow running the script, I want the loop to work the same way by hand, so that I'm not locked out.
28. As a target-repo maintainer, I want a Psalm-based project to resolve the PHPStan level chain the way it does today (through the recorded mutual-exclusion rejection), so that its Safety Net Track can still finish.
29. As a target-repo maintainer, I want `git`, `loop-config` and `is-php-project` still checked before anything else, so that the mandatory `loop-config` interview stays the first step on a fresh repo.
30. As a target-repo maintainer, I want the suite-wide cap on open suite merge requests to stay one shared check across all Tracks, so that the reviewer isn't overwhelmed.
31. As a suite maintainer, I want the script to depend only on the tree, the recorded rejections, the bookkeeping and the fulfilled set it is given, so that the same inputs always give the same output.
32. As a suite maintainer, I want adding or changing a tool's recognition to be one edit in the node's tree doc, so that no parser code has to change.
33. As a suite maintainer, I want the special-case stop conditions expressed as tree nodes with edges, so that the graph logic has no hidden flags.
34. As a suite maintainer, I want each detection heuristic the parser has audited against its tree doc before any code is deleted, so that no precision is lost silently.
35. As a suite maintainer, I want the manual fallback's prose and the script's output compared on shared seed inputs, so that the two implementations of the graph rules can't drift unnoticed.
36. As a suite maintainer, I want the merge-request outlook diagram (what a landed node unblocks) to keep working, so that reviewers keep that context.
37. As a suite maintainer, I want the scheduler's documentation to describe the real evaluation order, so that its stated guarantees hold.
38. As a suite maintainer, I want each step of the migration separately mergeable and, until the last one, separately revertible, so that a mistake in the middle never strands the suite.
39. As a suite maintainer, I want the decision recorded in an ADR that names which earlier decisions it replaces or amends, so that the record stays coherent.

## Implementation Decisions

- **Who judges fulfilment.** The agent judges every node's Fulfilment check against the node's Purpose, following the existing per-node prose in the tree docs. This includes `git`, `loop-config` and `is-php-project`. The parser no longer produces a fulfilled value for any node. The existing Flagged-candidate mechanism (`needs-info`) for genuinely ambiguous judgements is unchanged, and so is the rejection route for purposes served by convention rather than by a tool.
- **What the script keeps.** Graph logic only: unblocked and withheld computation with reasons, required, recommended, required-any and resolved edge semantics, the resolved-gate computation, cascading closure of a rejected required parent, the PHP-floor precheck and version-reversal findings, and the "what does a landed node unblock" view for the merge-request outlook. Detection helpers are removed at the end of the migration (not before). The forward-simulating roadmap and its fixture matrix are removed.
- **Script inputs and outputs.** Inputs: the tree docs, the recorded rejections, the Track sections of `bookkeeping.md`, and, for a scan pass only, a fulfilled set the agent hands over as a file. In every other pass the script derives node state from `bookkeeping.md`: a scope node that is neither in `Open` nor in `Out-of-scope` is fulfilled. New or reshaped outputs: the ordered `Open` order for a scan to record, the list of nodes closed by a rejected ancestor, and the withheld list with reasons (used for the stalled report). Exact file format for the fulfilled set is left to the implementing ticket.
- **Stop-conditions become tree nodes.** Three recognition-only gate nodes, modeled on the existing `is-php-project` gate (never proposed, only a required parent): one meaning "the project has a real (non-platform) dependency" gating the audit node, one meaning "the current PHPStan baseline is empty" gating every PHPStan level node, and one meaning "PHPStan, not Psalm, is the project's analyzer" gating the first level above zero. Their Fulfilment checks are agent-judged prose in the tree docs. The graph logic loses every special-case flag. The gate for the baseline is a recurring state rather than a one-way delivery; the implementing ticket must verify the permanent-gating and recommended-parent logic against that.
- **`Open` semantics.** After a completed scan, a node-based Track's `Open` holds every unresolved node of the Track's scope, in the script's deterministic order (tree table order, blocked nodes included); `Out-of-scope` keeps its meaning. `Open` empty means the Track is done. A Track's `Last scan` is still written on every completed scan. A Track's `Open` entries no longer carry an issue number unless the node is currently being worked; a human may reorder `Open` by hand.
- **Working an `Open` node.** Each pass works the topmost workable node (unblocked per the graph, not flagged `needs-info`, not blocked by the PHP floor). Before creating the node's issue, the agent re-runs that one node's Fulfilment check; if it is now fulfilled, the node leaves `Open` without a merge request and the pass continues with the next workable node. The issue is created only at this point. Track nodes are no longer pre-filed: Rank mode no longer runs for them, and the pre-filing rule applies only to what it always excluded plus any issue-backed proposal a human created.
- **Priority label.** An issue labeled for priority still narrows the Rank pool exactly as today and therefore outranks the top of `Open`. It does not participate in Track selection and cannot bypass the Safety Net blockade.
- **Scheduling.** Safety Net with a non-empty `Open` is always selected, and no other Track runs, whether or not a node is currently workable; a node waiting on the human is reported. Guardrails with at least one workable `Open` node is selected ahead of Investigation; Housekeeping preempts it for a pass when it is due (`overdue_ratio` at or above 1). Guardrails with `Open` non-empty but nothing workable is stalled: it yields the pass to the remaining Tracks by the ordinary ratio and tie-break rules, its `Open` stays as it is, and the pass report lists each stalled node with its reason. With `Open` empty, a Track is rescanned when due by cadence, as today. The fixed tie-break order and the manual Track override are unchanged.
- **One-time bootstrap exception.** Its precondition stays "Safety Net section present and `Open` empty", which is now sound. Its three turns still run one Track per pass in the existing order and do not wait for Guardrails' `Open`. Its documentation is corrected: the claim that ordinary eligibility keeps Guardrails selected after its first scan is wrong and is removed. At most one Track is ever selected per pass.
- **Investigation's gate.** `structural-scan` is proposable only when the Safety Net Track's section exists and its `Open` is empty, plus the existing rule that a recorded rejection counts as resolved. Investigation no longer re-judges the Safety Net leaves each pass; a tool removed later is noticed at the Safety Net's next scan.
- **Rejections and cascades.** Rejecting a node removes it from `Open`, writes the recorded rejection and the `Out-of-scope` pointer as today. Nodes closed by a rejected required ancestor are derived by the script and dropped from `Open` without new files; reversing the rejection makes the next scan pick them up again.
- **Bookkeeping schema.** `Fulfilled nodes` is retired; nothing reads or writes it, old repos keep the field and it is ignored. `Cadence`, `Last scan`, `Open` and `Out-of-scope` keep their names. No migration: a section written under the old `Open` meaning (unblocked nodes only) is left as it is and is corrected by the Track's next scan; a maintainer can force an immediate scan with the Track override.
- **Housekeeping reconciliation.** The reconciliation stops reading `Fulfilled nodes`. Each Housekeeping cycle instead checks only the nodes that carry a `Housekeeping` field and appends any missing line, judged by the agent. Delivering such a node's merge request continues to contribute its line as it does today. Removing lines stays a hand edit.
- **Fallback.** Python stays the default and stays optional. The manual tree-walk prompt remains, follows the same `Open`, ordering and stalled rules by hand, and loses its `Fulfilled nodes` cache step.
- **Unchanged.** Anti-flapping across passes: the agent's judgement is the authority, no extra guard. PHP-floor and version-reversal logic, the suite-wide cap on open suite merge requests, the `loop-config` interview, Investigation's candidate search, node slugs, and the recorded `out-of-scope` format.
- **Migration order.** Expand–contract: audit and gate nodes first (no runtime change), `Open` semantics and scheduler documentation alongside the script's new input contract (detection still present), then the skills' switch to agent input, then the tests, and last the deletion of detection code. Until the last step each ticket is independently revertible.

## Testing Decisions

Two seams, both existing.

- **Script contract (deterministic, CI).** Drive the script's JSON output on seeded fixtures: a fixture supplies a fulfilled set and a `bookkeeping.md` with `Open`/`Out-of-scope`, and the test asserts the workable list, the ordered `Open`, the withheld list with reasons, the closed-by-rejection list and the outlook view. This replaces the detection-derived expected outputs and the unit tests of detection helpers. The existing unit tests of graph behavior (edges, gating, rejection cascade, resolved gates, PHP floor) stay, adapted to take the fulfilled set as input.
- **Agent behavior (local, advisory).** The existing fixture harness with a seeded target-repo state and an expected-behavior description per fixture, as the scheduler fixtures already do. It checks decisions reached (which Track was selected, what `bookkeeping.md` received, what was proposed or dropped), never internal reasoning or prose wording. It also hosts the drift check, running the manual fallback against the same seeds and comparing its workable and withheld results with the script's.

A good test asserts external behavior only: which node is worked next, which Track runs, what gets written. Prior art: the existing scheduler fixtures for Track selection and bootstrap, the Safety Net and Guardrails first-run, open-blocks-rescan and rejection-symmetry fixtures, and the old-schema pass-through fixtures.

New fixtures and cases to add:

1. Safety Net `Open` non-empty with nothing workable: nothing else runs, the wait is reported.
2. Guardrails stalled (only stop-condition or PHP-floor blocked nodes): Investigation and Housekeeping proceed, stalled nodes reported with reasons.
3. Guardrails with a workable node and Housekeeping due: Housekeeping runs one pass, then Guardrails resumes; Investigation waits.
4. Scan populates `Open` with blocked nodes in script order.
5. Pick-up re-check: a node fulfilled by hand after the scan leaves `Open` without a merge request.
6. Rejected ancestor: descendants drop out of `Open`; reversing the rejection brings them back at the next scan.
7. Gate nodes: a project with no real dependency, a non-empty baseline, and a Psalm project each keep the gated nodes unproposed.
8. Housekeeping sweep adds the line for a hand-adopted Guardrails tool that has no merge-request history.
9. Priority-labeled issue outranks the top of `Open` but not the Safety Net blockade.
10. Old-schema and old-`Open` bookkeeping: ignored fields, no error, forced rescan via override.
11. Drift check: fallback prose and script agree on the shared seeds.

## Out of Scope

- Rewriting the PHP-floor precheck or version-reversal findings; they stay deterministic as they are.
- Restructuring the tree beyond the three new gate nodes; renaming node slugs.
- A guard against the agent judging the same node differently in two passes.
- Signal-based ordering inside `Open`; ordering is the tree order until Rank mode's removal for Track nodes has been observed in practice.
- Migrating existing `bookkeeping.md` files.
- Extending agent judgement to Investigation's structural-candidate search, which was never fulfilment-driven.
- Detecting a regression (a tool removed later) between scans.
- Other language specializations beyond PHP.

## Further Notes

- **Tickets.** Eleven tickets in this directory, in expand–contract order: (01) stop-conditions as gate nodes; (02, 03) prose audit of the Safety Net and of the Guardrails nodes and gates; (04) `Open` schema, scheduler rules, ADR and glossary; (05) script reduced to graph logic with seed input; (06) scan fills `Open` and `refactor-learn` maintains it; (07) working an `Open` node top to bottom with pick-up re-check and no pre-filing; (08) scheduler blockade, yield and Housekeeping insertion; (09) Housekeeping sweep over the five nodes and removal of `Fulfilled nodes`; (10) drift check and detection-free tests; (11) deletion of the detection code. 01 and 04 can start immediately; 02 and 03 follow 01; 05 needs 01 and 04.
- **ADR.** One new ADR (ticket 04) replaces the earlier decision to ship the parser with detection under `refactor-scan`, amends the pre-filing decision for Track nodes, and amends ADR-0055 on the meaning of `Open` and on `Fulfilled nodes`.
- **Earlier tickets 08 and 09 of the purpose-based-fulfilment directory** (open pull requests when this spec was written) are absorbed here: 08's behavioral premise no longer holds, only its documentation correction remains and is part of ticket 04; 09 is covered by tickets 01, 02, 03 and 09. Those pull requests are closed unmerged, together with the earlier spec-only pull request this spec was first proposed in.
- **Glossary.** Ticket 04 updates the **Track** entry (Safety Net blockade, Guardrails yielding), the **Proposals** entry (no pre-filing for Track nodes) and the **Fulfilment check** entry, and adds an entry for the recognition-only gate node.
- **Known details left to tickets.** The fulfilled-set file format (ticket 05), and whether the stalled report also appears as an issue comment or only in the pass status (ticket 08).
