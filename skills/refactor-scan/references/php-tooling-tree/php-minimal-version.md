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
  from the gap this node closes. Also contribute this node's `Housekeeping` line (below) to the Refactoring
  Notes' `housekeeping-template.md`, creating that file fresh if it doesn't exist yet
  (`skills/continuous-housekeeping/references/template-file-format.md`) — **except** when this node is
  already fulfilled the very first time it's evaluated (no delivering MR of its own ever runs): then
  `loop-config`'s own first MR contributes the line instead, so the target never permanently misses out on
  it just because the floor happened to be sufficient from day one (see `loop-config.md`'s own entry).
- **Housekeeping:** check whether a newer PHP patch/minor release exists for the declared floor
  (`_current_php_floor`) and update it if so — a distinct concern from this node's own Fulfilment check,
  which only asks whether the floor is *correct* (high enough for what the tree needs), not whether it's
  *current* (the newest release of the same line).
- **Re-triggering:** this fulfilment check is a comparison against a moving target, not a one-time artefact
  check — it can flip back to unfulfilled if a later tool raises its minimum, or a new quality-tooling CI
  job tests a higher version, without any special mechanism (every fulfilment check here is already
  re-derived fresh from live repo state each pass). Not retroactive: an already-decided `rector-php-set`
  (`rector.md`) candidate is unaffected, only still-open proposals are held back again. Elsewhere in this
  tree's own design discussions, the separate `continuous-housekeeping` skill (triggered on its own fixed
  cadence, `skills/continuous-housekeeping/SKILL.md`) is the other, time-driven — not fact-driven — case of
  a check that can flip back to "due" after being satisfied.
