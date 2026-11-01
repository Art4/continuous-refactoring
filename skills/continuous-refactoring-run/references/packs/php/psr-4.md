# PSR-4 Autoloading

The Tool for the Role Autoloading in the PHP Pack. Not a runnable tool: a `composer.json` autoload declaration plus a namespace convention, the same shape as `.editorconfig`.

**Why this order.** It needs `composer`, fulfilled: a PSR-4 mapping is a field inside `composer.json`, and a target that rejected Composer outright can never fulfil this Stage either.

### `psr-4`

- **Purpose:** give the app's own source code a real PSR-4 namespace mapping. Distinct from the two incidental appearances of PSR-4 elsewhere, the `tests/Unit/` layout in `phpunit.md` and the `paths` resolution in `phpstan.md`: neither asks whether the app's own source has a real, working PSR-4 mapping as an adoptable, checkable step. The Stage is deliberately narrow: it adopts the *mechanism*, not a full migration of every file. A flat, unnamespaced legacy codebase (every file at the repo root, no namespace, `require`d by path) would otherwise turn "adopt PSR-4" into one large, disruptive merge request. Once it is fulfilled, every remaining un-namespaced file is an ordinary friction signal for the agent-driven structural work to migrate incrementally; the Stage itself does not own or track that.
- **Fulfilment check:** two criteria, both required.
  1. **Mechanism proven.** `composer.json`'s `autoload.psr-4` section declares at least one namespace prefix mapped to a real directory, **and** at least one `.php` file under that directory carries a `namespace` declaration matching the mapped prefix. A declaration alone is a claim, not evidence the mechanism works. The bar is deliberately low and incomplete, like an empty PHPStan baseline rather than zero errors project-wide: it unlocks the mechanism without demanding the full migration up front.
  2. **Autoloader wired in.** The target's **Composition root** (`CONTEXT.md`), or every **Entry point** individually when the target has none, contains a `require` / `include` resolving to `vendor/autoload.php`. A target with no detectable entry points (a pure library) is vacuously fulfilled on this criterion.

  Finding the Composition root and the Entry points: walk every `.php` file outside `vendor/`, `.git/`, any `tests` directory and the PSR-4-mapped namespace directories (already-autoloaded source is never an unwired entry-point candidate). Tooling-config files with a `.php` extension that are never request-time entry points are excluded too (`rector.php`, `.php-cs-fixer.php`, `.php-cs-fixer.dist.php`). For each remaining candidate, collect every file it reaches via `require` / `include` of the `__DIR__ . "/…"` shape (`__DIR__`-relative, with or without `_once`, with or without `../` segments). A candidate that no other candidate reaches is an **Entry point**. Among the Entry points, the one required by more than half of them is the **Composition root**. The Composition root and every Entry point that does not require it must each contain a `require` / `include` resolving to `vendor/autoload.php`.
- **MR scope:** declare the `autoload.psr-4` mapping (root namespace, base directory) in `composer.json`; migrate **exactly one** real file as proof the mapping works (namespace it, move it into the mapped directory if it is not already there, update its one call site); and wire `require_once` / `include_once` of `vendor/autoload.php` into the Composition root (or every Entry point that does not converge on one). Deliberately not "migrate every file" (see Purpose). The wiring does not touch or remove any existing manual `require_once` for a not-yet-namespaced file; it adds the autoloader alongside them, so new code never needs another one.

## Autoloader wiring: stop the bleeding, not a full migration

Proving the mapping on one file is not the same as the target's request-time code loading classes through it: every entry point could keep accumulating manual `require_once` calls, since nothing wired `vendor/autoload.php` into the runtime loading path. That gap is a confirmed defect class: a class added without being added to the composition root's manual require list is invisible to a test suite that loads classes through the working autoloader, and is caught only by a human clicking through a live instance.

The wiring only stops the bleeding going forward. It does not retire existing manual `require_once` lines, and "every file eventually migrated" is not a tracked goal of the Stage. Once wired, new code never needs another manual require, and existing ones coexist with the autoloader until later structural work reaches them. Expected hygiene for a merge request that does reach one: also drop that file's now redundant require line, so the composition root's require list does not become a second, stale source of truth. The Stage does not check or track this.

## Judging flagged entry points

The check "does this candidate contain a `require` / `include` resolving to `vendor/autoload.php`" is blunt when done mechanically. It cannot tell a genuinely unwired application entry point from a script that never needed the autoloader, such as a generated CI or build helper under `scripts/`, `bin/` or `tools/` that never references the target's own namespace. This was caught once: the committed `scripts/check-coverage-floor.php`, a generic Clover XML reader with no application dependency, briefly made `psr-4` look unfulfilled on a target where the real class loading had not changed at all.

Sorting that out is a judgement call for whoever judges the Stage, in a scan or at a ticket's pick-up, never a mechanical verdict:

- **An agent is doing the reading** (the ordinary case): before treating flagged files as real, unaddressed work, look at each. One that is clearly not an application entry point (it never references the target's own PSR-4 root namespace, and its purpose is a dev, CI or build utility) is exempt. A file that is ambiguous, or does reference the app's own classes, is real unwired work.
- **No agent reading it** (a purely mechanical walk): no exemption applies. The raw result stands, a possible over-report until an agent reviews it.

## Downstream effects once fulfilled

- **`phpunit.md`'s `tests/Unit/` namespace** is read from this Stage's declared root namespace (`<app-root-namespace>\Tests\Unit\`) instead of being derived again from `composer.json`'s `name` field: one source instead of two that could drift apart. Without this Stage fulfilled, the `name`-derived prefix applies.
- **`phpstan.md`'s `paths` resolution** needs no change: it reads `autoload` / `autoload-dev` directly and falls back to `src` only when nothing is declared, and that fallback stops triggering once this Stage adds a real `autoload` section.
