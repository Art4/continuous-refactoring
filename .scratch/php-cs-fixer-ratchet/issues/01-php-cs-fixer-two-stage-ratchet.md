# 01 — PHP CS Fixer: adoption Stage plus a Ratchet Stage that rolls rules and paths out in reviewable parts

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
- `pack.json` still says `min_runtime: php 5.3` for this Tool, which looks stale (see *Verified facts*).

## Design (settled in discussion)

### Two Stages

- **`php-cs-fixer` (adoption).** Dependency, main config with the pinned preset, every rule that is already
  green on the whole target, the CI job once `ci-runner` is fulfilled. Rules not yet taken in stay in the
  main config as `'<rule>' => false` with a `Not yet:` comment. Keeps `requires: composer`,
  `after: editorconfig`. The Rector `after` edges stay on this Stage, so Rector is released once adoption
  is decided, not when the last file is formatted. Rector then runs on partly styled code; accepted.
- **Ratchet Stage (name open, working name `php-cs-fixer-ratchet`).** Takes in every `Not yet:` rule.
  `requires: php-cs-fixer`, `after: []`. Fulfilled when no `Not yet:` marker and no staging file is left.
  Stays open across many merge requests, like the PHPStan baseline ticket; each run plans the next part.

### Preset

- Pin the versioned name, `@PER-CS3x0` (the dotted `@PER-CS3.0` is deprecated). Never `@PER-CS` (floats to
  the newest version, so a fixer update moves the target) and never `@auto` (floats, and includes the
  `@PHPxMigration` sets, which rewrite code).
- If the target already has a config with a preset, that preset is the target (the project's choice).
- `:risky` sets are out of scope for now. `@PHPxMigration` sets stay out: code conversions are Rector's.

### Extra rules, declinable

- The plan proposes the preset plus a few extra rules (candidates, to be fixed in this ticket:
  `ordered_imports`, `no_unused_imports`, `single_quote`, `global_namespace_import`; the list is open).
- A declined rule is written `'<rule>' => false` with a `Declined: <reason>` comment. Fulfilment accepts
  `Declined:`, not `Not yet:`.
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

### Cutting: one rule at a time, a staging file per rule

Worked example: `array_syntax` (short arrays), part of the preset, hits several hundred files.

- **Main config** (`.php-cs-fixer.dist.php`): preset, **all** paths. Rules rolled out everywhere are on;
  rules in progress or not yet taken in are `false` with `Not yet:`.
- **Staging config** (one per rule in progress; file name open): only that rule, a Finder over the paths
  already migrated. Tried with two config files and `--config`: they run independently.
- **CI** runs the main config and every staging config.
- Sequence: adoption MR with the rule `false`; then one MR per directory step (or file group for a big
  directory): widen the staging Finder, commit the tool's formatting run by itself; last MR: the Finder
  covers everything, the staging file is deleted and the rule's `false` is removed from main.
- Why not narrow the main Finder: paths dropped from main would lose every rule already rolled out.
- Only one staging file at a time; a later run finds it and continues. Several tiny rules with few findings
  may share one staging file.
- The staging file's existence is the marker: it keeps the Ratchet Stage unfulfilled.
- Ordering of rules: fewest findings first (dry run per rule), stopping at the first rule whose commit a
  reviewer could not check by one pattern, as for PHPMD (*Taking in a rule*). Path steps are sized by the
  agent's judgment, no fixed threshold.

## Open points

- Name of the staging file and of the Ratchet Stage.
- Extra rule list (see above).
- `.git-blame-ignore-revs`: a squash merge changes the commit hash, so the entry cannot be written on the
  branch. A follow-up step after merge, or left out?
- Merge conflicts with parallel work when a step touches many files; smaller directory steps only mitigate.
- A staging file a human created by hand before any plan: does it count as the marker?
- Separate cache file per config (set in the experiment, collisions not tested).
- `pack.json` `min_runtime: php 5.3` for this Tool: the fixer's own requirement is `^7.4 || ^8.0`
  (3.95.27); decide whether the field is about the tool, the target, or is just stale.

## Verified facts

Checked 2026-10-20 against PHP CS Fixer 3.95.27 on PHP 8.3 (throwaway install, not part of the repo):

- Current preset names: `@PER-CS3x0`, `@PER-CS2x0`, `@PER-CS1x0`, `@PER-CS` (floating) and their `:risky`
  variants; the dotted names are deprecated. `@PSR12` is not deprecated.
- Fixer `composer.json` requires PHP `^7.4 || ^8.0`.
- `@PER-CS3x0` includes `array_syntax` (short): the main run reported `array(1, 2)` as fixable.
- Two config files with `--config` work side by side.

## To change when built

`php-cs-fixer.md` (two Stages, preset, markers, staging pattern), `pack.json` (second Stage, edges),
the docs `AGENTS.md` lists for a skill change (`docs/playbooks/tracks.md`, `CONTEXT.md` if *Not yet* /
*Declined* / staging file become vocabulary, `docs/FAQ.md` for "why two Stages"), a `.changelog.d/`
fragment, and tests in `scripts/`. `pint.md` and `ecs.md` stay as they are.

## Comments
