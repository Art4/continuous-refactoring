# `phpmd`

Node on the PHP **tooling tree** (`../php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **Guardrails**).

- **Name:** PHPMD
- **Tool:** PHPMD
- **Purpose:** cyclomatic-complexity and code-quality measurement — a Signal-producing node for
  the search for structural candidates, not a Safety Net one. Deliberately carries **no** `resolved`
  edge into `php-safety-net`/`structural-scan`: adopting it enriches the search for structural candidates, it
  never gates structural work the way the tree's deterministic-tooling leaves do.
- **Required parents:** `composer` (unchanged) and, additionally, `php-safety-net` — a
  **Guardrails** node: workable only once the Safety Net is fulfilled, not from the moment `composer` is
  fulfilled. Additive rather than replacing `composer`: a rejected `composer` must still permanently
  close this node the ordinary required-edge way, which a bare `php-safety-net` edge alone wouldn't do.
- **Fulfilment check:** dev dependency installed (`phpmd/phpmd`), a ruleset config committed
  (`phpmd.xml`, `phpmd.xml.dist`, or `.phpmd.xml`), runnable locally.
- **MR scope:** dependency + ruleset config + one pass over the codebase (fix or explicitly baseline
  what the initial run reports — this tree doesn't prescribe which; a target's own judgement call at
  adoption time).
- **Signal:** Understandability (the complexity measurement itself — nested conditionals, long
  methods, deep coupling) and Defect density (complexity's well-established empirical correlation
  with bug rates) — both `../signals.md` factors. Once this node is
  fulfilled, the search for structural candidates reads its real cyclomatic-complexity output in place of
  the generic (reading-the-code) recognition method for these two factors.
