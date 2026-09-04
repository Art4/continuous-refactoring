# 50 — PSR-4 node for the app's own source autoloading

**What to build:** Add a `psr-4` node to the PHP tooling tree
(`skills/refactor-scan/references/php-tooling-tree.md`, reference file at
`skills/refactor-scan/references/php-tooling-tree/psr-4.md`, matching the existing per-node file
convention — `composer.md`, `phpstan.md`, `rector.md`, etc.) covering PSR-4 autoloading for the
**app's own source code** — distinct from the existing incidental PSR-4 usage in `phpunit.md`'s
test-layout convention and `phpstan.md`'s `paths` fallback-to-`src` note, neither of which models
"does the app's own source have a real `autoload` PSR-4 mapping in `composer.json`" as its own
adoptable, checkable step.

**Why:** Real gap observed on `legacy-todo`: every PHP file sits flat at the repo root, no
namespace, no `autoload` section in `composer.json` at all, files `require`d by path. PSR-4
adoption for app source is a natural, currently unmodeled tooling-tree step that plausibly unblocks
or eases later structural work (namespacing, autoload-based static-analysis paths, a consistently
PSR-4-mapped test layout).

**Blocked by:** none.

**Priority:** low — no discovered bug motivates urgency; a proposed tree enhancement, not a fix
(same framing as ticket 38's housekeeping node).

**Status:** needs-triage

Open design questions:

- [ ] Where does this sit in the tree — recommended parent `composer` as sketched in the
  originating memory, or does it need a `required` edge from something (is namespacing app code a
  prerequisite the tree should force before other structural nodes, or purely opt-in)?
- [ ] `Tool:` field — `none` (a `composer.json` config change, not a package adoption) as the memory
  suggests; confirm against the existing convention for config-only nodes rather than
  tool-adoption nodes.
- [ ] Fulfilment check: full-repo PSR-4 compliance (every source file namespaced and mapped), or a
  lower bar (an `autoload` PSR-4 section exists and at least new/touched files comply, migrating
  incrementally)? A flat, unnamespaced legacy codebase like `legacy-todo` could make "full
  compliance" a large, disruptive single MR rather than the tree's usual small-step shape.
- [ ] MR scope: a single MR (declare the mapping + move/namespace every file), or, like the
  PHPStan-level/Rector-level nodes, adopted incrementally in slices — and if incremental, what
  determines a slice boundary (per-file? per-directory?)?
- [ ] Downstream updates this would trigger once decided: `phpstan.md`'s `paths` resolution note
  (stop falling back to `src` once a PSR-4 mapping can be assumed present) and `phpunit.md`'s
  `tests/Unit/` namespace-prefix derivation (currently ad hoc from `composer.json` `name` alone) —
  confirm both actually need edits, or whether one turns out to be a non-issue once grilled.
- [ ] Interaction with `structural-scan`'s resolved-gate — should `psr-4` become one of its resolved
  parents (structural work waits on it being decided), or stay a parallel, non-gating tooling node
  like most others in the family?

## Comments

> **2026-09-04:** Filed from the `psr4-tooling-tree-node-idea` memory (raised 2026-09-04 during the
> `Art4/legacy-todo` reviewer-loop run), per the user's request to prepare "für später" ideas for
> fixing. Not yet grilled.
