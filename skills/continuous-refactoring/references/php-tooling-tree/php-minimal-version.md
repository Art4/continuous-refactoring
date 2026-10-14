# `php-minimal-version`

Node on the PHP **tooling tree** (`../php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **Floor correction**, **Floor raise**, **Breaking change**, **Guardrails**).

- **Name:** PHP Minimum Version
- **Tool:** none
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
  No third-party tool: the tree's own gap detection.
- **Fulfilment check:** `composer.json`'s declared PHP floor (`config.platform.php`
  if pinned, else `require.php`'s lower bound) is at least the PHP-version level `rector-php-set`
  (`rector.md`) has itself applied. The applied level is read from Rector's config at the repo root
  (`rector.php` or `rector.neon`); the specific constant is `LevelSetList::UP_TO_PHP_XY` (e.g.
  `UP_TO_PHP_82` → PHP 8.2). No level applied yet, or floor unknown (no `composer.json`, or
  neither `require.php` nor `config.platform.php` parses) — both count as fulfilled: nothing to
  correct in either case, same "unknown floor blocks nothing" convention `php_floor_precheck()` itself
  uses.
- **Required parents:** `rector-php-set` (`rector.md`) — this node is only proposable once
  `rector-php-set` is genuinely *fulfilled* (a level truly landed), not merely decided; a rejected
  `rector-php-set` leaves this node permanently unproposable, matching the tree's ordinary
  required-parent-rejection-closes-everything-beneath-it convention, no special-casing needed. Nothing
  else the tree could raise as `require.php` short of the application's own code needing it —
  `rector-php-set`'s own landed syntax is the only legitimate signal. Additionally, `php-safety-net` — a
  **Guardrails** node: workable only once the Safety Net is fulfilled, kept alongside `rector-php-set`
  rather than replacing it, for the same rejection-must-permanently-close reasoning.
- **MR scope:** narrow — a `composer.json` `require.php` edit, plus the CI job that tests the app
  itself if a single unified job exists. No added verification step beyond the ordinary CI
  gate — `rector-php-set`'s own fulfilment check already means "fully applied, no remaining findings".
  Also add this node's `Housekeeping` line (below) to the target's Housekeeping template
  (`../implement-point.md`, *Slices every kind of ticket
  can have*). A node already
  fulfilled the very first time it's evaluated never gets a merge request of its own; its line then
  reaches the template through the Housekeeping Track
  (`../../../continuous-housekeeping/references/housekeeping-track.md`, step 4).
- **Housekeeping:** check whether a newer PHP patch or minor release exists for the PHP version
  `composer.json` declares as its minimum, and update the declared version if so.
- **Re-triggering:** this fulfilment check is a comparison against a moving target, not a one-time artefact
  check — `rector-php-set` re-leveling upward later (its own MR scope: "adopted in levels, one
  MR per target PHP version bump") can leave a previously-sufficient floor behind again. A scan the
  call asks for, or Housekeeping's re-check of the tooling Tracks, finds that and offers a ticket again.
- **Reversal:** a recorded rejection of this node that carries a PHP version as its blocker
  (`Blocker: PHP >= X.Y`, `../rejection.md`) is offered for reversal once the target's floor reaches that
  version, like any other node's.
