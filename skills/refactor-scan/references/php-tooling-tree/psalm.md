# Psalm (`psalm`, `psalm-taint-analysis`)

Nodes on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**). One file for both nodes (a deliberate exception to this directory's usual one-file-per-node shape — see `php-tooling-tree.md`'s *Nodes* preamble, and `phpstan.md`'s own opening note for the precedent) because `psalm-taint-analysis`'s Co-presence caveat and `psalm`'s own Co-presence bullet constantly cross-reference each other.

### `psalm`

- **Name:** Psalm
- **Tool:** vimeo/psalm
- **Purpose:** an alternative static-analysis path to the PHPStan level chain — recognized when a project
  has already adopted Psalm instead of PHPStan, never suggested as a new adoption (the same fait-accompli
  recognition Pest gets for `phpunit`).
- **Fulfilment check:** `vimeo/psalm` present as a dependency (dev or prod) with a committed
  `psalm.xml`/`psalm.xml.dist`, and `vendor/bin/psalm` exits without errors.
- **MR scope:** none — never proposed as a candidate by `next_candidates()`/`roadmap()`; recognized only
  when already present. Adopting Psalm from scratch is a decision made outside this tree's proposal flow,
  same as choosing Pest over PHPUnit.
- **Mutual exclusion:** the first scan pass that recognizes this node fulfilled while real
  PHPStan adoption is absent should write an
  `out-of-scope/phpstan-level-10.md` entry in the Refactoring Notes if it isn't already present — this
  resolves `phpstan-level-10` (the PHPStan level chain's `php-structural-scan` leaf) as rejected instead of
  leaving it permanently neither-fulfilled-nor-rejected. Because this node has no tree-proposed MR of its
  own to attach the write to (`MR scope: none`, above), this is housekeeping the scanning agent performs as
  part of that recognition pass, not part of an MR — the same "an agent records a decision" shape the
  `out-of-scope/` convention already requires (see `php-tooling-tree.md`'s *Nodes* preamble), just
  triggered by recognition instead of an MR landing. Template (mirrors the shape already used throughout
  the Refactoring Notes' `out-of-scope/` in this repo's own fixtures):
  ```markdown
  # Rejection: PHPStan Level 10

  **Date:** <today>
  **Reason:** mutual exclusion — this target adopted Psalm as its static analyzer (`psalm` node
  fulfilled); the PHPStan level chain does not apply (see `phpstan.md`'s *`phpstan` equivalents* section).
  **Scope:** subtree phpstan
  ```
  This does **not** touch `phpstan-level-0` itself — see that node's own entry and the
  *Equivalents* section in `phpstan.md` for why its equivalence-driven fulfilment must stay intact.
- **Co-presence:** if both PHPStan and Psalm are present, PHPStan is authoritative for the level chain (see
  `phpstan.md`'s *Equivalents* section) — this node still shows fulfilled, harmlessly; nothing downstream
  reads its fulfilled state except `phpstan-level-0`'s own equivalence bullet and `rector-php-set`'s
  (`rector.md`) `required-any` gate (already satisfied via `phpstan-level-0` on that path regardless, so
  this is never load-bearing there either). A target that adopts `psalm-taint-analysis` (below) on the
  PHPStan path also installs `vimeo/psalm` and a `psalm.xml`, which makes this node's own fulfilment check
  incidentally read `true` too — harmless: `psalm` isn't a `php-structural-scan` leaf, so there's no
  resolved-leaf state this could disturb. See `psalm-taint-analysis`'s own entry below for the full
  reasoning.

### `psalm-taint-analysis`

- **Name:** Psalm Taint Analysis
- **Tool:** vimeo/psalm (`--taint-analysis`)
- **Purpose:** security-focused taint analysis (SQL injection, XSS, and similar tainted-data-flow bugs) —
  a distinct capability from Psalm's general static analysis, orthogonal to which general analyzer a
  target chose. Available once either general-analysis path has matured enough to be worth layering a
  security scan on top of, regardless of whether that path is PHPStan or Psalm.
- **Required-any parents:** `phpstan-level-4` (`phpstan.md`), `psalm` (above) — a new edge type
  (`CONTEXT.md`: **required-any edge**) distinct from a `required` edge: this node is proposed once **at
  least one** of these is fulfilled, not both. Either a target that reached PHPStan level 4, or a target
  that chose Psalm as its general analyzer, unlocks this node.
- **Fulfilment check:** `vimeo/psalm` present as a dependency (dev or prod), a committed
  `psalm.xml`/`psalm.xml.dist`, and — once `ci-runner` is fulfilled — a CI job that actually invokes
  `vendor/bin/psalm --taint-analysis` (self-wired CI gate, same ticket-34 shape as
  `phpstan-level-0`'s own CI check; no CI yet still fulfils the node on local adoption alone).
- **MR scope:** on the Psalm path, `vimeo/psalm` and `psalm.xml` already exist (via the `psalm` node) —
  this MR only wires the `--taint-analysis` CI invocation. On the PHPStan path, this MR additionally runs
  `composer require --dev vimeo/psalm` and commits a `psalm.xml` (reused for taint-checking only, not as a
  competing general analyzer) alongside the CI wiring.
- **Co-presence caveat:** adopting this node on the PHPStan path installs `vimeo/psalm` + `psalm.xml`
  purely for taint scanning, which incidentally makes the `psalm` node's own live-detected `fulfilled` flag
  read `true` too. This is harmless: `psalm` isn't a `php-structural-scan` leaf (see that node's entry
  above), so there's no resolved-leaf state to disturb; `rector-php-set`'s (`rector.md`)
  `required-any(phpstan-level-0, psalm)` gate stays satisfied regardless either way on the PHPStan
  path (already unlocked via `phpstan-level-0`); and the PHPStan/Psalm choice itself was never
  encoded as a written rejection to begin with (see `phpstan-level-0`'s own MR-scope entry in
  `phpstan.md`) — only the tree structure and each node's own detection record it. Nothing reads
  `psalm.fulfilled` in a way this incidental flip could break.
- **`php-structural-scan` resolved-leaf:** yes — one of the thirteen. The gate's purpose is "deterministic
  tooling has had its say before agent-driven structural work begins" (`skills/refactor-scan/references/tooling-tree.md`'s
  `structural-scan` node), not "structural-quality tools only" — `composer-audit` (`composer-audit.md`) is
  already one of these thirteen leaves and is itself a pure security scan (dependency vulnerabilities), so
  excluding this node on a "security vs. structural" distinction wouldn't have been consistent with that
  precedent.
