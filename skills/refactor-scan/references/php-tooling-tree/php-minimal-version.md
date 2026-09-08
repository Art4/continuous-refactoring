# `php-minimal-version`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **Floor correction**, **Floor raise**, **Breaking change**).

- **Name:** PHP Minimum Version
- **Tool:** none — the tree's own gap detection, not a third-party tool.
- **Purpose:** a **Floor correction** only, never a **Floor raise** — `composer.json`'s declared PHP
  floor (`require.php`) genuinely understates what the codebase already contains once `rector-php-set`
  has landed a PHP-version rule set: the rewritten syntax needs that version to run, so declaring the
  floor is just telling the truth, not a behavior change. This node never proposes committing the
  application to a newer PHP than its own code currently needs — that would be a **Breaking change**
  (excludes any consumer still on a version between the old and new floor), out of scope for anything
  shipped under the refactor label. A `require-dev` tool's own PHP-version requirement (PHPStan,
  Rector, …) never drives this floor either: Composer's dependency resolution only needs the platform
  actually running `composer install` to satisfy a dev tool, never the package's own declared floor —
  so neither "a leaf tool needs a newer PHP" nor "CI happens to run quality tooling under a newer PHP
  image" is ever a legitimate signal here, independent of the breaking-change question.
- **Fulfilment check:** `composer.json`'s declared PHP floor (`_current_php_floor` — `config.platform.php`
  if pinned, else `require.php`'s lower bound) is at least the PHP-version level `rector-php-set`
  (`rector.md`) has itself applied. No level applied yet, or floor unknown (no `composer.json`, or
  neither `require.php` nor `config.platform.php` parses) — both count as fulfilled: nothing to
  correct in either case, same "unknown floor blocks nothing" convention `php_floor_precheck()` itself
  uses.
- **Required parent:** `rector-php-set` (`rector.md`) — this node is only proposable once
  `rector-php-set` is genuinely *fulfilled* (a level truly landed), not merely decided; a rejected
  `rector-php-set` leaves this node permanently unproposable, matching the tree's ordinary
  required-parent-rejection-closes-everything-beneath-it convention, no special-casing needed. Nothing
  else the tree could raise as `require.php` short of the application's own code needing it —
  `rector-php-set`'s own landed syntax is the only legitimate signal.
- **MR scope:** narrow — a `composer.json` `require.php` edit, plus the CI job that tests the app
  itself if a single unified job exists. No added verification step beyond the loop's own ordinary CI
  gate — `rector-php-set`'s own fulfilment check already means "fully applied, no remaining findings".
  Also contribute this node's `Housekeeping` line (below) to the Refactoring Notes'
  `housekeeping-template.md`, creating that file fresh if it doesn't exist yet
  (`skills/continuous-housekeeping/references/template-file-format.md`) — **except** when this node is
  already fulfilled the very first time it's evaluated (no delivering MR of its own ever runs): then
  `loop-config`'s own first MR contributes the line instead, so the target never permanently misses out on
  it just because the floor happened to be sufficient from day one (see `loop-config.md`'s own entry).
- **Housekeeping:** check whether a newer PHP patch/minor release exists for the declared floor
  (`_current_php_floor`) and update it if so — a distinct concern from this node's own Fulfilment check,
  which only asks whether the floor is *correct* (matches what `rector-php-set` has landed), not whether
  it's *current* (the newest release of the same line).
- **Re-triggering:** this fulfilment check is a comparison against a moving target, not a one-time artefact
  check — `rector-php-set` re-leveling upward in a later pass (its own MR scope: "adopted in levels, one
  MR per target PHP version bump") can leave a previously-sufficient floor behind again, without any
  special mechanism (every fulfilment check here is already re-derived fresh from live repo state each
  pass). Not retroactive: an already-decided candidate elsewhere in the tree is unaffected, only still-open
  proposals are held back again. Elsewhere in this tree's own design discussions, the separate
  `continuous-housekeeping` skill (triggered on its own fixed cadence,
  `skills/continuous-housekeeping/SKILL.md`) is the other, time-driven — not fact-driven — case of a
  check that can flip back to "due" after being satisfied.
- **`Blocked by: PHP >= X.Y.Z` reversal detection:** an out-of-scope rejection of this node written
  under a target's own history keeps reversing correctly if the floor it names is later satisfied (the
  mechanism is generic, not specific to how this node currently reaches that state). No path in this
  node's own design writes a new entry of this shape any more — a premature MR can no longer be
  proposed in the first place, the required-parent gate above does that job instead.
