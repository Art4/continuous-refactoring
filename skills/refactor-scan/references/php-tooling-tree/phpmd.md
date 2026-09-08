# `phpmd`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**).

- **Name:** PHPMD
- **Tool:** PHPMD
- **Purpose:** cyclomatic-complexity and code-quality measurement — a Signal-producing node for
  `refactor-prioritize`'s Select mode, not a Safety Net one. Deliberately carries **no** `resolved`
  edge into `php-structural-scan`/`structural-scan`: adopting it enriches candidate selection, it
  never gates structural work the way the tree's deterministic-tooling leaves do. Proposed and ranked
  through the ordinary scan/prioritize cycle like any other node — no special-cased admission.
- **Fulfilment check:** dev dependency installed (`phpmd/phpmd`), a ruleset config committed
  (`phpmd.xml`, `phpmd.xml.dist`, or `.phpmd.xml`), runnable locally.
- **MR scope:** dependency + ruleset config + one pass over the codebase (fix or explicitly baseline
  what the initial run reports — this tree doesn't prescribe which; a target's own judgement call at
  adoption time).
- **Signal:** Understandability (the complexity measurement itself — nested conditionals, long
  methods, deep coupling) and Defect density (complexity's well-established empirical correlation
  with bug rates) — both `skills/refactor-prioritize/references/signals.md` factors. Once this node is
  fulfilled, `refactor-prioritize`'s Select mode prefers its real cyclomatic-complexity output over
  `signals.md`'s generic (reading-the-code) recognition method for these two factors.
