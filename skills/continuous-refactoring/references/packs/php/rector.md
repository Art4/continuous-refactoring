# Rector

The recommended Tool for the Role Automated Refactoring in the PHP Pack. One file for the whole family: the Stages point at each other for their caveats. The Stages are `rector-php-set`, `rector-dead-code`, `rector-code-quality`, `rector-phpunit-set` and `rector-type-coverage`. Every Stage is adopted in levels, one merge request per level, and keeps PHPStan green by shrinking the baseline within the same merge requests.

**Why this order.**

- **Rector PHP Set** is the hub: it needs the Role Static Analysis filled, by PHPStan or by Psalm, so Rector's rewrites are checked by an analyser. Dead Code and Code Quality require it, so they read which static-analysis path was chosen through it.
- **Style first.** Every Rector Stage except PHPUnit Set waits until PHP CS Fixer's adoption (`php-cs-fixer-adoption`) is decided (fulfilled or rejected), so Rector's rewrites land on already-styled code. They do not wait for `php-cs-fixer-rollout`: rules still being taken in path by path leave parts of the code unstyled for a while. A rejected PHP CS Fixer releases them; they just never get styled output. A target on Pint or ECS has PHP CS Fixer out, which holds nobody back.
- **Type Coverage** waits until Dead Code and Code Quality are decided (type-coverage rewrites touch messier code if dead code is not removed and control flow not flattened first) and until PHPStan Level 3 is decided (without strict analysis its rewrites are hard to review). Level 3 was judged strict enough for reviewable rewrites and stays the threshold although the chain reaches level 10. Any of these rejected instead of fulfilled still releases it; it just goes in without that benefit. It requires only Composer: in principle it could become proposable with Dead Code and Code Quality rejected and PHP Set never touched.
- **PHPUnit Set** rewrites PHPUnit-specific code, so it requires PHPUnit (or Pest, which the `phpunit` Stage recognizes) adopted first, and waits until Code Quality and PHP CS Fixer are decided.
- **PHP Version Floor** (`php-minimal-version.md`) requires PHP Set fulfilled, so the declared floor follows what the rewrites landed.

### `rector-php-set`

- **Purpose:** adopt Rector's own PHP-version-targeted rule set, the common gate the other Rector rule-set Stages wait on. A versioned PHP-upgrade rule set, such as `LevelSetList::up_to_php_8x`.
- **Fulfilment check:** the PHP-version rule set is enabled in `rector.php` / `rector.neon` and fully applied, with no remaining rule findings.
- **MR scope:** adopted in levels, one merge request per target PHP version bump; keeps PHPStan green by shrinking the baseline within the same merge requests (the same shape as `rector-dead-code`).

### `rector-dead-code`

- **Purpose:** remove dead code with rules whose changes are safe to review early. Uses Rector's dead-code suite.
- **Fulfilment check:** the dead-code suite is enabled and fully applied, with no remaining rule findings.
- **MR scope:** adopted in levels, one merge request per level; keeps PHPStan green by shrinking the baseline within the same merge requests.

### `rector-code-quality`

- **Purpose:** apply Rector's code-quality rewrites (readability and idiom improvements beyond dead-code removal), including flattening nested conditionals into early returns. Rector's own dedicated early-return rule set (`SetList::EARLY_RETURN`) ships empty upstream and its rules are part of this set, so early return is not a Stage of its own. Uses Rector's code-quality suite.
- **Fulfilment check:** the code-quality suite is enabled and fully applied, with no remaining rule findings.
- **MR scope:** adopted in levels, one merge request per level; keeps PHPStan green by shrinking the baseline within the same merge requests.

### `rector-phpunit-set`

- **Purpose:** modernize PHPUnit test code (assertion methods, annotations to attributes, …) via Rector's PHPUnit rule set.
- **Fulfilment check:** the PHPUnit suite is enabled and fully applied, with no remaining rule findings.
- **MR scope:** adopted in levels, one merge request per level.

### `rector-type-coverage`

- **Purpose:** raise declared type coverage progressively. Uses Rector's typing suites.
- **Fulfilment check:** the typing suites are enabled and fully applied at the agreed coverage degree.
- **MR scope:** adopted in levels, one merge request per level; keeps PHPStan green via baseline shrinking.
