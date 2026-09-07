# Signal-producing tooling-tree nodes never gate `structural-scan`; three existing PHP-tree edges simplified

> Amends [ADR-0019](0019-static-analyzer-mutual-exclusion-and-taint-analysis-node.md): its "Considered
> Options" list rejected "also drop `php-cs-fixer`/`phpunit`'s direct `php-structural-scan` resolved
> edges" as "a real gate relaxation, not a no-op." This ADR does drop `php-cs-fixer`'s direct edge after
> all — but only once a compensating `recommended` edge into `rector-php-set` is added in the same
> change, which the earlier, rejected version lacked. `phpunit`'s own leaf is untouched; ADR-0019's
> concern about it stands.

Raised while filing candidate issues against `Art4/legacy-todo` (signals ticket 1, ADR-0038/0039): the
suite's own stated principle — deterministic tooling signals take precedence over agentic
reading-the-code recognition — was contradicted by its own tree. Five tickets
(`.scratch/php-tooling-tree/issues/08,09,11,13,14`) proposed tools (PHPMD, mutation testing, a coverage
floor, SAST, DAST, secret detection) whose entire purpose is producing exactly this kind of
deterministic evidence, yet none were real tooling-tree nodes — `signals.md` could only ever recommend
the generic, read-the-code recognition method for the factors those tools cover, since there was no
adopted-node state to prefer instead. Settled via `/grill-with-docs` (three rounds) directly against
`skills/refactor-scan/references/{tooling-tree.md,php-tooling-tree.md}`.

## Considered Options

- **Leave Signal-producing tools as documentation-only entries in `signals.md`**, as ticket 1 left them.
  Rejected — this is the chicken-and-egg problem itself: a target never gets credit for adopting one of
  these tools, so there's no incentive path from "tool absent" to "tool adopted, Select mode uses its
  real output," only ever the generic heuristic.
- **Make the new nodes ordinary `php-structural-scan`/`structural-scan` resolved-leaves**, like every
  existing deterministic-tooling node. Rejected — these tools produce prioritization evidence, not
  regression protection; gating structural work on PHPMD or a secret scanner being adopted would extend
  the Safety Net's scope to something it was never meant to cover, and would make five/six more nodes
  mandatory decisions (fulfilled or explicitly rejected) before any target could ever reach
  `structural-scan` at all — a real cost for zero Safety Net benefit.
- **A separate second tree, parallel to the tooling tree, for Signal-only nodes.** Rejected — the
  existing tree's `required`/`recommended` machinery (adoption prerequisites, `next_candidates()`,
  `roadmap()`) already does everything a Signal node needs; a second parser/edge-table/detection layer
  would duplicate all of it for no real gain over "same tree, no `resolved` edge into `structural-scan`."
- **A second, distinct field name for this node-level concept, instead of reusing `Signal`.** Rejected —
  the node-level field and the existing candidate-issue field name the exact same thing: which
  `signals.md` factor applies, and why. A second name would suggest two different concepts sharing a
  catalogue by coincidence, when in fact a Signal-producing node's whole purpose is to eventually
  *become* the evidence a candidate issue's own Signal field cites — one glossary entry now explicitly
  covering both usages (`CONTEXT.md`, widened) is more honest than two similarly-named terms would be.
- **Keep `test-runner-if-missing`'s direct `php-structural-scan` resolved edge, add no replacement.**
  This is what shipped (see Decision below) — recorded here because the alternative, giving it a
  replacement edge, was seriously considered and rejected: `ci-runner` already carries its own
  independent `resolved` edge straight into `structural-scan` itself (the generic root,
  `tooling-tree.md`) — a second edge from `test-runner-if-missing` into `php-structural-scan` would only
  ever be redundant with a gate `structural-scan` already has through a shorter path.
- **Give `phpstan-level-10` a replacement leaf at some level other than 5** (levels 4, 6, 7 were each
  raised during grilling). Rejected in favor of level 5 specifically — it's the level chain's only
  existing structural fork point (`phpstan-deprecation-rules`'s own required-parent line already forks
  there), and matches the user's own field experience that level 6+ strictness (heavier array typing)
  starts trading off against "simple refactoring shouldn't be blocked."
- **Keep `phpstan-level-10` as the leaf, alongside the new `phpstan-level-5` leaf, rather than replacing
  it.** Rejected — redundant in the same way the `test-runner-if-missing` replacement option above was:
  `phpstan-level-10 → phpstan-level-9 → … → phpstan-level-5` is a `required`-edge chain, so once level 5
  is a resolved-leaf, level 10 being fulfilled or rejected always implies level 5 already is too. A
  second edge would never independently gate anything level 5's own edge doesn't already cover.

## Decision

### New nodes: `phpmd` (PHP tree) and `secret-detection` (generic root)

Two Signal-producing nodes, real and adoptable, neither carrying a `resolved` edge into
`php-structural-scan`/`structural-scan`:

- **`phpmd`** — `php-tooling-tree.md`, required parent `composer` (same shape as `php-cs-fixer`).
  Fulfilment check: `phpmd/phpmd` dependency + a committed `phpmd.xml`/`phpmd.xml.dist`/`.phpmd.xml`
  config, the same dep+config approximation `php-cs-fixer` already uses. Signal: Understandability +
  Defect density.
- **`secret-detection`** — `tooling-tree.md` (generic root), required parent `loop-config`. Chosen for
  the generic root rather than the PHP tree because a secret scanner reads git history and file
  contents directly — no language-specific tooling ecosystem involved, so a future non-PHP
  specialization inherits it automatically. Fulfilment check: a CI job invoking a recognized scanner
  (gitleaks, detect-secrets, trufflehog — a tool-agnostic node, like `test-runner-if-missing`'s own "any
  test runner"). Signal: Security. Implements the CI-gate half of
  `.scratch/php-tooling-tree/issues/13-secret-detection-in-baseline.md`; that ticket's retroactive
  git-history-scan half (filing candidates for secrets already committed) stays explicitly out of scope
  for this node's own adoption MR — real, separate follow-up work.

Tickets 08 (coverage floor), 09 (mutation testing), 11 (SAST) stay open, each updated with a comment
pointing at this decision as the pattern to follow once picked up — not implemented here, since neither
had a settled concrete tool choice the way PHPMD and secret detection did.

### A new node-level `Signal` field

Mirrors the `Housekeeping` field ADR-0037 added: an optional field on a tooling-tree node's own doc,
alongside Purpose/Fulfilment check/MR scope. Once a Signal-producing node is fulfilled,
`refactor-prioritize`'s Select mode reads its real tool output for the named `signals.md` factor instead
of falling back to the generic, reading-the-code recognition method. `CONTEXT.md`'s existing `Signal`
entry — until now scoped only to "the third field on a candidate issue" — is widened to cover both
usages explicitly; the **Tooling tree** entry gains one sentence cross-referencing it, the same way it
already does for `Housekeeping`.

### Three edge simplifications to the existing PHP tree

All three were proposed by the user, each verified independently before being confirmed:

1. **`test-runner-if-missing` drops its direct `resolved` edge into `php-structural-scan`, with no
   replacement.** `ci-runner` already gates `structural-scan` directly and independently (generic
   root); a target having *some* CI runner was always the actual guarantee this edge encoded, and that
   guarantee already exists elsewhere. `phpunit` itself is unaffected — remains its own direct leaf,
   still guaranteeing a real test suite runs, not just that a runner exists.

2. **`php-cs-fixer` gains a `recommended` edge into `rector-php-set`; its own direct `resolved` edge into
   `php-structural-scan` is removed.** Verified topologically lossless: `php-cs-fixer` is still proposed
   early (`composer`'s own `required` parent), and the new `recommended` edge still transitively forces
   it to be *decided* before `php-structural-scan` can resolve — `rector-php-set` requires
   `rector-dead-code`/`rector-code-quality` decided, and both remain direct `php-structural-scan` leaves
   in their own right. Reverses two prior decisions, both re-confirmed directly with the user before
   implementing:
   - A ticket-43 decision that `rector-php-set` should *not* get a `php-cs-fixer` recommended parent —
     "the styling-order exception in the family," believed (not fully certain) to have existed so
     `php-cs-fixer` couldn't end up the only node with no recommended child. No longer applies once
     `php-cs-fixer`'s own leaf status is what's being removed.
   - ADR-0019's own "Considered Options" rejection of the same drop (see the amendment note at the top
     of this document) — the critical difference from what ADR-0019 rejected is the compensating edge:
     ADR-0019's version dropped the leaf with nothing forcing `php-cs-fixer` to be decided first; this
     version adds exactly that forcing edge in the same change.

3. **`phpstan-level-10`'s `resolved` edge is replaced (not kept alongside) by `phpstan-level-5 →
   php-structural-scan | resolved`.** Level 5 is the level chain's only existing structural fork point —
   `phpstan-deprecation-rules`'s own required-parent line already forks there. Unlike the two edges
   above, this one is a real, deliberate trade-off, not a lossless restructuring: earlier structural work
   in exchange for less strictness guaranteed up front. Levels 6–10 remain ordinary, non-gating,
   still-proposable chain nodes — adopting them stays available and encouraged, just no longer mandatory
   before `structural-scan` opens.

`php-structural-scan` now aggregates eleven `resolved` leaves (down from thirteen):
`psr-4`, `composer-audit`, `phpunit`, `phpstan-level-5`, `phpstan-deprecation-rules`, `rector-dead-code`,
`rector-type-coverage`, `rector-php-set`, `rector-code-quality`, `rector-phpunit-set`,
`psalm-taint-analysis`. The PHP-floor-precheck's five-node leaf set (`php-cs-fixer`, `phpunit`,
`test-runner-if-missing`, `composer-audit`, `phpstan-level-0`) is unchanged in membership; only two of
those five (`phpunit`, `composer-audit`) are still also `php-structural-scan` leaves, down from four.

## Consequences

`tooling_tree.py` needed zero code changes for the three edge simplifications — the graph (`resolved_parents`,
`required_parents`, `recommended_parents`, `exposed_resolved_gate_nodes`) is derived entirely from
`load_tree()`/`_parse_edges()`'s read of the markdown edge tables, so restructuring edges is a pure
documentation change. Only the two new nodes' fulfilment detection needed real code: a
`_has_secret_scan_ci_job()` helper (reusing the existing `_has_ci_job_invoking()` primitive
`composer-audit`/`phpunit`/`phpstan-level-0`/`psalm-taint-analysis` already share) and a `phpmd`
dep+config check mirroring `php-cs-fixer`'s own.

Fixture fallout, matching the scale ADR-0019 documented for its own Rector-family restructuring: eight
`fixtures/php/*/expected/roadmap.json` snapshots regenerated (`tree["order"]`'s roadmap-simulation
priority shifted once `secret-detection`'s edge was inserted into `tooling-tree.md`'s edge table); two
fixture-project `out-of-scope/phpstan-level-10.md` rejections (`php-psalm`, `php-clean`) renamed/rewritten
around the new `phpstan-level-5` leaf; `php-clean`'s own "every leaf resolved" negative-control fixture
gained a `phpmd` dep+config and a `gitleaks` CI step, so the fixture's own stated property (nothing but
`structural-scan` proposable) still holds now that two more real, non-gating nodes exist for it to
otherwise leave dangling. `scripts/test_tooling_tree.py` and `scripts/test_trigger_controls.py` both
needed corresponding updates — new edge assertions, renumbered roadmap-order indices, and several tests
whose fixtures had (coincidentally, before this change) configured PHPStan at exactly level 5 or level 10
for reasons that only made sense under the old leaf.

`CONTEXT.md` gains the widened `Signal` entry and one new sentence on the **Tooling tree** entry
cross-referencing it. `.scratch/php-tooling-tree/issues/08,09,11,13,14` each gain a comment; 13 is
partially implemented (see above), the other four record the "Signal-producing, no resolved edge" pattern
to follow once picked up, without implementing tools that were never concretely chosen.
