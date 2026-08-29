# PHP Tooling Tree

The canonical shape of the PHP specialization's **tooling tree**. This document records the form only — nodes and edges below `loop-config` (see `skills/refactor-scan/references/tooling-tree.md` for the generic root, and for `structural-scan`, this tree's downstream gate). Fulfilment and rejection state lives in each target repo under `docs/refactoring/`. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

## Diagram

```mermaid
graph TD
    lc[loop-config]
    ci[ci-runner]
    comp[composer]
    cs[php-cs-fixer]
    unit[phpunit]
    audit[composer-audit]
    tr[test-runner-if-missing]
    p0[phpstan-level-0-baseline]
    p1[phpstan-level-1]
    p2[phpstan-level-2]
    p3[phpstan-level-3]
    rdc[rector-dead-code]
    rtc[rector-type-coverage]
    ss[structural-scan]

    lc -->|required| comp
    lc -->|required| ci
    comp -->|required| cs
    comp -->|required| unit
    comp -->|required| tr
    comp -->|required| audit
    comp -->|required| p0
    p0 -->|required| p1
    p1 -->|required| p2
    p2 -->|required| p3
    p0 -->|required| rdc
    p0 -->|required| rtc
    cs -.->|recommended| rdc
    cs -.->|recommended| rtc
    p3 -.->|recommended| rtc
    audit -.->|resolved| ss
    unit -.->|resolved| ss
    tr -.->|resolved| ss
    cs -.->|resolved| ss
    p3 -.->|resolved| ss
    rdc -.->|resolved| ss
    rtc -.->|resolved| ss
```

## Edges

| from (parent) | to (child) | type |
|---|---|---|
| `loop-config` | `composer` | required |
| `loop-config` | `ci-runner` | required |
| `composer` | `php-cs-fixer` | required |
| `composer` | `phpunit` | required |
| `composer` | `test-runner-if-missing` | required |
| `composer` | `composer-audit` | required |
| `composer` | `phpstan-level-0-baseline` | required |
| `phpstan-level-0-baseline` | `phpstan-level-1` | required |
| `phpstan-level-1` | `phpstan-level-2` | required |
| `phpstan-level-2` | `phpstan-level-3` | required |
| `phpstan-level-0-baseline` | `rector-dead-code` | required |
| `phpstan-level-0-baseline` | `rector-type-coverage` | required |
| `php-cs-fixer` | `rector-dead-code` | recommended |
| `php-cs-fixer` | `rector-type-coverage` | recommended |
| `phpstan-level-3` | `rector-type-coverage` | recommended |
| `composer-audit` | `structural-scan` | resolved |
| `phpunit` | `structural-scan` | resolved |
| `test-runner-if-missing` | `structural-scan` | resolved |
| `php-cs-fixer` | `structural-scan` | resolved |
| `phpstan-level-3` | `structural-scan` | resolved |
| `rector-dead-code` | `structural-scan` | resolved |
| `rector-type-coverage` | `structural-scan` | resolved |

The table is the machine-readable source; the diagram is its rendering. Extending the tree means adding a row here and the matching line in the diagram.

The seven `resolved` rows above are not `required` or `recommended` — see `skills/refactor-scan/references/tooling-tree.md`'s `structural-scan` node for what `resolved` means (a rejected leaf still unblocks `structural-scan`, unlike a rejected required parent) and why it exists.

## Nodes

A node may span several merge requests; a rejection of a required parent closes every node beneath it, a rejected recommended parent never blocks (the merge request outlook states where it would have helped). Reopening a rejected node is a recorded reversal of its out-of-scope entry; dependents unlock at fulfilment.

A node's full definition may live in its own file under `php-tooling-tree/` (sibling to this document) once extracted — see `composer` below for the first example. The stub left behind here keeps Tool and Purpose inline so merge requests can be described by the tool's human-readable name rather than the node's slug (e.g. `phpstan-level-0-baseline` reads as "PHPStan Level 0"); Fulfilment check and MR scope move to the extracted file. Nodes not yet extracted stay inline in full.

### `ci-runner`

- **Tool:** GitHub Actions / GitLab CI
- **Purpose:** an existing pipeline that later hosts quality jobs.
- **Fulfilment check:** CI config file present; forge determined from `git remote`; unknown CI → ask, do not record a rejection.
- **MR scope:** pipeline file only. Quality-job children have two parents (this node + their tool) and are deferred to a later wave.

### `composer`

- **Tool:** Composer
- **Purpose:** dependency management for the Composer-stack track.

Full definition (Fulfilment check, MR scope): `skills/refactor-scan/references/php-tooling-tree/composer.md`.

### `php-cs-fixer`

- **Tool:** php-cs-fixer
- **Purpose:** automated code style so later Rector output lands styled.
- **Fulfilment check:** dev dependency installed, config committed, runnable locally with zero reported diffs.
- **MR scope:** dependency + config + one formatting pass.

### `phpunit`

- **Tool:** PHPUnit
- **Purpose:** the project's test runner.
- **Fulfilment check:** dev dependency installed and runnable (`phpunit` exits green on existing tests); an equivalent already present (Pest) fulfils the node.
- **MR scope:** dependency + minimal config; no test rewrites.

### `test-runner-if-missing`

- **Tool:** any test runner
- **Purpose:** guarantees *some* runner exists before deepening work relies on tests.
- **Fulfilment check:** proposed only when no runner exists; fulfilled by adopting one (default PHPUnit).
- **MR scope:** dependency + config + smoke test if none exists.

### `composer-audit`

- **Tool:** composer audit
- **Purpose:** dependency vulnerability visibility (thin node).
- **Fulfilment check:** `composer audit` runs locally without configuration errors.
- **MR scope:** none beyond running it — making it fail CI is a separate child in a later wave (ticket 10).

### `phpstan-level-0-baseline`

- **Tool:** PHPStan (`vimeo/psalm` fulfils as an equivalent — see *Equivalents* below).
- **Purpose:** static analysis introduced green at level 0.
- **Fulfilment check:** one of:
  - **PHPStan path (canonical):** `phpstan/phpstan` present as a dev dependency, `phpstan.neon` at the repo root declares `level: 0`, a committed baseline file exists at the fixed path `phpstan-baseline.neon` (repo root), and `vendor/bin/phpstan analyse` (with the baseline included) exits 0 without errors. OR
  - **Psalm path (equivalent):** `vimeo/psalm` present (dev or prod dependency) with a committed `psalm.xml` / `psalm.xml.dist` and `vendor/bin/psalm` exits without errors — then this node is considered fulfilled without PHPStan. Psalm's own strictness is tracked via its `errorLevel`, not via the PHPStan level chain.
- **Config (PHPStan path):**
  - `phpstan.neon` — committed at repo root (not `phpstan.neon.dist`). Minimal exact content:
    ```neon
    parameters:
        level: 0
        paths:
            - src
        excludePaths:
            - vendor
    includes:
        - phpstan-baseline.neon
    ```
    `paths` is resolved from `composer.json` `autoload` / `autoload-dev` (`psr-4` + `psr-0` directories; `files` ignored). If no autoload directories are declared, the fallback is `src`. Additional source roots (e.g., `tests/` when not already covered) may be appended when present. `excludePaths` always contains `vendor`. `includes` references the baseline at the fixed path `phpstan-baseline.neon` (repo root); the line is present in `phpstan.neon` from the introduce MR onward.
  - `phpstan-baseline.neon` — committed at repo root. Auto-generated, never hand-edited. Generated by `vendor/bin/phpstan analyse --generate-baseline=phpstan-baseline.neon` (overwrites if present). Contains `parameters.ignoreErrors` entries for all violations at the current level; when no violations remain the file is still committed but contains an empty ignore list (see *Empty baseline*).
  - Dependency versioning follows the target's pinning policy; if none is declared, use a `^` caret range with a committed `composer.lock`.
- **MR scope:** dependency addition (`composer require --dev phpstan/phpstan`) + `phpstan.neon` with `level: 0` + initial baseline generation (`--generate-baseline`) committed together, leaving `vendor/bin/phpstan analyse` green (exit 0). Shrinking the baseline belongs to the level nodes' scope, not this introduce MR. No level above 0 and no additional rulesets are introduced here.
- **Verification:** `composer install` succeeds locally; `vendor/bin/phpstan analyse --error-format=table` (or plain `vendor/bin/phpstan analyse`) exits 0 with the committed baseline included.

### `phpstan-level-1`, `phpstan-level-2`, `phpstan-level-3`

- **Tool:** PHPStan
- **Purpose:** raise the analysis level one step at a time.
- **Fulfilment check:** the immediate predecessor level node is fulfilled **and** its baseline is **empty** (see *Empty baseline*). Then: bump `level` in `phpstan.neon` by exactly one (e.g., `0 → 1`, `1 → 2`), regenerate `phpstan-baseline.neon` via `vendor/bin/phpstan analyse --generate-baseline=phpstan-baseline.neon`, and `vendor/bin/phpstan analyse` is green. Levels are never skipped; one MR raises exactly one level.
- **Empty baseline — operational definition:** `phpstan-baseline.neon` is **absent** at repo root **OR** the file exists but `parameters.ignoreErrors` is absent or an empty array (no `message:` entries). Both count as empty. A file that exists and contains one or more ignore entries is non-empty and blocks the next level raise. The scan performs this check by parsing the Neon file (or, equivalently, counting `message:` entries); an absent file is treated as zero entries. After the introduce MR the file is normally present; absence is tolerated as empty for the purpose of gating the next level, but after any successful analysis the committed state should include the file (empty list when green without baseline).
- **MR scope:** level bump (single integer increment) + regenerated baseline (overwritten in place) + only those source fixes that strictly reduce the new baseline's `ignoreErrors` count. Shrinking findings into the regenerated baseline is part of the same MR — the MR must commit the reduced baseline alongside any fixes that produced the reduction. Unrelated refactoring or feature changes stay out. The chain stays open above level 3 — further levels (`phpstan-level-4`, etc.) are appended as new nodes with the same rules, not a redesign.
- **Stop conditions / when not to raise:**
  - Baseline is non-empty → do not propose the next level; the loop proposes shrinking work (candidates flagged by the fulfilled tooling, or Rector steps that reduce baseline entries) until the baseline becomes empty.
  - Immediate predecessor level node is not fulfilled → blocked by the required edge; the scan does not propose out-of-order levels.
  - Target uses Psalm as its `phpstan-level-0-baseline` fulfiller → level nodes are not proposed at all (see *Equivalents*). Psalm strictness is governed by `psalm.xml` `errorLevel`, not by this chain.
  - CI is irrelevant to this node's gating: the fulfilment check is local (`vendor/bin/phpstan analyse` green). The CI-job child with two parents (tool + `ci-runner`) remains deferred and does not gate the level chain.
- **Verification:** after the MR, `vendor/bin/phpstan analyse` exits 0 at the new level with the committed baseline; `phpstan.neon` diff is exactly one `level:` line change; `phpstan-baseline.neon` is regenerated and reflects the current violations at that level.

### `phpstan` equivalents

- **Psalm (`vimeo/psalm`) fulfils `phpstan-level-0-baseline`** — fill gaps, never downgrade; an equivalent fulfils the node (same as Pest fulfils `phpunit`). Detection: `composer.json` lists `vimeo/psalm` and a Psalm config file (`psalm.xml` or `psalm.xml.dist`) exists. When present and green, the scan marks `phpstan-level-0-baseline` as fulfilled and does not propose the PHPStan introduce candidate.
- **Level nodes (`phpstan-level-1` → `phpstan-level-3`) do not apply when Psalm is the fulfiller.** They are PHPStan-specific. A project that chose Psalm raises strictness via Psalm's `errorLevel` (8 loosest → 1 strictest) rather than via PHPStan levels; proposing a PHPStan level on top of a Psalm-only codebase would reintroduce a second analyser as a new, out-of-scope decision. If a repo later replaces Psalm with PHPStan, that is recorded as a reversal of the Psalm equivalent and the PHPStan introduce + level chain is then proposed from level 0.
- **Co-presence:** if both analysers are present, PHPStan is the authoritative check for this tree; Psalm fulfilment is considered superseded and the standard PHPStan baseline/level rules apply.
- **No other analyser fulfils the node:** only `vimeo/psalm` is recognised as an equivalent for the PHPStan nodes. Other tools (e.g., Phan, Psalm plugins) are not treated as fulfilling this chain.

### `rector-dead-code`

- **Tool:** Rector (dead-code suite)
- **Purpose:** remove dead code with rules whose changes are safe to review early.
- **Fulfilment check:** dead-code suite enabled and fully applied — no remaining rule findings.
- **MR scope:** adopted in levels, one MR per level; keeps PHPStan green by shrinking the baseline within the same MRs.

### `rector-type-coverage`

- **Tool:** Rector (typing suites)
- **Purpose:** raise declared type coverage progressively.
- **Fulfilment check:** typing suites enabled and fully applied at the agreed coverage degree.
- **MR scope:** adopted in levels, one MR per level; keeps PHPStan green via baseline shrinking. Proposed once `phpstan-level-0-baseline` is fulfilled; most valuable after `phpstan-level-3` — without strict analysis its rewrites are hard to review, without `php-cs-fixer` its output cannot be styled (stated in the outlook when those are unfulfilled or rejected).
