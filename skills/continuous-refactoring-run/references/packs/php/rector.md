# Rector

The recommended Tool for the Role Automated Refactoring in the PHP Pack. One file for the whole family: the Stages point at each other for their caveats. The Stages are `rector-php-set`, `rector-dead-code`, `rector-code-quality`, `rector-phpunit-set` and `rector-type-coverage`. Every Stage is adopted in levels, one merge request per level, and keeps PHPStan green by shrinking the baseline within the same merge requests.

**Why this order.**

- **Rector PHP Set** is the hub: it needs the Role Static Analysis filled, by PHPStan or by Psalm, so Rector's rewrites are checked by an analyser. Dead Code and Code Quality require it, so they read which static-analysis path was chosen through it.
- **Style first.** Every Rector Stage waits until the Role Code Style is decided, so Rector's rewrites land on already-styled code. Whichever Tool fills it releases them: PHP CS Fixer with its adoption (`php-cs-fixer-adoption`), or a recognized Tool such as Pint, ECS or PHP_CodeSniffer. They do not wait for `php-cs-fixer-rollout`: rules still being taken in path by path leave parts of the code unstyled for a while. A rejected PHP CS Fixer releases them; they just never get styled output.
- **Type Coverage** waits until Roave Backward Compatibility Check is decided (`roave-bc-check.md`): on a target with a SemVer promise the check is in place before the rewrites that can break a subclass in another repository. It waits until Dead Code and Code Quality are decided (type-coverage rewrites touch messier code if dead code is not removed and control flow not flattened first) and until PHPStan Level 3 is decided (without strict analysis its rewrites are hard to review). Level 3 was judged strict enough for reviewable rewrites and stays the threshold although the chain reaches level 10. Any of these rejected instead of fulfilled still releases it; it just goes in without that benefit. It requires only Composer: in principle it could become proposable with Dead Code and Code Quality rejected and PHP Set never touched.
- **PHPStan waits for two of them.** PHPStan Level 4 waits until Dead Code is decided and Level 5 until Type Coverage is (`phpstan.md`, *Why this order*): the two Tools are worked side by side, and these rewrites shrink the baseline the level would otherwise fix by hand.
- **PHPUnit Set** rewrites PHPUnit-specific code, so it requires PHPUnit (or Pest, which the `phpunit` Stage recognizes) adopted first, and waits until Code Quality and Code Style are decided. It is a Guardrails Stage: it touches only test code, mechanically, and a conflict with structural work is resolved by running Rector again, so the Safety Net does not wait for it.
### `rector-php-set`

- **Purpose:** adopt Rector's own PHP-version-targeted rule set, the common gate the other Rector rule-set Stages wait on. A versioned PHP-upgrade rule set, such as `LevelSetList::up_to_php_8x`, up to the PHP floor the target declares and never above it: `config.platform.php` where it is set, otherwise the lowest version `require.php` allows. `withPhpSets()` without an argument reads that floor from `composer.json`. A set above the floor would make the code need a newer PHP than the project promises, a **Floor raise** (`CONTEXT.md`), which is a product decision and never a Stage's.
- **Fulfilment check:** the PHP-version rule set is enabled in `rector.php` / `rector.neon` at the level of the declared floor and fully applied, with no remaining rule findings. A level below the floor is not fulfilled. When there is no `composer.json`, or the floor cannot be read, the Stage is fulfilled at any level that is fully applied.
- **MR scope:** adopted in levels, one merge request per PHP version up to the floor; keeps PHPStan green by shrinking the baseline within the same merge requests (the same shape as `rector-dead-code`). Never edits `require.php` or `config.platform.php`.
- **Re-triggering:** the floor is a moving target. When a human raises it later, the Stage is unfulfilled again, and a scan the call asks for, or Housekeeping's re-check of the tooling Tracks, offers a ticket for the next level.
- **Code already above the floor:** code that needed a newer PHP than declared before the suite came is not this Stage's to fix. Whoever notices it proposes an ordinary ticket, because raising the floor or lowering the code is a product decision.

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

- **Purpose:** raise declared type coverage progressively. Uses Rector's typing suites, or the BC-safe path below.
- **Two paths.** Adding a parameter or return type to a method a class outside the repository may override
  breaks that class. Read the target's **BC promise** (`../../refactoring-operations.md`):
  - **The promise covers extending and overriding non-final classes and methods** — the usual case for a
    package — or it is not settled yet → the BC-safe path: `art4/rector-bc-library` as a dev dependency,
    Rector's own type-declaration set switched off (`withPreparedSets(typeDeclarations: false)`) and
    `Art4\RectorBcLibrary\Set::BC_TYPE_DECLARATION` in its place; for adoption in levels
    `Set::withTypeCoverageLevel(n)` instead of Rector's `withTypeCoverageLevel()`. Its guards skip a change
    to a public or protected member of a non-final class. The Rector versions it supports are in its
    README; check them before adding it.
  - **No promise, or one that leaves extending non-final classes out** → Rector's own typing
    suites.
- **Fulfilment check:** the typing suites of the path in use are enabled and fully applied at the agreed
  coverage degree. A target that uses the BC-safe path without needing it, or the other way round, is
  still fulfilled; the path matters for what the next level adds.
- **MR scope:** adopted in levels, one merge request per level; keeps PHPStan green via baseline shrinking.
  The first merge request on the BC-safe path names in its description why that path was taken.
