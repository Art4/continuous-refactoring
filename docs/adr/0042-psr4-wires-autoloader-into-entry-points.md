# `psr-4` wires the autoloader into the target's entry points, not just proves the mechanism

## Context

`psr-4`'s own fulfilment check and MR scope have always been deliberately narrow: declare
`composer.json`'s `autoload.psr-4` mapping, migrate exactly one real file as proof the mechanism
works, leave the rest of the codebase's own migration to `structural-scan`'s slow, incremental
discovery. That narrowness was a genuine, considered design decision (a flat legacy codebase
shouldn't have to accept one large, disruptive MR to adopt PSR-4 at all) — but it left a gap nobody
had designed around: nothing in either `composer`'s or `psr-4`'s own scope ever touches how the
target's *own request-time code* actually loads classes. A target could fully adopt both nodes and
still load every class by hand, via manually maintained `require_once` lists, indefinitely.

That gap is a confirmed defect class, not a hypothetical: a target repo added a new class but forgot
to add it to its composition root's own manual require list. 126 green unit tests and full static
analysis never caught it — both load classes through the (already-working) Composer autoloader in
their own test bootstrap, an entirely different path from the one the real app actually uses at
request time. Only a human clicking through a live instance found it. The gap directly motivated
building a whole new end-to-end HTTP test suite as a compensating, after-the-fact detection control —
useful, but it only catches the mistake once it's already made; it doesn't change the habit that
causes it.

## Decision

`psr-4` gains a second fulfilment criterion, in addition to the existing "mapping declared and used"
bar: the target's **Composition root** — or every **Entry point** individually, when the target has
no single composition root — contains a `require`/`include` resolving to `vendor/autoload.php`. Two
new terms land in `CONTEXT.md`:

- **Entry point**: a `.php` file the runtime executes directly, never `require`d/`include`d by
  another file in the target's own source tree.
- **Composition root**: the one file, if any, more than half of the detected entry points directly
  require — recognized even when some entry points don't converge on it (those "stragglers" get wired
  individually alongside it, not treated as disqualifying the recognition).

**Scope: stop the bleeding, not a full migration.** The wiring step does not retire any existing
manual `require_once` for a file that isn't PSR-4-migrated yet, and does not turn "every file
eventually migrated" into a tracked goal of this node. Once wired, new code never needs another manual
require line — the defect class becomes structurally harder to reintroduce, not just easier to catch —
while existing manual requires simply coexist with the autoloader until `structural-scan`'s own later,
incremental work reaches them, exactly as `psr-4`'s original narrow-migration philosophy already
intended. Expected hygiene for whichever future migration does reach a given file: also drop that
file's own now-redundant require line. Not itself checked or tracked by this node — stated as
guidance, not a mechanical requirement.

**Lives in `psr-4`'s own node, not `composer`'s.** `vendor/autoload.php` exists the moment `composer
install` runs, before any PSR-4 mapping is declared — wiring it in that early would be free, but it
would also solve nothing yet: nothing of the target's own code is autoloadable until `psr-4` proves
the mechanism works on at least one file. `psr-4`'s own "migrate one file" step is also the first
point there's a real, working example for the wiring to actually matter for.

**Detection, concretely** (`tooling_tree.py`): entry-point search is scoped to every `.php` file
outside the PSR-4-mapped namespace directory, `vendor/`, and test directories — reusing a fact the
node already computes rather than a second directory-scoping rule — plus a small, explicit exclusion
list for known repo-root tooling-config scripts that happen to carry a `.php` extension (`rector.php`,
`.php-cs-fixer.php`/`.dist.php`) but are never a request-time entry point. The require/include graph
is read via the same conservative, single-shape approximation this tree's other filesystem-text
checks already use (`__DIR__ . "/Foo.php"`-style concatenation only, not a full parser). A target with
no detectable entry points at all (e.g. a pure library) is vacuously fulfilled on this criterion —
nothing to wire, the same convention this tree already uses for an undeterminable PHP floor.

**PHP-tree-specific**, not the generic root — the concrete mechanism (finding `vendor/autoload.php`,
PHP's own require/include semantics) is entirely Composer/PHP-specific, matching this suite's existing
precedent for not attempting a generic-tree shape before a second language specialization exists to
validate one against.

## Considered Options

- **Wire it into `composer`'s own node instead**, since `vendor/autoload.php` exists earlier. Rejected
  — wiring in an autoloader that can't yet load any of the target's own code doesn't close the gap
  this decision is about; the earlier trigger point buys nothing real.
- **A new, dedicated node** between `composer` and `psr-4`, or after `psr-4`. Rejected — the wiring
  step is a natural extension of "adopt the mechanism" (`psr-4`'s own existing Purpose), not a
  separate adoption decision; a new node would add ceremony without a corresponding new decision for a
  target to actually make.
- **Full migration as this ticket's own scope** — actively retiring every existing manual require as
  each file gets PSR-4-migrated, tracked to completion. Rejected — re-litigates `psr-4`'s already-
  settled incremental, non-disruptive philosophy for existing files; the stop-the-bleeding scope
  closes the actual defect class (a *new* file going missing from a manual list) without that.
- **Never introduce "Composition root" as its own term — always wire every entry point individually,
  even when they all happen to delegate to one shared file.** Considered during grilling; rejected —
  the distinction is load-bearing for detection (finding "do all entry points require the same one
  file" is a materially different, and materially cheaper, question than "wire every entry point
  separately"), and it names the exact place the confirmed defect class actually lived.
- **Require unanimous convergence for composition-root recognition** (every entry point, not just a
  majority). Rejected — a target with one legacy straggler entry point that doesn't delegate to the
  shared root shouldn't lose recognition of the root for everything else; the straggler is wired
  individually instead, on top of the root, not in place of it.

## Consequences

`tooling_tree.py`: new detection helpers (`_psr4_mapped_dirs`, `_entry_point_candidates`,
`_require_targets`, `_detect_entry_points`, `_autoloader_wired`) and `psr-4`'s own `set_node(...)`
call now AND the two criteria together. No edge-table changes — `psr-4`'s required parent and its
`resolved` contribution to `php-structural-scan` are unaffected; only its own internal fulfilment bar
widened. `psr-4.md` documents both criteria and the stop-the-bleeding scope explicitly. `CONTEXT.md`
gains **Entry point** and **Composition root**. None of this suite's own 8 PHP fixtures were affected
— none currently declare any real application entry point outside their mapped namespace directory
(only tooling-config scripts, already excluded), so all stayed vacuously fulfilled and needed no
fixture changes.
