# `psr-4`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**, **resolved edge**).

- **Name:** PSR-4 Autoloading
- **Tool:** none — a `composer.json` autoload declaration plus a namespace convention, not a runnable tool (same shape as `.editorconfig`'s own "plain-text convention file" node).
- **Purpose:** give the app's own source code a real PSR-4 namespace mapping. Distinct from PSR-4's two existing *incidental* appearances in this tree — `phpunit.md`'s `tests/Unit/` test-layout convention, and `phpstan.md`'s `paths` resolution (which already reads `autoload`/`autoload-dev` when present, falling back to `src` only when nothing is declared) — neither of those models "does the app's own source have a real, working PSR-4 mapping" as its own adoptable, checkable step. This node is deliberately scoped narrow: it adopts the *mechanism*, not a full migration of every file. A flat, unnamespaced legacy codebase (every file at the repo root, no namespace, `require`d by path) could otherwise turn "adopt PSR-4" into one large, disruptive MR — the tree's usual small-step shape doesn't fit that. Once this node is fulfilled, every remaining un-namespaced file is simply an ordinary friction signal for `structural-scan`'s own agent-driven work to discover and migrate incrementally, the same way any other deepening is discovered — not something this node itself owns or tracks.
- **Fulfilment check:** two criteria, both required. (1) **Mechanism proven:** `composer.json`'s `autoload.psr-4` section declares at least one namespace prefix mapped to a real directory, **and** at least one `.php` file under that directory actually carries a `namespace` declaration matching the mapped prefix. Declaration alone isn't enough — an `autoload.psr-4` section nothing yet uses is a claim, not evidence the mechanism works, the same "adopted, not just configured" bar every other node in this tree holds itself to. Mirrors `phpstan-level-0`'s own bar (an empty baseline, not zero errors project-wide): a low, deliberately incomplete threshold that unlocks the mechanism without demanding the full migration up front. (2) **Autoloader wired in:** the target's **Composition root** (`CONTEXT.md`) — or every **Entry point** individually when the target has none — contains a `require`/`include` resolving to `vendor/autoload.php`. A target with no detectable entry points at all (e.g. a pure library) is vacuously fulfilled on this second criterion — nothing to wire.
- **MR scope:** declare the `autoload.psr-4` mapping (root namespace, base directory) in `composer.json`, migrate **exactly one** real file as proof the mapping actually works (namespace it, move it into the mapped directory if it isn't already there, update its one call site), **and** wire `require_once`/`include_once` of `vendor/autoload.php` into the composition root (or every entry point that doesn't converge on one). Deliberately not "migrate every file" — see Purpose above for why the rest is left to `structural-scan`, not this node; the wiring step doesn't touch or remove any existing manual `require_once` for a not-yet-namespaced file, it only adds the autoloader alongside them so *new* code never needs another one.
- **Required parent:** `composer` (`composer.md`) — a PSR-4 mapping is literally a field inside `composer.json`; impossible without it. `required`, not `recommended`: a target that rejected `composer` outright (no Composer at all) can never fulfil this node either, so it must wait on `composer` being *fulfilled*, not merely *decided*.

## Autoloader wiring: stop the bleeding, not a full migration

The wiring step exists because proving the mapping mechanism works on one file was never the same as
the target's own request-time code actually loading classes through it — every entry point could
otherwise keep accumulating manual `require_once` calls indefinitely, since nothing ever wired
`vendor/autoload.php` into the runtime loading path. That gap is a real, confirmed defect class: a
target repo that added a new class but forgot to add it to its composition root's own manual require
list, invisible to any test suite that itself loads classes through the (already-working) autoloader
rather than through that same manual list, caught only by a human clicking through a live instance.

This step deliberately only stops the bleeding going forward — it does not retire any existing manual
`require_once` for a file that isn't PSR-4-migrated yet, and it does not turn "every file eventually
migrated" into a tracked goal of this node (that stays `structural-scan`'s own incremental job,
unchanged). Once wired, new code never needs another manual require line; existing ones simply
coexist with the autoloader until `structural-scan`'s own later work reaches them. Expected hygiene
for whichever future MR does reach one: also drop that file's own now-redundant require line from
wherever it was required — cheap, obviously correct, and keeps the composition root's own require list
from becoming a second, stale source of truth nobody trusts. Not itself checked or tracked by this
node.

## Downstream effects once fulfilled

- **`phpunit.md`'s `tests/Unit/` namespace** switches from independently re-deriving a prefix from `composer.json`'s `name` field to reading this node's own declared root namespace instead (`<app-root-namespace>\Tests\Unit\`) — one source of truth instead of two that could drift apart. Falls back to the `name`-derived prefix exactly as before when this node isn't fulfilled yet.
- **`phpstan.md`'s `paths` resolution** needs no change — it already reads `autoload`/`autoload-dev` directly and only falls back to `src` when nothing is declared; that fallback simply stops triggering once this node adds a real `autoload` section.
- **`php-structural-scan`'s resolved-gate** gains this node as one of its eleven leaves (`php-tooling-tree.md`'s edge table) — structural work waits until it's *decided* (fulfilled at the bar above, or explicitly rejected), the same way every other convention/check in that leaf set already gates structural work, on the reasoning that agent-driven structural changes are safer once the codebase's own organizational conventions are settled.
