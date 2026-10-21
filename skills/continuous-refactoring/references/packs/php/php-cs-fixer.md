# PHP CS Fixer

The recommended Tool for the Role Code Style in the PHP Pack. Laravel Pint (`pint.md`) and Easy Coding Standard (`ecs.md`) are recognized: on a target that runs either, the Role is filled, PHP CS Fixer is out and is not proposed. Two Stages: `php-cs-fixer-adoption` adopts the tool with the rules a first merge request can carry, `php-cs-fixer-rollout` takes in the rest, rule by rule and path by path.

**Why this order.** `php-cs-fixer-adoption` waits until `editorconfig` is decided, so the target's basic formatting conventions are settled before language-specific style rules arrive; a rejected `editorconfig` releases it. The Rector Stages wait until `php-cs-fixer-adoption` is decided, so Rector's rewrites land on styled code. They wait for the adoption only, not for the rollout: on a target of a thousand files the last rule may be many merge requests away, and Rector then runs on code that is partly styled. `php-cs-fixer-rollout` is a Guardrails Stage for the same reason, so structural work does not wait for the last file to be formatted; a merge conflict with a structural merge request is resolved by running the fixer again.

### `php-cs-fixer-adoption`

- **Purpose:** automated code style, so later Rector output lands styled.
- **Fulfilment check:** all of:
  - a dev dependency (`friendsofphp/php-cs-fixer` or `php-cs-fixer/php-cs-fixer`) is installed;
  - a config is committed (`.php-cs-fixer.php` or `.php-cs-fixer.dist.php`), naming a preset pinned to a version (*Preset*) or the target's own choice;
  - `vendor/bin/php-cs-fixer check` reports zero diffs with that config;
  - once `ci-runner` is fulfilled, a CI job runs `check` with it, and with the rollout file where there is one (*Taking in a rule*). With no CI yet, local adoption alone still fulfils the Stage.

  Rules switched off with `Not yet:` leave this Stage fulfilled; they are `php-cs-fixer-rollout`'s (*Rules switched off*).
- **An existing config.** A target that already runs PHP CS Fixer keeps its config: its preset is the target, and the rules it switches off are its own choice, accepted and never proposed again, as PHPMD's rule sets. A target that runs PHP CS Fixer clean thus has both Stages fulfilled at their first evaluation.
- **MR scope** of a fresh adoption, one commit each, every commit leaving `check` green:
  1. The dependency and the main config: the pinned preset, the version overrides (*PHP version*), the extra rules proposed (*Extra rules*), a Finder over every PHP path of the target outside `vendor/`, its own cache file, and that cache file in `.gitignore`. Every rule that reports findings (*Measuring*) is switched off with `Not yet:` and its count, including those the following commits take in.
  2. One commit per rule taken in, the rule with the fewest findings first: it deletes the rule's `false` line, and the tool's formatting run is in the same commit, with nothing typed by hand. Stop at the first rule whose commit a reviewer could no longer check by one pattern (`../../principles.md`, *A merge request a person can review*). That rule and every rule after it stay `Not yet:` and belong to `php-cs-fixer-rollout`. So the boundary between the two Stages is where the first merge request is full, not a fixed list. The plan names each rule's count and the rule where it stopped.
  3. Once `ci-runner` is fulfilled, the CI job.
  4. Also add the Housekeeping line below to the target's Housekeeping template (`../../implement-point.md`, *Slices every kind of ticket can have*), as a commit of its own before the changelog entry. A Stage already fulfilled the very first time it is evaluated never gets a merge request of its own; its line then reaches the template through the Housekeeping Track (`../../../../continuous-housekeeping/references/housekeeping-track.md`, step 4).
- **Done when** also holds `php -l` on the floor PHP over every file the formatting runs changed (*PHP version*).
- The merge request reads in its description the preset, each override with its reason, the extra rules proposed, and each rule left `Not yet:` with its count.

### `php-cs-fixer-rollout`

- **Purpose:** take in every rule the adoption left `Not yet:`, in merge requests a person can review.
- **Fulfilment check:** `php-cs-fixer-adoption` is fulfilled, the main config holds no `Not yet:`, and no rollout file exists (*Taking in a rule*), whoever created it.
- **Its ticket** is "PHP CS Fixer: take in the remaining rules", the shape of a baseline ticket: it stays open across many merge requests, each run plans the next part (`../../design-point.md`, *Planning a baseline ticket*), and each merge request delivers a part and carries no closing reference.
- **A part** is one path step of one rule (*Taking in a rule*). Several tiny rules may share a part.
- **MR scope** of a part: the rollout file widened by the part's paths, or created for the next rule, and the tool's formatting run, one commit with nothing typed by hand. The last part of a rule deletes the rollout file and the rule's `false` line in the main config instead.

### Preset

- A fresh adoption writes the newest PER-CS version by its pinned name, today `@PER-CS3x0` (`vendor/bin/php-cs-fixer list-sets`). Never the floating `@PER-CS`, which moves the target with a fixer update, and never `@auto`, which floats too and brings the `@PHPxMigration` sets that rewrite code. The dotted names (`@PER-CS3.0`) are deprecated.
- The preset stands in the main config from the first merge request, with the rules not taken in yet switched off below it:

  ```php
  '@PER-CS3x0' => true,
  'array_syntax' => false, // Not yet: 212 files, rolled out via .php-cs-fixer.rollout.php
  'no_unused_imports' => false, // Not yet: 31 files
  'single_quote' => false, // Declined: the team writes double quotes throughout
  ```

  The config reads as the end state, the markers are a shrinking list, and taking a rule in ends with deleting its line.
- The `:risky` sets and the `@PHPxMigration` sets are out of scope: code conversions are Rector's.

### Extra rules

The plan proposes, beside the preset, these rules. None is risky, none is in `@PER-CS3x0`, none depends on a PHP version, and none takes ground from another Tool: no rewrite of code (Rector), no PHPDoc content (PHPStan), no PHPMD rule.

- `no_unused_imports`, `single_quote`
- Casing: `native_function_casing`, `magic_constant_casing`, `magic_method_casing`, `class_reference_name_casing`, `native_type_declaration_casing`, `integer_literal_case`
- Whitespace: `whitespace_after_comma_in_array`, `no_whitespace_before_comma_in_array`, `trim_array_spaces`, `no_whitespace_in_empty_array`, `no_trailing_comma_in_singleline`, `no_multiline_whitespace_around_double_arrow`, `no_spaces_around_offset`, `object_operator_without_whitespace`, `no_singleline_whitespace_before_semicolons`, `space_after_semicolon`, `type_declaration_spaces`, `single_line_comment_spacing`, `include`, `no_leading_namespace_whitespace`
- Empty: `no_empty_statement`, `no_empty_comment`, `no_empty_phpdoc`
- PHPDoc form: `phpdoc_indent`, `phpdoc_trim`, `phpdoc_trim_consecutive_blank_line_separation`, `no_blank_lines_after_phpdoc`, `phpdoc_single_line_var_spacing`, `phpdoc_types`, `phpdoc_scalar`

Extra rules are taken in like the preset's: fewest findings first, the rest `Not yet:`. An interactive run puts the list to the human as a question; an autonomous run takes it as the default, names it in the merge request's description, and the reviewer declines a rule by comment. Rector can also remove unused imports; both would do the same, so there is no collision.

### PHP version

- The agent reads the target's PHP floor itself: `config.platform.php`, else `require-dev.php`, else `require.php` of `composer.json`, the lowest version the constraint allows. A pinned preset is not adjusted to it by the fixer.
- The floor matters: on a floor below PHP 8.0, `@PER-CS3x0` adds a trailing comma to multiline parameter lists, a parse error there. The config then overrides `trailing_comma_in_multiline` with `'elements' => ['arguments', 'array_destructuring', 'arrays']`, without `parameters`. Where the floor is lower than the preset suits, the plan proposes an older PER-CS version or further overrides, each with its reason.
- `php -l` on the floor PHP over the changed files is part of every `Done when` of both Stages. The fixer itself should run on the floor PHP too; it warns when it does not. Where the floor PHP is not available, the run does not stop: the overrides stand in, and the merge request says the floor was not checked.

### Rules switched off

- **`Not yet:`** — a rule the suite has not taken in yet, with the number of files the last measurement counted, and the rollout file's path while one is running for it: `// Not yet: 212 files, rolled out via .php-cs-fixer.rollout.php`. A later run finds the rollout file by it, wherever it lies.
- **`Declined:`** — a rule the target does not want, with the reason. Only a human declines; many findings are no reason, such a rule waits.
- **No marker** — a rule the target switched off itself: its own choice, accepted and never proposed again.

The fulfilment of `php-cs-fixer-adoption` accepts all three, that of `php-cs-fixer-rollout` no `Not yet:`.

### Taking in a rule

One rule at a time, through a second config beside the main one.

- **The main config** keeps the preset and every path. A rule in progress stays `false` there. Narrowing the main config's Finder is no way to cut: the paths left out would lose every rule already taken in.
- **The rollout file**, `.php-cs-fixer.rollout.php` by default: only the rule in progress, with the options the preset gives it (`vendor/bin/php-cs-fixer describe @PER-CS3x0 --expand`), and a Finder over the paths already done. It names the rule inside, not in its file name, since there is only one at a time. It has its own cache file, in `.gitignore`. The fixer finds only `.php-cs-fixer.php` and `.php-cs-fixer.dist.php` by itself, so the rollout file is always passed with `--config`:

  ```php
  <?php

  // Takes in array_syntax path by path; the main config switches it off until the Finder covers everything.
  return (new PhpCsFixer\Config())
      ->setRules(['array_syntax' => ['syntax' => 'short']])
      ->setCacheFile('.php-cs-fixer.rollout.cache')
      ->setFinder((new PhpCsFixer\Finder())->in(['lib/Legacy', 'src/Billing']));
  ```

- **The order of the rules:** the fewest files first, by a fresh measurement (*Measuring*).
- **The path steps:** the directories changed least recently first (`git log`), to keep merge conflicts with parallel work low; a big directory is cut into groups of files. The agent sizes each step by `../../principles.md`, *A merge request a person can review*; there is no fixed threshold.
- **The formatting run** of a part is the rollout file, then the main config, so the rules already on tidy what the rule left; both outputs go into one commit.
- **The last part** of a rule: its Finder would cover every path of the main config. The rollout file is deleted, the rule's `false` line in the main config with it, and the main config's run is the commit. The next rule gets a new rollout file.
- **CI** runs `check` with the main config, and with the rollout file wherever it exists.

**Names and places.** The main config's name, the rollout file's and the cache files' are defaults. The plan or the target may set others; a config the target already has always wins.

### Measuring

One run tells which rules report, and in how many files: a temporary config outside the target with the main config's preset, rules and Finder, every `Not yet:` rule switched on, run as `vendor/bin/php-cs-fixer check --config=<it> --using-cache=no --format=json -v`. With `-v`, every file of the report lists its `appliedFixers`; a rule's count is the number of files that list it. Nothing is written into the target.

### Housekeeping

- **Housekeeping:** look for a newer PER-CS version than the one the main config pins (`vendor/bin/php-cs-fixer list-sets` after `composer update`); a pinned preset never moves by itself. Where there is one, switch to it, measure, and set each rule that now reports findings to `false` with `Not yet:` and its count; only the config changes, never the code. `php-cs-fixer-rollout` is then unfulfilled again and its ticket is worked as usual. A target on a preset of its own choice is left on it.
