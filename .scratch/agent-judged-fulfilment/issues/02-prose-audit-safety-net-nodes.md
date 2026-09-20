# 02: Prose audit — Safety Net nodes

Spec: `agent-judged-fulfilment`.

**What to build:** Before any detection code is removed, the Fulfilment-check prose of every Safety Net node must carry everything the parser's detection currently knows. For each node in the Safety Net scope (the generic root nodes and the PHP nodes up to and including the resolved leaves of the safety-net aggregation node), compare the parser's heuristics with the prose in the node's tree doc and move every rule the parser applies but the prose lacks into the prose. Typical candidates: tools installed only ephemerally in a CI job, verified autoloading and entry-point wiring, equivalence and co-presence rules between Psalm and PHPStan, config-file naming variants, Rector set naming. Rules found to be deliberately dropped are recorded with the reason. No runtime behavior changes; the parser is untouched.

**Blocked by:** 01 (Stop-conditions become recognition-only gate nodes) — the same tree docs are edited there.

**Status:** implemented — PR #104, open items listed in Comments

- [x] Every Safety Net node's tree doc is audited; the ticket's Comments list each node as "prose extended" (with what was added) or "already covered".
- [ ] Every heuristic the parser applies to a Safety Net node is either stated in that node's prose or listed in Comments as intentionally dropped, with a reason.
- [x] The evidence procedure the scan uses for autoloading and unwired entry points is described in prose well enough that an agent without the script can follow it.
- [ ] The manual tree-walk fallback can evaluate every Safety Net node from the prose alone, without reading parser code.
- [x] The validation checks the repo already runs on skill and tree docs still pass.

## Comments

**PR:** [#104](https://github.com/Art4/continuous-refactoring/pull/104)

Audit outcome per node, reconstructed from the audit commit (`30efb61`, four files) and a
comparison of the pre-deletion parser (`54105f5^`, `detect_nodes()` and helpers) with each node's prose.
The commit message records no per-node verdicts, so "already covered" below is this reconstruction, not
something the commit states.

Prose extended (`30efb61`):

- `php-cs-fixer`: package names (`friendsofphp/php-cs-fixer`, `php-cs-fixer/php-cs-fixer`) and config file
  names (`.php-cs-fixer.php`, `.php-cs-fixer.dist.php`) added to the Fulfilment check.
- `psr-4`: the Composition-root / Entry-point evidence procedure (which `.php` files are walked, which
  directories and tooling-config files are excluded, `__DIR__`-relative require collection, "reached by no
  other candidate" = Entry point, "required by more than half" = Composition root, each must reference
  `vendor/autoload.php`) added to the Fulfilment check.
- `phpstan-level-1`..`-10`: the Psalm-equivalence rule (all level nodes not applicable when `psalm` is the
  fulfiller) added to the level nodes' Fulfilment check. (The applied-level constant reading added to
  `php-minimal-version.md` in the same commit belongs to ticket 03's scope.)

Already covered:

- `git`, `loop-config`, `is-php-project`, `editorconfig`, `static-code-analyzer`, `psalm` (incl.
  `psalm.xml.dist`), `phpunit` (Pest equivalent, `vendor/bin/pest` CI needle, self-wired CI gate),
  `test-runner-if-missing`, `phpstan-level-0` (ephemeral CI-runtime install, committed baseline,
  `phpstan.neon`/`.dist` precedence, CI gate, Psalm equivalence with the co-presence guard),
  `psalm-taint-analysis` (`vendor/bin/psalm --taint-analysis` needle), and the gate nodes
  `phpstan-not-psalm`/`phpstan-baseline-empty` (ticket 01).
- Parser rules not carried because the prose is the stricter or more accurate rule: `phpunit` counted a bare
  `phpunit.xml(.dist)` as adoption; `psalm` counted dep + `psalm.xml` without running `vendor/bin/psalm`;
  `composer` required a lockfile for every project type while the prose keeps the type-dependent
  lockfile rule (gitignored for `type: library`).

Not covered (open items, see the unticked boxes):

- Item 2, parser heuristics still absent from the prose:
  - `rector-php-set`, `rector-dead-code`, `rector-type-coverage`, `rector-code-quality`,
    `rector-phpunit-set`: set-name recognition (`LevelSetList`, `DeadCode`/`DEAD_CODE`,
    `CodeQuality`/`CODE_QUALITY`, `PHPUnitSetList`, case/underscore tolerance) is not in `rector.md`, which
    the audit commit did not touch; the parser's loose `Type`/`type` substring match for
    `rector-type-coverage` is neither stated nor recorded as dropped.
  - `phpstan-level-1`..`-10` (and `-6`..`-10` for ticket 03): the state predicate "the level configured in
    `phpstan.neon`/`phpstan.neon.dist` is >= N" is not written down. The level nodes' Fulfilment check
    describes delivering a bump (predecessor fulfilled, baseline empty, bump, regenerate), not how to tell
    whether level N is already reached.
  - `ci-runner`: the recognized CI files (`.github/workflows/*.yml`/`*.yaml`, `.gitlab-ci.yml`) are not
    enumerated in `ci-runner.md` (only "GitHub Actions / GitLab CI" as `Tool`).
  - `composer`: the alternate `composer/composer.json` + `composer/composer.lock` location the parser read
    is stated only in `is-php-project.md`, not in `composer.md`.
- Item 4, manual fallback from prose alone: `tree-walk-prompt.md` tells the agent to evaluate each Fulfilment
  check by reading the files it names, and the psr-4 procedure is now fully in prose, but the level-node
  predicate and the Rector set recognition above are not, so a fallback agent has to guess there. The
  prompt's "never a candidate" list also names only `static-code-analyzer`, `psalm` and `git`, while the
  recognition-only gates (`is-php-project`, `has-real-dependency`, `phpstan-baseline-empty`,
  `phpstan-not-psalm`) are stated only in their own node docs, with a pointer to `tooling_tree.py`'s
  `_NEVER_PROPOSED`.

Checks: `python3 scripts/validate_skills.py .` and the unit suite pass on the branch head (item 5).
