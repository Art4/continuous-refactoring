# PHP Tooling Tree

The prose for the PHP Pack's three larger families: Psalm, PHPStan and Rector. **The edges, the Stages and their order live in `packs/php/pack.json`** (`tooling-model.md`); the other Tools of the Pack have their file in `packs/php/`. Paragraphs below that describe edges, parents, children or aggregation nodes describe the model before `tooling-model.md` and are superseded by it. Which Stages are fulfilled is judged against the target in a scan; which are rejected is read from the target's recorded rejections (`rejection.md`). Vocabulary: `CONTEXT.md`.

## Nodes

A Stage may span several merge requests. A Tool's full definition lives in its own file under `php-tooling-tree/` (sibling to this document), named by the `details` field of the Tool in the Pack. Every Tool and Stage also carries a **Name**, the label ticket titles, merge requests and reports use instead of the slug.

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

