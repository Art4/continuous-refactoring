# 05: Script reduced to graph logic, driven by seed input

Spec: `agent-judged-fulfilment`.

**What to build:** The deterministic script gains an input contract that lets it run without its own detection, and the outputs the new model needs. In a scan pass the agent hands over the fulfilled set as a file; in every other pass the script derives node state from the bookkeeping (a scope node that is neither in `Open` nor in `Out-of-scope` is fulfilled). New or reshaped outputs: the workable nodes, the ordered list a scan records into `Open` (tree order, blocked nodes included), the nodes closed by a rejected required ancestor, and the withheld list with reasons. The "what does a landed node unblock" view for the merge-request outlook keeps working. The forward-simulating roadmap and its fixture matrix are removed. The PHP-floor precheck and version-reversal findings stay. The existing detection code stays callable as the default when no seed is given, so scans keep working until ticket 06 switches them.

**Blocked by:** 01 (Stop-conditions become recognition-only gate nodes), 04 (`Open` as the complete backlog).

**Status:** ready-for-agent

- [ ] The script accepts a fulfilled-set file and produces its graph outputs from it, including the recognition-only gate nodes; nodes missing from the file are treated as not fulfilled. The exact file format is fixed here and documented.
- [ ] Without a seed and with a bookkeeping file that has Track sections, the script derives node state from `Open` and `Out-of-scope` as described; a missing section means the Track was never run.
- [ ] The script outputs the ordered backlog, the list closed by rejection, and the withheld list with a reason per node; the merge-request outlook view is unchanged in behavior.
- [ ] The roadmap simulation, its fixtures and its harness view are removed, and no documentation still points at them.
- [ ] Fixtures supply a seed and a bookkeeping file; deterministic tests assert the script's output contract (workable, ordered backlog, withheld with reasons, closed by rejection, outlook) on those seeds. Existing graph-behavior tests (edge types, gating, rejection cascade, resolved gates, PHP floor) pass, taking the fulfilled set as input.
- [ ] Nothing in this ticket removes detection code.
