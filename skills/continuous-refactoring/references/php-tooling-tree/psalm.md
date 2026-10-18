# Psalm (`psalm`, `psalm-taint-analysis`)

Nodes on the PHP **tooling tree** (`../php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**). One file for both nodes (a deliberate exception to this directory's usual one-file-per-node shape — see `php-tooling-tree.md`'s *Nodes* preamble, and `phpstan.md`'s own opening note for the precedent) because `psalm-taint-analysis`'s Co-presence caveat and `psalm`'s own Co-presence bullet constantly cross-reference each other.

### `psalm`

- **Name:** Psalm
- **Tool:** vimeo/psalm
- **Purpose:** an alternative static-analysis path to the PHPStan level chain — recognized when a project
  has already adopted Psalm instead of PHPStan, never suggested as a new adoption (the same fait-accompli
  recognition Pest gets for `phpunit`).
- **Fulfilment check:** `vimeo/psalm` present as a dependency (dev or prod) with a committed
  `psalm.xml`/`psalm.xml.dist`, and `vendor/bin/psalm` exits without errors.
- **MR scope:** none — recognition-only, never a ticket; recognized only
  when already present. Adopting Psalm from scratch is a decision made outside this tree's proposal flow,
  same as choosing Pest over PHPUnit.
- **Takes the place of PHPStan:** once this Stage is fulfilled and PHPStan's first Stage is not, Psalm fills
  the Role Static Analysis and PHPStan is not proposed; none of the level Stages gets a ticket. Strictness is
  governed by `psalm.xml`'s `errorLevel`. The agent hands in `psalm` as fulfilled and does not hand in
  `phpstan-level-0` for it (`phpstan.md`, *PHPStan and Psalm*).
- **Co-presence:** if both PHPStan and Psalm are present, PHPStan is the Tool in use and this Stage is
  harmlessly fulfilled too. A target on PHPStan that adopts `psalm-taint-analysis` (below) also installs
  `vimeo/psalm` and a `psalm.xml`, so this Stage's own check reads `true` as well — which changes nothing,
  since PHPStan's first Stage is fulfilled.

### `psalm-taint-analysis`

- **Name:** Psalm Taint Analysis
- **Tool:** vimeo/psalm
- **Purpose:** security-focused taint analysis (SQL injection, XSS, and similar tainted-data-flow bugs) —
  a distinct capability from Psalm's general static analysis, orthogonal to which general analyzer a
  target chose. Available once either general-analysis path has matured enough to be worth layering a
  security scan on top of, regardless of whether that path is PHPStan or Psalm.
  Run as `vimeo/psalm --taint-analysis`.
- **Required-any parents:** `phpstan-level-4` (`phpstan.md`), `psalm` (above) — a new edge type
  (`CONTEXT.md`: **required-any edge**) distinct from a `required` edge: this node is proposed once **at
  least one** of these is fulfilled, not both. Either a target that reached PHPStan level 4, or a target
  that chose Psalm as its general analyzer, unlocks this node.
- **Fulfilment check:** `vimeo/psalm` present as a dependency (dev or prod), a committed
  `psalm.xml`/`psalm.xml.dist`, and — once `ci-runner` is fulfilled — a CI job that actually invokes
  `vendor/bin/psalm --taint-analysis` (self-wired CI gate, same shape as
  `phpstan-level-0`'s own CI check; no CI yet still fulfils the node on local adoption alone).
- **MR scope:** on the Psalm path, `vimeo/psalm` and `psalm.xml` already exist (via the `psalm` node) —
  this MR only wires the `--taint-analysis` CI invocation. On the PHPStan path, this MR additionally runs
  `composer require --dev vimeo/psalm` and commits a `psalm.xml` (reused for taint-checking only, not as a
  competing general analyzer) alongside the CI wiring.
- **Co-presence caveat:** adopting this node on the PHPStan path installs `vimeo/psalm` + `psalm.xml`
  purely for taint scanning, which incidentally makes the `psalm` node's own Fulfilment check
  read fulfilled too. This is harmless: `psalm` isn't a `php-safety-net` leaf (see that node's entry
  above), so there's no resolved-leaf state to disturb; `rector-php-set`'s (`rector.md`)
  `required-any(phpstan-level-0, psalm)` gate stays satisfied regardless either way on the PHPStan
  path (already unlocked via `phpstan-level-0`); and the PHPStan/Psalm choice itself was never
  encoded as a written rejection to begin with (see `phpstan-level-0`'s own MR-scope entry in
  `phpstan.md`) — only the tree structure and each node's own detection record it. Nothing reads
  `psalm.fulfilled` in a way this incidental flip could break.
- **`php-safety-net` resolved-leaf:** yes — one of the nine. The gate's purpose is "deterministic
  tooling has had its say before agent-driven structural work begins" (the former `structural-scan` gate), not "structural-quality tools only" — `composer-audit` (`composer-audit.md`) is
  already one of these thirteen leaves and is itself a pure security scan (dependency vulnerabilities), so
  excluding this node on a "security vs. structural" distinction wouldn't have been consistent with that
  precedent.
