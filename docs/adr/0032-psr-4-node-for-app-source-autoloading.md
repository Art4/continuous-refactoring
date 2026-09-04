# A new `psr-4` node for the app's own source autoloading

> Not an amendment — a new PHP-tooling-tree node, the tree's normal growth path (same weight as
> ADR-0016's `psr-4`-unrelated node additions before it). Referenced here only because two existing
> nodes' own reference files change as a direct consequence: `phpstan.md`'s `paths` resolution needs
> no edit (already generic), but `phpunit.md`'s `tests/Unit/` namespace derivation gains a new
> source of truth once this node is fulfilled.

A real gap observed on `Art4/legacy-todo`: every PHP file sits flat at the repo root, no namespace,
no `autoload` section in `composer.json` at all, files `require`d by path. PSR-4 already appears
twice in this tree, both times incidentally — `phpunit.md`'s `tests/Unit/` test-layout convention,
and `phpstan.md`'s `paths` resolution (which reads `autoload`/`autoload-dev` when present, falling
back to `src` only when nothing is declared) — but neither models "does the app's own source have a
real, working PSR-4 mapping" as its own adoptable, checkable step.

The obvious framing — "add a node, adopt PSR-4 fully" — doesn't fit this tree's usual shape. Unlike
almost every other node (a config or dependency change with no code restructuring implied),
PSR-4-for-app-source on a flat, unnamespaced legacy codebase is a real, potentially large code
migration: move files, namespace them, update every call site. Settled via a `/grill-me` session
(ticket 50).

## Considered Options

- **Full-compliance Fulfilment check** (every source file namespaced and PSR-4-mapped). Rejected —
  would turn adoption into one large, disruptive MR, unlike the tree's usual small-step shape; a
  flat legacy codebase like `legacy-todo` could never cross this bar in one candidate.
- **Model it as a structural-candidate concern instead of a tooling-tree node at all** (no Fulfilment
  check of its own; namespacing discovered per-module via `refactor-design`'s existing structural
  path). Rejected — loses the mechanism-adoption step entirely: nothing would ever declare the
  `autoload.psr-4` section itself, which structural work then depends on existing.
- **Declaration alone as the Fulfilment bar** (an `autoload.psr-4` section exists, nothing more).
  Rejected during grilling — a declaration nothing yet uses is a claim, not evidence the mechanism
  works, exactly the pattern ADR-0030 (ticket 48) flagged as a problem for a different node
  (`rector-early-return` landing "fulfilled" with no actual effect).
- **`composer` as a `recommended` parent** (the idea's original framing). Rejected — corrected during
  grilling: PSR-4 is literally a field inside `composer.json`, impossible without it. `recommended`
  would let this node stay proposable even with `composer` *rejected* (no Composer at all), which
  makes no sense; it must be `required`.

## Decision

**Fulfilment check** — deliberately low, mirroring `phpstan-level-0`'s own bar (an empty baseline,
not zero errors project-wide): `composer.json`'s `autoload.psr-4` section declares at least one
namespace prefix mapped to a real directory, **and** at least one `.php` file under that directory
actually carries a matching `namespace` declaration. The rest of the migration is deliberately not
this node's job — once fulfilled, every remaining un-namespaced file becomes an ordinary friction
signal for `structural-scan`'s own agent-driven work to discover and migrate incrementally, the same
way any other deepening is.

**MR scope** — declare the mapping, then migrate exactly one real file as proof of the wiring. Not
"migrate every file."

**Required parent**: `composer` — corrected from the idea's original "recommended" framing (see
above).

**Resolved parent of `php-structural-scan`** — joins the existing twelve leaves (thirteenth again,
after ADR-0030 dropped `rector-early-return` back to twelve) as a thirteenth, on a different basis
than every other leaf there: a code-organization convention structural work depends on, not a
checking tool, but decided (fulfilled at the low bar, or explicitly rejected) before agent-driven
structural changes begin, same reasoning as every other leaf in that set.

**`phpunit.md`'s `tests/Unit/` namespace** — once `psr-4` is fulfilled, derives its prefix from that
node's own declared root namespace instead of independently re-deriving from `composer.json`'s
`name` field, avoiding two sources of truth that could drift apart. Falls back to the `name`-derived
prefix, unchanged, when `psr-4` isn't fulfilled yet.

**`phpstan.md`'s `paths` resolution** — no change. It already reads `autoload`/`autoload-dev`
directly; the `src` fallback simply stops triggering once this node adds a real `autoload` section.

## Consequences

A new, low-cost tooling-tree node closes a real modeling gap without pretending a single MR can
namespace an entire legacy codebase. `phpunit.md`'s test-namespace logic gains a dependency it didn't
have before — reading `psr-4`'s own declared root namespace requires that detection to have already
run this pass, same ordering constraint the tree already imposes elsewhere (e.g. `rector-type-coverage`
reading sibling Rector nodes' decided state). `tooling_tree.py` gains two new small helpers
(`_psr4_root_namespace`, `_has_verified_psr4_autoload`) and one new `detect_nodes()` entry; every
fixture under `fixtures/php/` needed its `expected/roadmap.json` regenerated to reflect the new node
(mechanical, no fixture behavior changed beyond gaining/losing this one node).
