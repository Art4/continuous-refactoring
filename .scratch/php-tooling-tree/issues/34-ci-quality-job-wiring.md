# 34 — Define the `phpunit`/`phpstan` CI-quality-job nodes the `ci-runner` node already promises

**What to build:** Define `phpunit`-as-CI-job and `phpstan`-as-CI-job tooling-tree nodes (two required parents each: `ci-runner` + the tool, mirroring `composer-audit`'s existing shape) and add their edges to `skills/refactor-scan/references/php-tooling-tree.md`, so a target that has adopted PHPUnit/PHPStan locally but never wired either into its CI pipeline gets that proposed as its own candidate.

**Why:** `ci-runner`'s own node prose already promises this: "Quality-job children have two parents (this node + their tool) and are deferred to a later wave" (`skills/refactor-scan/references/php-tooling-tree.md`). `composer-audit` is the one example of that later wave that actually got filed and built (ticket 10, done — it wires `composer audit` into CI as a gate). No equivalent ticket or node exists for `phpunit`/`phpstan`, even though a real run (`Art4/legacy-todo`) adopted both months (in-run time) before this gap was noticed: `.github/workflows/ci.yml` still only ran `php -l`, never `vendor/bin/phpunit` or `vendor/bin/phpstan analyse`, despite both being green locally the whole time.

**Blocked by:** none — `composer-audit`'s existing shape (`skills/refactor-scan/references/php-tooling-tree.md`'s `composer-audit` node, and `.scratch/php-tooling-tree/issues/10-dependency-vulnerability-scan.md`) is the template to copy, not a prerequisite.

**Priority:** high

**Status:** ready-for-human

- [ ] Add `phpunit-ci-job` node: required parents `ci-runner` + `phpunit`; fulfilment check — a CI job exists that runs the test suite and fails the pipeline on a red result (mirror `composer-audit`'s fulfilment-check shape: "a CI job exists that runs `composer audit`").
- [ ] Add `phpstan-ci-job` node (or fold into the existing `phpstan-level-N` chain? — decide which is cleaner): required parents `ci-runner` + `phpstan-level-0-baseline`; fulfilment check — a CI job runs `vendor/bin/phpstan analyse` (with the committed baseline) and fails the pipeline on a non-zero exit.
- [ ] Decide whether either new node needs a `composer-audit`-style "extra gate" (proposable only once a real dependency exists / every other structural-scan leaf is resolved) or is simply required-edge-unlocked like most nodes — `composer-audit`'s extra gate exists because `composer audit` has nothing to check against zero real dependencies; that reasoning doesn't obviously carry over to running an already-adopted test suite or analyser, so the default (no extra gate) is the likely answer, but confirm rather than assume.
- [ ] Add both nodes' edges into `structural-scan`'s `resolved` set (mirroring how `composer-audit`, `phpunit`, `test-runner-if-missing`, `php-cs-fixer`, `phpstan-level-3`, `rector-dead-code`, `rector-type-coverage` already feed it) — these are exactly the kind of leaf that should hold structural work back until real, running the target's own CI.
- [ ] Update `tooling_tree.py`'s `detect_nodes()`/`_parse_edges()` consumers (the edges table parse is generic, but `detect_nodes()`'s per-tool filesystem checks are hardcoded per node — a real implementation needs new detection functions for these two, e.g. grepping the CI workflow file for the actual test/analyse invocation, similar to `_has_composer_audit_ci_job()`).

## Comments

> **2026-08-29:** Filed from the legacy-todo reviewer-loop findings log
> (`.scratch/legacy-todo-loop-observation/findings.md`, "Finding — CI-Pipeline führt weder PHPUnit noch
> PHPStan aus, obwohl beide adoptiert sind") after the user asked for it to be turned into a real ticket.
> The original finding explicitly noted this matches the tree's own stated design ("deferred to a later
> wave") rather than being a bug — the gap is that the later-wave ticket itself was never filed, until now.
