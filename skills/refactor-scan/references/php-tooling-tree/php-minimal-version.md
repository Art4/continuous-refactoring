# `php-minimal-version`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** PHP Minimum Version
- **Tool:** none — the tree's own gap detection, not a third-party tool.
- **Purpose:** detect a gap between `composer.json`'s declared PHP floor and what the tree actually needs,
  and propose raising the floor to close it. Motivating case: a target that stayed pinned to an old PHP
  version throughout, solving PHPStan/Rector's own version requirements by running them in a second,
  parallel higher-PHP container instead — nothing in the tree ever raised the floor mismatch itself as a
  candidate.
- **Fulfilment check:** `composer.json`'s declared PHP floor (`_current_php_floor` — `config.platform.php`
  if pinned, else `require.php`'s lower bound) is at least the maximum of: (a) the minimum-ever PHP version
  of any leaf `php_floor_precheck()` currently reports blocked, and (b) the highest PHP version tested by a
  CI job that invokes a quality tool (`vendor/bin/phpstan analyse`, `vendor/bin/psalm`,
  `vendor/bin/rector`, `vendor/bin/php-cs-fixer`) — not an arbitrary compatibility-matrix job that
  legitimately tests multiple PHP versions for unrelated reasons. Floor unknown (no `composer.json`, or
  neither `require.php` nor `config.platform.php` parses) counts as fulfilled — same convention
  `php_floor_precheck()` itself uses: nothing to recommend without a determinable floor.
- **MR scope:** narrow — raise `composer.json`'s `require.php` constraint, plus the CI job that tests the
  app itself if a single unified job exists. Explicitly out of scope: consolidating a separate
  tooling-only container/job into the app's own version, if the target has one — a distinct, later concern
  from the gap this node closes.
- **Re-triggering:** this fulfilment check is a comparison against a moving target, not a one-time artefact
  check — it can flip back to unfulfilled if a later tool raises its minimum, or a new quality-tooling CI
  job tests a higher version, without any special mechanism (every fulfilment check here is already
  re-derived fresh from live repo state each pass). Not retroactive: an already-decided `rector-php-set`
  (`rector.md`) candidate is unaffected, only still-open proposals are held back again. Elsewhere in this
  tree's own design discussions, a recurring `housekeeping` node (re-proposed on a fixed schedule) is the
  other, time-driven — not fact-driven — case of a fulfilment check that can flip back to false.
