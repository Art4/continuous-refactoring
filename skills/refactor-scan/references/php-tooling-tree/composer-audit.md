# `composer-audit`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** Composer Audit
- **Tool:** composer audit
- **Purpose:** dependency vulnerability visibility, enforced as a CI gate (absorbs what was originally
  tracked as a separate dependency-vulnerability-scan concern, now folded into this node).
- **Fulfilment check:** a CI job exists that runs `composer audit` (the pipeline fails when it reports a
  known advisory).
- **MR scope:** wire `composer audit` into CI as a gate — no production-code change.
- **Stop conditions / when not to propose:** both required parents (`composer`, `ci-runner`) fulfilled is
  necessary but not sufficient — this node also stays blocked until either (a) `composer.json`'s
  `require` block names at least one real package (platform pseudo-packages — `php`, `hhvm`, `ext-*`,
  `lib-*`, `composer-plugin-api`, `composer-runtime-api` — don't count; `composer audit` has nothing to
  check without a real dependency), **or** (b) every other leaf feeding `php-structural-scan`
  (`php-structural-scan.md`) — `phpunit`, `test-runner-if-missing`, `php-cs-fixer`, `phpstan-level-10`,
  `phpstan-deprecation-rules` (`phpstan.md`), `rector-dead-code`, `rector-type-coverage`, `rector-php-set`,
  `rector-code-quality`, `rector-phpunit-set` (`rector.md`), `psalm-taint-analysis`
  (`psalm.md`) — is already resolved — so a dependency-free target still eventually resolves this leaf
  instead of leaving `structural-scan` permanently blocked. (a) and (b) are independent alternatives, not
  ordered.
