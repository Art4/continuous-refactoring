# 05: Script reduced to graph logic, driven by seed input

Spec: `agent-judged-fulfilment`.

**What to build:** The deterministic script gains an input contract that lets it run without its own detection, and the outputs the new model needs. In a scan pass the agent hands over the fulfilled set as a file; in every other pass the script derives node state from the bookkeeping (a scope node that is neither in `Open` nor in `Out-of-scope` is fulfilled). New or reshaped outputs: the workable nodes, the ordered list a scan records into `Open` (tree order, blocked nodes included), the nodes closed by a rejected required ancestor, and the withheld list with reasons. The "what does a landed node unblock" view for the merge-request outlook keeps working. The forward-simulating roadmap and its fixture matrix are removed. The PHP-floor precheck and version-reversal findings stay. The existing detection code stays callable as the default when no seed is given, so scans keep working until ticket 06 switches them.

**Blocked by:** 01 (Stop-conditions become recognition-only gate nodes), 04 (`Open` as the complete backlog).

**Status:** implemented — PR #107, open items listed in Comments

- [x] The script accepts a fulfilled-set file and produces its graph outputs from it, including the recognition-only gate nodes; nodes missing from the file are treated as not fulfilled. The exact file format is fixed here and documented.
- [ ] Without a seed and with a bookkeeping file that has Track sections, the script derives node state from `Open` and `Out-of-scope` as described; a missing section means the Track was never run.
- [x] The script outputs the ordered backlog, the list closed by rejection, and the withheld list with a reason per node; the merge-request outlook view is unchanged in behavior.
- [ ] The roadmap simulation, its fixtures and its harness view are removed, and no documentation still points at them.
- [x] Fixtures supply a seed and a bookkeeping file; deterministic tests assert the script's output contract (workable, ordered backlog, withheld with reasons, closed by rejection, outlook) on those seeds. Existing graph-behavior tests (edge types, gating, rejection cascade, resolved gates, PHP floor) pass, taking the fulfilled set as input.
- [x] Nothing in this ticket removes detection code.

## Comments

**PR:** [#107](https://github.com/Art4/continuous-refactoring/pull/107)

- Item 1: `--seed <file>` or `<Refactoring Notes>/fulfilled-set.json`, JSON `{node_slug: true/false}`,
  missing nodes are not fulfilled; the format is documented in `fixtures/README.md` ("Tooling-tree script")
  and the `tooling_tree.py` docstring. Item 3: `backlog`, `closed_by_rejection`, `withheld_with_reasons`
  in the JSON, `--unblocked-by` unchanged (`SeedInputTests`, `OrderedBacklogTests`,
  `WithheldWithReasonsTests`, `ClosedByRejectionTests`, `DirectlyUnblockedChildrenTests`).
- Item 5: the contract tests build their seeds and bookkeeping files inline in temp repos; the only
  checked-in fixture carrying a seed is `fixtures/php/php-clean` (`fulfilled-set.json`). Item 6: at the
  ticket's own commits `detect_nodes()` was still present; it was removed only in `54105f5` (ticket 11).
- Item 2 not met: without a seed, `_derive_fulfilled_from_bookkeeping` marks every node that is not in
  `Open`/`Out-of-scope` fulfilled, for all Tracks at once, as soon as *any* `## Safety Net`/`## Guardrails`
  state exists. A `bookkeeping.md` with only `## Safety Net` (empty `Open`) and no `## Guardrails` section
  therefore reports every Guardrails node fulfilled (`backlog: []`, 41/41 fulfilled), not "never run". Only
  a file with no Track section at all is treated as never run (returns `{}`).
- Item 4 not met: the roadmap simulation, `expected/roadmap.json` files and the `run.sh` roadmap tier are
  gone (no `roadmap` in `run.sh`, no `expected/roadmap.json` under `fixtures/`), but live text still points
  at the removed output: `skills/refactor-scan/SKILL.md` step 4 ("**Not** `roadmap`"),
  `php-tooling-tree/psalm.md` and `php-tooling-tree/php-safety-net.md` (`next_candidates()`/`roadmap()`),
  `scripts/test_tooling_tree.py` and `scripts/test_trigger_controls.py` docstrings, and
  `.github/workflows/test-harness.yml` comments (historical). See ticket 11 item 3.
