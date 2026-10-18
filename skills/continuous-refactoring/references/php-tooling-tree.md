# PHP Tooling Tree

The prose for the PHP Pack's Tools. **The edges, the Stages and their order live in `packs/php/pack.json` now** (`tooling-model.md`); this document and the files under `php-tooling-tree/` keep what is prose: Purpose, Fulfilment check, MR scope, Housekeeping lines. Paragraphs below that describe edges, parents, children, aggregation nodes or recognition-only gates describe the model before `tooling-model.md` and are superseded by it; they leave when the Tool files move into the Packs. Which Stages are fulfilled is judged against the target in a scan; which are rejected is read from the target's recorded rejections (`rejection.md`). Vocabulary: `CONTEXT.md`.

## Nodes

A Stage may span several merge requests. Reopening a rejected Stage is reversing its recorded rejection (`rejection.md`, *Reversing*). A Tool's full definition lives in its own file under `php-tooling-tree/` (sibling to this document), named by the `details` field of the Tool in the Pack. Every Tool and Stage also carries a **Name** — the human-readable label ticket titles, merge requests and a run's reports use instead of the slug (e.g. `phpstan-level-0` → "PHPStan Level 0"). The stub left behind here keeps Name, Tool and Purpose inline so that label is available without opening the file; Fulfilment check and MR scope are in the file.

### The runtime floor

Four PHP tools carry a `min_runtime` in `packs/php/pack.json`: the oldest PHP release any published version of the tool has ever run on (`php-cs-fixer` and `phpunit` 5.3, `composer-audit` 7.2, `phpstan` 7.0). The agent reads the lowest PHP the target allows from `composer.json` — `config.platform.php` where it is set, otherwise the lowest version `require.php` allows — and hands it to the parser as the seed's `runtime` (`tooling-parser.md`). The parser reports a tool below its minimum in `runtime_blocked`, at the tool's first Stage, with both versions in the reason. It can not be set up while the target allows the older PHP, and left undecided it keeps the Safety Net from being fulfilled: `phpunit` and the PHPStan level chain are Safety Net Stages. A scan therefore proposes recording a rejection that carries the minimum as its blocker (`rejection.md`, *Below the runtime floor*); the Stage then counts as decided, and the parser reports the reversal once the target's floor reaches that version.

### `require-dev` security advisories

A known security advisory in a `require-dev` package never blocks that package's adoption. Dev-only
tooling (test runners, static analysers, style fixers, …) is excluded from production installs
(`composer install --no-dev`) and never ships or runs there — the blast radius stays inside CI/dev
machines. More importantly, the tooling a vulnerable dev-dependency provides — most of all a test suite —
is frequently the prerequisite for the very refactoring/PHP-upgrade path that would let a newer,
non-vulnerable version of that same tool be adopted later; refusing it here would block the fix instead
of enabling it. Applies tree-wide to every `require-dev` node (`phpunit` below is the concrete case that
surfaced this rule). Does not apply to `require` (production) dependencies — that's exactly what
`composer-audit` (below) exists to police.

### `php-minimal-version`

- **Name:** PHP Minimum Version
- **Tool:** none
- **Purpose:** a **Floor correction** only, never a **Floor raise** (`CONTEXT.md`) — bring
  `composer.json`'s declared PHP floor in line with syntax the codebase already demonstrably contains
  once `rector-php-set` has landed it, so the declared floor stops understating reality. Never proposes
  committing the application to a newer PHP than its own code currently needs — that would be a
  **Breaking change**, out of this node's scope entirely. A **Guardrails** node (`CONTEXT.md`): keeps
  `rector-php-set` as a required parent and additionally requires `php-safety-net`, so it's never
  proposed ahead of the Safety Net closing.
  No third-party tool: the tree's own gap detection.

Full definition (Fulfilment check, MR scope, Re-triggering, Required parent): `php-tooling-tree/php-minimal-version.md`.

### `composer`

- **Name:** Composer
- **Tool:** Composer
- **Purpose:** dependency management for the Composer-stack track.

Full definition (Fulfilment check, MR scope): `php-tooling-tree/composer.md`.

### `psr-4`

- **Name:** PSR-4 Autoloading
- **Tool:** none
- **Purpose:** give the app's own source code a real PSR-4 namespace mapping, distinct from the incidental PSR-4 usage `phpunit.md`'s test layout and `phpstan.md`'s `paths` resolution already have. Not a runnable tool: a `composer.json` autoload declaration plus a namespace convention.

Full definition (Fulfilment check, MR scope, Required parent): `php-tooling-tree/psr-4.md`.

### `php-cs-fixer`

- **Name:** PHP CS Fixer
- **Tool:** php-cs-fixer
- **Purpose:** automated code style so later Rector output lands styled.

Full definition (Fulfilment check, MR scope, Recommended parent, Recommended child): `php-tooling-tree/php-cs-fixer.md`.

### `phpmd`

- **Name:** PHPMD
- **Tool:** PHPMD
- **Purpose:** cyclomatic-complexity and code-quality signal for the search for structural candidates — a Signal-producing node, not a Safety Net one (no `resolved` edge anywhere). Also a **Guardrails** node (`CONTEXT.md`, orthogonal to the **Signal** field above): keeps `composer` as a required parent and additionally requires `php-safety-net`, so it's never proposed ahead of the Safety Net closing.
- **Signal:** Understandability (the complexity measurement itself) and Defect density (complexity's empirical correlation with bugs) — both `signals.md` factors, once this node is fulfilled its real output supersedes the generic git-log heuristic for them.

Full definition (Fulfilment check, MR scope, Required parent): `php-tooling-tree/phpmd.md`.

### `phpunit`

- **Name:** PHPUnit
- **Tool:** PHPUnit
- **Purpose:** the project's test runner.

Full definition (Fulfilment check, security advisories, MR scope, test-directory layout convention): `php-tooling-tree/phpunit.md`.

### `coverage-floor`

- **Name:** Test Coverage Floor
- **Tool:** PHPUnit
- **Purpose:** a self-tightening coverage ratchet plus real per-file numbers for the search for structural candidates — a Signal-producing node, not a Safety Net one (no `resolved` edge anywhere). Also a **Guardrails** node (`CONTEXT.md`, orthogonal to the **Signal** field below): keeps `phpunit` as a required parent and additionally requires `php-safety-net`, so it's never proposed ahead of the Safety Net closing. Measured with PHPUnit's own coverage report (PCOV or Xdebug as the driver).
- **Signal:** Untested / hard-to-test (`signals.md`) — once fulfilled, the search for structural candidates reads the real Clover-XML coverage report instead of the generic "read the test suite" heuristic.

Full definition (Fulfilment check, MR scope, Ratchet mechanism, PCOV-vs-Xdebug): `php-tooling-tree/coverage-floor.md`.

### `composer-audit`

- **Name:** Composer Audit
- **Tool:** composer audit
- **Purpose:** dependency vulnerability visibility, enforced as a CI gate (absorbs what was originally
  tracked as a separate dependency-vulnerability-scan concern, now folded into this node). A **Guardrails** node (`CONTEXT.md`): audits
  third-party CVEs a target's own structural refactoring neither creates nor fixes, unlike
  `psalm-taint-analysis`, so it no longer gates `structural-scan` — keeps `composer` as a required
  parent and additionally requires `php-safety-net`.

Full definition (Fulfilment check, MR scope, Required parent, Stop conditions): `php-tooling-tree/composer-audit.md`.

### `psalm`

- **Name:** Psalm
- **Tool:** vimeo/psalm
- **Purpose:** an alternative static-analysis path to the PHPStan level chain — recognized when a project
  has already adopted Psalm instead of PHPStan, never suggested as a new adoption (the same fait-accompli
  recognition Pest gets for `phpunit`).

Full definition (Fulfilment check, MR scope, Mutual exclusion, Co-presence): `php-tooling-tree/psalm.md`.

### `phpstan-level-0`

- **Name:** PHPStan Level 0
- **Tool:** PHPStan
- **Purpose:** static analysis introduced green at level 0. `vimeo/psalm`, via the `psalm` node above, fulfils as an equivalent — see the extracted file's *Equivalents* section.

Full definition (Fulfilment check, Config, MR scope, Verification, and the cross-cutting *`phpstan`
equivalents* section — Psalm's equivalence to this node, co-presence, mutual exclusion):
`php-tooling-tree/phpstan.md`.

### `phpstan-level-1` through `phpstan-level-10`

- **Names:** `phpstan-level-N` → "PHPStan Level N" for each `N` in 1–10 (e.g. `phpstan-level-4` → "PHPStan Level 4").
- **Tool:** PHPStan
- **Purpose:** raise the analysis level one step at a time, straight through the chain, same rules
  throughout, no redesign at any level — `phpstan-level-5` is the chain's resolved-leaf into
  `php-safety-net` (see that node's own entry and `phpstan-deprecation-rules`' required-parent
  line above for why level 5); every other level (`1`–`4`, `7`–`10`) is an ordinary, non-gating
  intermediate node — levels above 5 stay proposable, they just no longer hold up structural work.
  `phpstan-level-6` is the one exception among them: a **Guardrails** node (`CONTEXT.md`) —
  keeps `phpstan-level-5` as its ordinary
  chain predecessor and additionally requires `php-safety-net`, so it's never proposed ahead of the
  Safety Net closing; levels 7–10 need no edge of their own, inheriting the wait transitively through
  level 6.

Full definition (Fulfilment check, Empty baseline, MR scope, Stop conditions, Verification):
`php-tooling-tree/phpstan.md`.

### `phpstan-deprecation-rules`

- **Name:** PHPStan Deprecation Rules
- **Tool:** PHPStan
- **Purpose:** flag calls to deprecated APIs/functions, orthogonal to the level chain's strictness ladder —
  adopted once the codebase is far enough along the chain that deprecation noise isn't drowned out by
  lower-level findings. A **Guardrails** node (`CONTEXT.md`) —
  no longer a `php-safety-net` leaf (flagging
  deprecated calls doesn't collide with agent-driven structural work the way this gate's remaining
  leaves do).
  The tool is PHPStan's deprecation rule set — bundled rules PHPStan reports independently of `level`.
- **Required parents:** `phpstan-level-5` — proposed once the chain has reached level 5, a threshold decided
  directly with the user rather than tied to level 10's top — and, additionally, `php-safety-net`, so
  it's never proposed ahead of the Safety Net closing.

Full definition (Fulfilment check, MR scope): `php-tooling-tree/phpstan.md`.

### `psalm-taint-analysis`

- **Name:** Psalm Taint Analysis
- **Tool:** vimeo/psalm
- **Purpose:** security-focused taint analysis (SQL injection, XSS, and similar tainted-data-flow bugs) —
  a distinct capability from Psalm's general static analysis, orthogonal to which general analyzer a
  target chose. Available once either general-analysis path has matured enough to be worth layering a
  security scan on top of, regardless of whether that path is PHPStan or Psalm.
  Run as `vimeo/psalm --taint-analysis`.

Full definition (Required-any parents, Fulfilment check, MR scope, Co-presence caveat, `php-safety-net` resolved-leaf): `php-tooling-tree/psalm.md`.

### `semgrep`

- **Name:** Semgrep (OWASP Top 10)
- **Tool:** Semgrep
- **Purpose:** broad OWASP Top 10 static-analysis coverage for the search for structural candidates — a Signal-producing node, not a Safety Net one (no `resolved` edge anywhere). Complements `psalm-taint-analysis` rather than duplicating it. Also a **Guardrails** node (`CONTEXT.md`): required parent is `php-safety-net` alone (fully replacing the old `composer` edge — this node was the one clean full-replacement case, see its own entry for why). A standalone binary/Python/Docker tool, not a Composer dependency.
- **Signal:** Security (`signals.md`) — alongside `psalm-taint-analysis`'s own real findings for the same factor.

Full definition (Required parent, Recommended parent, Fulfilment check, MR scope): `php-tooling-tree/semgrep.md`.

### `rector-dead-code`

- **Name:** Rector: Dead Code Set
- **Tool:** Rector
- **Purpose:** remove dead code with rules whose changes are safe to review early. Uses Rector's dead-code suite.

Full definition (Fulfilment check, MR scope, Required parent): `php-tooling-tree/rector.md`.

### `rector-type-coverage`

- **Name:** Rector: Type Coverage Set
- **Tool:** Rector
- **Purpose:** raise declared type coverage progressively. Uses Rector's typing suites.

Full definition (Fulfilment check, MR scope, recommended-only gating): `php-tooling-tree/rector.md`.

### `rector-php-set`

- **Name:** Rector: PHP Set
- **Tool:** Rector
- **Purpose:** adopt Rector's own PHP-version-targeted rule set — the common gate the other Rector
  rule-set nodes below wait on, mirroring how `phpstan-level-0`/`psalm` gate the family today.
  A versioned PHP-upgrade rule set, e.g. `LevelSetList::up_to_php_8x`.

Full definition (Fulfilment check, MR scope, Required-any parents, Recommended parent): `php-tooling-tree/rector.md`.

### `rector-code-quality`

- **Name:** Rector: Code Quality Set
- **Tool:** Rector
- **Purpose:** apply Rector's code-quality rewrites (readability/idiom improvements beyond dead-code
  removal) — including flattening nested conditionals into early returns, folded in once Rector's own
  dedicated early-return rule set shipped empty upstream.
  Uses Rector's code-quality suite.

Full definition (Fulfilment check, MR scope, Required parent, Recommended parent): `php-tooling-tree/rector.md`.

### `rector-phpunit-set`

- **Name:** Rector: PHPUnit Set
- **Tool:** Rector
- **Purpose:** modernize PHPUnit test code (assertion methods, annotations → attributes, etc.) via Rector's
  PHPUnit rule set.

Full definition (Fulfilment check, MR scope, Required parent, Recommended parents): `php-tooling-tree/rector.md`.

