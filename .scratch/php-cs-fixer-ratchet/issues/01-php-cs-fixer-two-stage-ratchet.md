# 01 — PHP CS Fixer: adoption Stage plus a rollout Stage that takes rules and paths in, in reviewable parts

Type: task
Status: open
Priority: normal

**Goal:** a target with 1000+ PHP files can be brought to a code style in merge requests a person can
review. Today the Stage is one step ("the dependency, the config and one formatting pass") and has no
answer to a formatting pass that touches hundreds of files.

## State today

- `skills/continuous-refactoring/references/packs/php/php-cs-fixer.md`: one Stage, `php-cs-fixer`
  (`requires: composer`, `after: editorconfig`). Fulfilment check: dependency, committed config, zero
  diffs locally. MR scope: dependency, config, one formatting pass. No Ratchet, no CI gate, no preset named.
- Every Rector Stage has `after: php-cs-fixer` (`recommended` edge, gates until the parent is decided:
  fulfilled or rejected), so Rector waits for a Stage that, on a big target, would take many merge requests.
- Reviewability is generic only: `design-point.md`, *Planning a tooling ticket* (size estimate, cut into
  parts) and `principles.md`, *A merge request a person can review*. Nothing says how to cut a style fixer.
- `pack.json` says `min_runtime: php 5.3`: by `tooling-model.md` the oldest runtime any version of the Tool
  ever ran on, so not stale.

## Design (settled in discussion)

### Two Stages

- **`php-cs-fixer` (adoption).** Dependency, main config, the CI job once `ci-runner` is fulfilled, and the
  first rules taken in (below). Keeps `requires: composer`, `after: editorconfig`. The Rector `after` edges
  stay on this Stage, so Rector is released once adoption is decided, not when the last file is formatted.
  Rector then runs on partly styled code; accepted.
  - Rules are taken in as for PHPMD (*Taking in a rule*): first those with no findings, then those with the
    fewest, while each rule's commit stays checkable by one pattern (`principles.md`, *A merge request a
    person can review*). The tool's own formatting run is one commit per rule. The first rule whose commit
    is no longer checkable that way, and every rule after it, stays off with `Not yet:` and belongs to the
    rollout Stage. So the boundary between the Stages is where the first merge request is full, not a fixed line.
  - Steps, one commit each: dependency and main config; extra rules (proposal); rules with no findings; rules
    with few findings, each with its formatting run; CI job; `php -l` on the floor PHP as Done-when.
  - Finding the rules that fail: one `check --dry-run --format=json` with the full preset lists the applied
    fixers per file, so the per-rule file count falls out of one run (the `appliedFixers` field is from
    memory, not yet verified).
  - Fulfilment check: dependency installed, main config committed with the pinned preset (or the target's
    own), `check` reports zero diffs, every rule switched off carries `Not yet:` or `Declined:`, and once
    `ci-runner` is fulfilled a CI job runs `check`.
  - An existing config with rules switched off and no marker is the target's own decision (as PHPMD's rule
    sets): accepted, never proposed again. A target that already runs `php-cs-fixer` clean thus has both
    Stages fulfilled at the first evaluation.
  - Housekeeping line: look for a newer PER-CS version than the pinned one (the preset is pinned, so a
    newer one never arrives by itself); if there is one, switch the pinned preset and set the rules that now
    report findings to `Not yet:`. The rollout Stage is then unfulfilled again and is worked as usual.
- **Rollout Stage (name: `php-cs-fixer-rollout`, Track Guardrails).** Takes in every `Not yet:` rule.
  `requires: php-cs-fixer`, `after: []`. In Guardrails, not Safety Net, so structural work does not wait for
  the last file to be formatted; an occasional merge conflict with a structural merge request is resolved
  by running the fixer again. Fulfilled when no `Not yet:` marker and no rollout file is left. Stays open across many merge
  requests, like the PHPStan baseline ticket; each run plans the next part. The name avoids "ratchet", which
  in `tooling-model.md` is a property of a Tool; this Stage carries it out.

### Preset

- Pin the versioned name, `@PER-CS3x0` (the dotted `@PER-CS3.0` is deprecated). Never `@PER-CS` (floats to
  the newest version, so a fixer update moves the target) and never `@auto` (floats, and includes the
  `@PHPxMigration` sets, which rewrite code).
- If the target already has a config with a preset, that preset is the target (the project's choice).
- The preset stands in the main config **from the first merge request**, with the rules not yet taken in
  switched off below it as `'<rule>' => false`:

  ```php
  '@PER-CS3x0' => true,
  'array_syntax' => false, // Not yet: ...
  'ordered_imports' => false, // Declined: ...
  ```

  The config reads as the end state, the markers are a shrinking list, and the last step of a rule is only
  deleting its `false` line. The alternative, listing the preset's rules one by one and switching to the
  preset at the end, makes the config unreadable and the last merge request a big bang.
- `:risky` sets are out of scope for now. `@PHPxMigration` sets stay out: code conversions are Rector's.

### Extra rules, declinable

- The plan proposes the preset plus extra rules from a default list in the Tool's `details` file. None is
  risky, none is in `@PER-CS3x0`, none rewrites code (Rector's), touches PHPDoc content (PHPStan's) or
  overlaps PHPMD, none depends on a PHP version. Confirmed list (`method_chaining_indentation` was
  declined: by its own description it does not support mixed indentation):
  - `no_unused_imports`, `single_quote`
  - Casing: `native_function_casing`, `magic_constant_casing`, `magic_method_casing`,
    `class_reference_name_casing`, `native_type_declaration_casing`, `integer_literal_case`
  - Whitespace: `whitespace_after_comma_in_array`, `no_whitespace_before_comma_in_array`,
    `trim_array_spaces`, `no_whitespace_in_empty_array`, `no_trailing_comma_in_singleline`,
    `no_multiline_whitespace_around_double_arrow`, `no_spaces_around_offset`,
    `object_operator_without_whitespace`, `no_singleline_whitespace_before_semicolons`,
    `space_after_semicolon`, `type_declaration_spaces`, `single_line_comment_spacing`, `include`,
    `no_leading_namespace_whitespace`
  - Empty: `no_empty_statement`, `no_empty_comment`, `no_empty_phpdoc`
  - PHPDoc form: `phpdoc_indent`, `phpdoc_trim`, `phpdoc_trim_consecutive_blank_line_separation`,
    `no_blank_lines_after_phpdoc`, `phpdoc_single_line_var_spacing`, `phpdoc_types`, `phpdoc_scalar`
- Left out on purpose: Rector's ground (`no_useless_else`, `simplified_if_return`,
  `ternary_to_null_coalescing`, `protected_to_private`, `combine_consecutive_*`, `no_useless_return`,
  `lambda_not_used_import`, `php_unit_*`), PHPStan-relevant (`no_superfluous_phpdoc_tags`,
  `phpdoc_to_comment`), taste (`yoda_style`, `phpdoc_align`, `phpdoc_summary`, `single_line_throw`,
  `blank_line_before_statement`, `global_namespace_import`), version-bound (`octal_notation`,
  `numeric_literal_separator`, `stringable_for_to_string`).
- Note: Rector can also remove unused imports (`withImportNames(removeUnusedImports: true)`); no hard
  collision, both would do the same.
- Extra rules are taken in like preset rules (no findings first, then fewest, the rest `Not yet:`).
- A declined rule is written `'<rule>' => false` with a `Declined: <reason>` comment. Only a human
  declines. Fulfilment accepts `Declined:`, not `Not yet:`.
- Interactive: a question to the human. Autonomous: the proposal is the default, named in the merge request
  description; the reviewer declines per comment.

### PHP version

- The agent reads the floor itself (`config.platform.php`, `require-dev.php`, `require.php` of
  `composer.json`) and proposes the PER version and any overrides.
- The fixer reads `composer.json` only through `@auto` (`ComposerJsonReader`: `config.platform.php`, then
  `require-dev.php`, `require.php`, minimum of the constraint). A pinned preset gets no adjustment.
- It does matter: with `require.php: ^7.4` and `@PER-CS3x0`, the fixer added a trailing comma to a
  multiline parameter list, a parse error before PHP 8.0. Overriding
  `trailing_comma_in_multiline` with `elements: arguments, array_destructuring, arrays` (no `parameters`)
  avoided it. Other rules were not checked.
- Done-when includes a `php -l` run on the floor PHP over the changed files. The fixer itself should run on
  the floor PHP too; it warns when it does not.

### Cutting: one rule at a time, a rollout file

Worked example: `array_syntax` (short arrays), part of the preset, hits several hundred files.

- **Main config** (`.php-cs-fixer.dist.php`): preset, **all** paths. Rules rolled out everywhere are on;
  rules in progress or not yet taken in are `false` with `Not yet:`.
- **Rollout config** (`.php-cs-fixer.rollout.php`, fixed name): only the rule in progress, a Finder over the
  paths already migrated. The rule is named inside the file, not in its name. Tried with two config files
  and `--config`: they run independently. The fixer discovers only `.php-cs-fixer.php` and
  `.php-cs-fixer.dist.php` by itself, so this file is always passed with `--config`.
- **CI** runs the main config, and the rollout config where the file exists.
- Sequence: adoption MR with the rule `false`; then one MR per directory step (or file group for a big
  directory): widen the rollout Finder, commit the tool's formatting run by itself; last MR: the Finder
  covers everything, the rollout file is deleted and the rule's `false` is removed from main. The next rule
  gets a new rollout file.
- Why not narrow the main Finder: paths dropped from main would lose every rule already rolled out.
- Only one rollout file at a time (so no rule name in the file name); a later run finds it and continues.
  Several tiny rules with few findings may share it.
- The rollout Stage's ticket is "PHP CS Fixer: take in the remaining rules", shaped like a baseline ticket
  (PHPMD's "take in the remaining rules" is the model): open across many merge requests, each run plans the
  next part, merge requests deliver a part and carry no closing reference. `design-point.md`, *Planning a
  baseline ticket*, gets a paragraph for it, like PHPMD's. It is built by the tooling rule: the fixer's run
  is one commit with nothing typed by hand.
- The `Not yet:` comment carries the number of files the last measurement counted, as PHPMD's does:
  `// Not yet: 212 files, rolled out via .php-cs-fixer.rollout.php`.
- The rollout file's existence is the marker: it keeps the rollout Stage unfulfilled, whoever created it.
- The `Not yet:` comment of a rule in progress names the rollout file's path, so a later run finds it
  wherever it lies: `'array_syntax' => false, // Not yet: rolled out via .php-cs-fixer.rollout.php`.
  A rule with no rollout running carries `Not yet:` without a path.
- File names and places (main config, rollout file, cache files) are defaults. The plan or the target may
  set others; an existing config of the target always wins. Each config gets its own cache file, all of
  them in `.gitignore`.
- Path steps go from the least recently changed directories to the most (git history), to keep merge
  conflicts with parallel work low.
- When the floor PHP is not available for `php -l`, the run does not stop: the overrides against known
  version traps stand in, and the merge request says the floor was not checked.
- Ordering of rules: fewest findings first (dry run), stopping at the first rule whose commit a reviewer
  could not check by one pattern, as for PHPMD (*Taking in a rule*). Path steps are sized by the agent's
  judgment, no fixed threshold.

## Open points

None left after grilling.

## Decided

- Two Stages; Rector edges stay on adoption (the first merge request releases Rector).
- Stage 1 takes rules in like PHPMD does; the boundary to the rollout Stage is the first full merge request.
- Preset in main from the start, unfinished rules `false` with `Not yet:`; declined ones `Declined:`.
- One rollout file at a time, fixed name `.php-cs-fixer.rollout.php`; Stage name `php-cs-fixer-rollout`.
- An existing config's switched-off rules without marker are the target's choice.
- Housekeeping line: look for a newer PER-CS version.
- `:risky` and migration sets stay out; the agent checks the PHP floor and proposes the PER version.
- Extra rules: the list above; only a human declines.
- A hand-made rollout file counts as the marker; `Not yet:` names its path.
- File names and places are defaults; the plan or the target may set others.
- `.git-blame-ignore-revs`: left out.
- Floor PHP not available: overrides stand in, the merge request names it.
- Path steps: coldest directories first.
- Built as one ticket, one PR.
- Rollout Stage in Guardrails; its ticket is baseline-shaped, planned like PHPMD's remaining rules.
- `Not yet:` carries the file count of the last measurement.
- Housekeeping line also switches to a newer PER-CS and sets new failing rules to `Not yet:`.
- No new `CONTEXT.md` terms: rollout file, `Not yet:`, `Declined:` stay Tool conventions in the `details`
  files until a third Tool uses the pattern.

## Verified facts

Checked 2026-10-20 against PHP CS Fixer 3.95.27 on PHP 8.3 (throwaway install, not part of the repo):

- Current preset names: `@PER-CS3x0`, `@PER-CS2x0`, `@PER-CS1x0`, `@PER-CS` (floating) and their `:risky`
  variants; the dotted names are deprecated. `@PSR12` is not deprecated.
- Fixer `composer.json` requires PHP `^7.4 || ^8.0`.
- `@PER-CS3x0` includes `array_syntax` (short): the main run reported `array(1, 2)` as fixable.
- Two config files with `--config` work side by side.
- `check --format=json` lists `appliedFixers` per file only with `-v`.
- `ordered_imports` is already part of `@PER-CS3x0`.

## To change when built

`php-cs-fixer.md` (two Stages, preset, extra rules, markers, rollout file, Housekeeping line), `pack.json`
(second Stage, edges), `design-point.md` (*Planning a baseline ticket* paragraph), the docs `AGENTS.md`
lists for a skill change (`docs/playbooks/tracks.md`, `docs/FAQ.md` for "why two Stages"; no `CONTEXT.md`
change), a `.changelog.d/` fragment, and tests in `scripts/`. `pint.md` and `ecs.md` stay as they are.

## Comments

> **2026-10-21:** Design grilled with the user in two rounds; every decision is under *Decided*.
> Follow-up idea outside this ticket: split PHPMD's adoption into two Stages the same way.
