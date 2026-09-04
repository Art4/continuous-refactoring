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

**Status:** done

- [x] `composer` is a `required` parent, not `recommended` as originally sketched — a `psr-4`
  mapping is literally a field inside `composer.json`, impossible without it; `recommended` would
  wrongly allow it to stay proposable even with `composer` rejected outright.
- [x] `Tool:` `none` — confirmed against the `.editorconfig` precedent ("plain-text convention
  file... not a runnable tool").
- [x] Fulfilment check settled at a deliberately **low** bar, mirroring `phpstan-level-0`'s empty
  baseline rather than demanding full-repo compliance: `autoload.psr-4` declared **and** at least
  one real file verifiably namespaced under it — declaration alone isn't enough (the same
  "adopted, not just configured" bar ticket 48 showed the tree needs). Full migration is
  deliberately **not** this node's job — every remaining file becomes ordinary `structural-scan`
  work instead, discovered incrementally like any other deepening.
- [x] MR scope, matching the above: declare the mapping + migrate exactly one file as proof, not
  every file.
- [x] `phpstan.md`'s `paths` resolution needs no change — already generic, the `src` fallback
  simply stops triggering once a real `autoload` section exists.
- [x] `phpunit.md`'s `tests/Unit/` namespace now derives from `psr-4`'s own declared root namespace
  once fulfilled (avoiding two sources of truth that could drift), falling back to the previous
  `composer.json` `name`-derivation otherwise.
- [x] `psr-4` **does** become a resolved-parent of `php-structural-scan` — a thirteenth leaf,
  gating structural work on a different basis than every other leaf (a code-organization
  convention, not a checking tool), but the same underlying reasoning: settled before agent-driven
  structural changes begin.
- [x] New ADR-0032. `tooling_tree.py` gains `_psr4_root_namespace`/`_has_verified_psr4_autoload` and
  a `detect_nodes()` entry; `PsrFourGateTests` added to `scripts/test_tooling_tree.py`; every
  `fixtures/php/*/expected/roadmap.json` regenerated against the real parser;
  `fixtures/php/php-clean/project/composer.json` gained a real `autoload.psr-4` section (its
  existing `src/Greeter.php` was already namespaced, just not wired up).
  `python3 -m unittest discover -s scripts -p 'test_*.py'` (247/247) and
  `python3 scripts/validate_skills.py` (same 5 pre-existing advisory warnings) both green.

## Comments

> **2026-09-04:** Filed from the `psr4-tooling-tree-node-idea` memory (raised 2026-09-04 during the
> `Art4/legacy-todo` reviewer-loop run), per the user's request to prepare "für später" ideas for
> fixing.

> **2026-09-04 (later):** Design settled via a `/grill-me` session (in German) — the last of the
> three "für später" tickets (48, 49, 50). Researched the existing `.editorconfig`/`phpstan-level-0`
> precedents directly rather than guessing at conventions. Corrected the originating memory's
> `composer`-as-`recommended` framing to `required`. Settled the node's biggest open question —
> full compliance vs. a low, mechanism-only bar — in favor of the low bar, deliberately deferring
> the actual file-by-file migration to ordinary structural-scan work rather than having this node
> pretend to own a potentially large, disruptive migration. Implemented in the same session on
> branch `tickets/50-psr4-app-source-autoloading-node`.
