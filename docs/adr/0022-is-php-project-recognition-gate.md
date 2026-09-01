# `is-php-project`: a recognition gate for the PHP specialization, declared at the generic root

> Amends [ADR-0008](0008-generic-tool-tree-and-structural-scan-gate.md): the generic root's own claim to
> stay "language-neutral" now has one deliberate, bounded exception — one **recognition gate** per language
> specialization lives here, even though what a given gate detects is necessarily specific to that language.
> Continues [ADR-0021](0021-remaining-php-tooling-tree-nodes-extracted.md): `ci-runner`'s extracted file
> (`php-tooling-tree/ci-runner.md`) is folded back inline, moving with the node to `tooling-tree.md`.

`skills/refactor-scan/references/tooling_tree.py`'s `detect_nodes()` never checked whether a target repo is
a PHP project at all before evaluating the PHP tree — `composer`, `phpstan-level-0`, every leaf, all
computed unconditionally on every target. Most just come back `fulfilled: false` on a non-PHP repo, which
reads identically to "a real PHP project missing this tool." Run against a static HTML/CSS/JS site
(`continuous-refactoring.de`), this surfaced directly: `composer` got proposed as a real candidate on a
target with zero PHP anywhere.

Raised by the user together with the fix: a gate node, `is-php-project`, checking for a genuine PHP
signal before the Composer-stack subtree opens at all — the same shape a future `is-css-project`/
`is-js-project` would take for their own specializations. The user's own framing settled where it lives:
the gate's *role* — "should this specialization's tree even be reachable on this target" — is evaluated
fresh every pass regardless of which specializations exist, which makes it a generic-root concern even
though its own Fulfilment check is PHP-specific; `ci-runner`, previously a `php-tooling-tree.md` node, was
folded in alongside it for a related but distinct reason — its *content* was already language-neutral, only
referenced by the PHP tree externally (the same shape `editorconfig` already had) — so the PHP tree ends up
referencing exactly two externally-defined nodes (`editorconfig`, `ci-runner`) plus its own recognition
gate, and never `loop-config` directly.

## Decision

- New node `is-php-project`, declared in `skills/refactor-scan/references/tooling-tree.md` (the generic
  root), required parent of `loop-config`. Fulfilment check: `composer.json` (or `composer/composer.json`)
  present, **or** at least one `*.php` file anywhere in the tree, `vendor/` excluded — not
  `composer.json`-only, so a PHP project without Composer yet can still open the tree that proposes
  adopting it. Re-derived fresh every pass — no separate mechanism needed for a target that only later
  becomes a PHP project to open the tree retroactively.
- `is-php-project` is a required (not `resolved`) parent, and — like `git` — goes in `tooling_tree.py`'s
  `_NEVER_PROPOSED`: a `required` parent's rejection never unblocks its children (unlike `resolved`), so a
  human ever filing `docs/refactoring/out-of-scope/is-php-project.md` would accomplish nothing leaving it
  unfulfilled doesn't already.
- `composer` and `php-minimal-version` re-parent from `loop-config` to `is-php-project` in
  `php-tooling-tree.md`'s edge table — the tree's existing ownership rule (an edge with one endpoint in a
  language tree belongs to that tree's edge table) applies exactly as it already did for
  `loop-config → composer`. `ci-runner` stays a **direct** `loop-config` child, deliberately not gated by
  `is-php-project`: a CI pipeline is useful regardless of which language specialization (if any) is active.
- `ci-runner` itself — node definition and its `loop-config` edge — moves from `php-tooling-tree.md` to
  `tooling-tree.md`, the same treatment `editorconfig` already had: genuinely language-neutral content,
  referenced externally by the PHP tree only for the PHP-specific edges hanging off it
  (`ci-runner → php-minimal-version`, `ci-runner → composer-audit`). Its extracted file
  (`php-tooling-tree/ci-runner.md`, ADR-0021) is deleted; the content folds back inline into
  `tooling-tree.md`, which — like `git`/`loop-config`/`editorconfig`/`structural-scan` before it — keeps
  every node inline rather than extracting.
- Net effect: `php-tooling-tree.md` now references exactly two externally-defined nodes
  (`editorconfig`, `ci-runner`) plus its own recognition gate (`is-php-project`) — `loop-config` itself no
  longer appears there at all, and the document's own node section begins with `is-php-project`.

## Considered Options

- **`is-php-project` lives in `php-tooling-tree.md`, only its `loop-config` edge declared generically.**
  The first design proposed here. Rejected by the user: a future `is-css-project`/`is-js-project` should be
  structurally identical, and keeping the node itself PHP-owned would mean each specialization inventing its
  own shape for the same recognition-gate role instead of one shared pattern at the root.
- **A `resolved` edge instead of `required`.** Rejected: `resolved` exists so a rejected leaf still unblocks
  its aggregation node — meaningful for a leaf a human actually decides to accept or reject. Nobody ever
  rejects "is this a PHP project"; it is a fact, not a decision, and `required`'s ordinary AND-semantics are
  exactly what's needed to hold the subtree closed.
- **`composer.json`-only Fulfilment check.** Rejected: would leave a PHP project that hasn't adopted
  Composer yet unable to open the tree — including the `composer` node itself, whose entire job is
  proposing that adoption.
- **Also gate `ci-runner` behind `is-php-project`.** Rejected: CI pipeline setup is language-agnostic value,
  independent of whether any particular language specialization ends up active.
- **Fix `php-structural-scan`'s `resolved`-gate blindness to required-ancestor closure in the same change**
  (see Consequences). Rejected/deferred: independent, larger surface — touches every future language's
  aggregation node, not just PHP recognition — tracked as a named follow-up instead of folded in here.

## Consequences

On a non-PHP target, `composer`/`php-minimal-version` and everything reachable only through them stay
permanently unproposed — `next`/`roadmap`/`withheld` never surface them — while `ci-runner`/`editorconfig`
(language-neutral) remain reachable as before. `tooling_tree.py` gains one new hardcoded detection helper
(`_has_php_files`) and one new `set_node` call in `detect_nodes()`; no change needed in `_is_unblocked`,
`next_candidates`, `roadmap`, or `withheld_candidates` — required-edge closure is already generic and
edge-table-driven. All 7 existing PHP fixtures regenerated (`fixtures/php/*/expected/roadmap.json`): no
step-count or reachability change in any of them (each already carries a real PHP signal), only a cosmetic
ordering shift — `ci-runner` now sorts ahead of `editorconfig` in the roadmap, since `tooling-tree.md`'s
edge table lists `is-php-project`/`ci-runner` before `editorconfig`. A new eighth fixture,
`fixtures/php/non-php-project/` (a static HTML/CSS/JS site, no PHP anywhere), demonstrates the gate closed;
added to the CI roadmap matrix (`.github/workflows/test-harness.yml`).

**Known gap, not fixed here:** `php-structural-scan`'s own `resolved` gate
(`skills/refactor-scan/references/php-tooling-tree.md`) checks each of its thirteen leaves for "fulfilled,
or explicitly rejected under `out-of-scope/`" — it does not understand a leaf permanently closed by an
unfulfilled `required` ancestor as a form of resolution. A leaf gated shut by `is-php-project` (e.g.
`composer-audit`) therefore counts as neither fulfilled nor rejected there; `structural-scan` cannot open
via the PHP path on a non-PHP target without a human filing all thirteen leaf-level rejections by hand. This
predates `is-php-project` (a target where a human rejected `composer` itself already hit the same wall,
since `composer`'s own children never even got proposed to reject) and is not worsened by it — tracked as a
follow-up for `_resolved_gate_status()` in `tooling_tree.py`, teaching it required-ancestor closure the way
`_is_effectively_rejected()` already has it for other purposes.

A future `is-css-project`/`is-js-project` follows this exact pattern — its own Fulfilment check, `required`
parent of `loop-config`, `_NEVER_PROPOSED`, gating its own specialization's first genuinely-specific nodes —
but needs its own new detection layer in `tooling_tree.py` (comparable in size to the ~250 lines of existing
PHP detection logic) and its own `<language>-tooling-tree.md`/`<language>-structural-scan` aggregation node
(ADR-0017's pattern, already designed to generalize); tracked as a follow-up ticket, not designed here.
