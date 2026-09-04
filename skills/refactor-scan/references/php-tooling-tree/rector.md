# Rector (`rector-php-set`, `rector-dead-code`, `rector-type-coverage`, `rector-code-quality`, `rector-phpunit-set`)

Nodes on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**). One file for the whole Rector family (a deliberate exception to this directory's usual one-file-per-node shape — see `php-tooling-tree.md`'s *Nodes* preamble, and `phpstan.md`'s own opening note for the precedent): `rector-php-set` is the hub the other four read their static-analyzer gate through, and `rector-type-coverage`/`rector-phpunit-set` explicitly point at sibling entries below for their own caveats.

### `rector-php-set`

- **Name:** Rector: PHP Set
- **Tool:** Rector (versioned PHP-upgrade rule set, e.g. `LevelSetList::up_to_php_8x`)
- **Purpose:** adopt Rector's own PHP-version-targeted rule set — the common gate the other Rector
  rule-set nodes below wait on, mirroring how `phpstan-level-0`/`psalm` gate the family today.
- **Fulfilment check:** the PHP-version rule set enabled in `rector.php`/`rector.neon` and fully applied —
  no remaining rule findings.
- **MR scope:** adopted in levels, one MR per target PHP version bump; keeps PHPStan green by shrinking
  the baseline within the same MRs (same shape as `rector-dead-code`).
- **Required-any parents:** `phpstan-level-0`, `psalm` (both `phpstan.md`/`psalm.md`) — either fulfilled
  unlocks this node. Previously this was a single `required` parent on `phpstan-level-0` alone
  (relying on that node's own Psalm-equivalence branch to also cover the Psalm path implicitly); reading
  the `required-any` group directly instead makes the OR explicit at the edge level and is now the gate on
  which static-analysis path was chosen for this node's own two direct children —
  `rector-dead-code`/`rector-code-quality` (see those nodes' own **Required parent**
  lines below) — read it transitively via their required parent on this node. `rector-type-coverage`/
  `rector-phpunit-set` are *not* among them any more (a later restructuring made them wait on sibling Rector
  nodes instead — see those nodes' own entries below for why they no longer transitively depend on this gate
  at all). No `php-cs-fixer` (`php-cs-fixer.md`) recommended parent (unlike the sibling Rector nodes below)
  — decided directly with the user; this node is the styling-order exception in the family.
- **Recommended parent:** `php-minimal-version` (`php-minimal-version.md`) — this node's rule set rewrites
  code to target syntax for a PHP version composer.json may not even declare support for yet; closes the
  one gap where this family previously had no dependency on the runtime floor at all.

### `rector-dead-code`

- **Name:** Rector: Dead Code Set
- **Tool:** Rector (dead-code suite)
- **Purpose:** remove dead code with rules whose changes are safe to review early.
- **Fulfilment check:** dead-code suite enabled and fully applied — no remaining rule findings.
- **MR scope:** adopted in levels, one MR per level; keeps PHPStan green by shrinking the baseline within the same MRs. Proposed once `rector-php-set` is fulfilled **and** `php-cs-fixer` (`php-cs-fixer.md`) has been decided (fulfilled or rejected) — a still-undecided `php-cs-fixer` withholds this node so its dead-code rewrites don't land unstyled; a rejected `php-cs-fixer` still releases it, it just never gets styled output. Does not carry its own direct required parent on `phpstan-level-0` — `rector-php-set`'s own `required-any` gate (see its entry above) already covers which static-analysis path was chosen; duplicating it here would be redundant.

### `rector-type-coverage`

- **Name:** Rector: Type Coverage Set
- **Tool:** Rector (typing suites)
- **Purpose:** raise declared type coverage progressively.
- **Fulfilment check:** typing suites enabled and fully applied at the agreed coverage degree.
- **MR scope:** adopted in levels, one MR per level; keeps PHPStan green via baseline shrinking. Proposed once `rector-dead-code` **and** `rector-code-quality` have both been decided **and** both `php-cs-fixer` and `phpstan-level-3` (`phpstan.md`) have been decided (fulfilled or rejected) — without strict analysis its rewrites are hard to review, without `php-cs-fixer` its output cannot be styled, without dead code removed or control flow flattened first its type-coverage rewrites touch messier code, so this node waits on all three pairs. Any one being rejected instead of fulfilled still releases this node, it just goes in without that particular benefit. The `phpstan-level-3` threshold stays put here even though the level chain itself now reaches `phpstan-level-10` — level 3 was already judged "strict enough" for reviewable Rector rewrites. (`rector-code-quality` replaced `rector-early-return` in this gate when that node was retired — see `rector-code-quality`'s own entry below for why it's the one now carrying the "control flow flattened first" prerequisite.)
- **No required parent** (as of the `rector-dead-code`/`rector-code-quality` restructuring above) — unlike
  every other node in this family, nothing here directly or transitively requires `rector-php-set` (or,
  through it, that a static analyzer was chosen) to be *fulfilled*; only decided recommended parents gate
  it, and a rejected recommended parent still releases its child same as any other recommended edge in
  this tree (`php-tooling-tree.md`'s *Nodes* preamble). In
  principle this node could become proposable with `rector-dead-code`/`rector-code-quality` both rejected
  and `rector-php-set` never touched at all — an edge case, not a new category of gap (nothing in this tree
  validates that a rejected node was ever reachable first), but worth naming plainly rather than implying a
  guarantee that no longer holds.

### `rector-code-quality`

- **Name:** Rector: Code Quality Set
- **Tool:** Rector (code-quality suite)
- **Purpose:** apply Rector's code-quality rewrites (readability/idiom improvements beyond dead-code
  removal) — including flattening nested conditionals into early returns. Rector's own dedicated
  early-return rule set (`SetList::EARLY_RETURN`) ships empty upstream; its rules were folded into this
  set instead, so this tree no longer models early-return adoption as a separate node.
- **Fulfilment check:** code-quality suite enabled and fully applied — no remaining rule findings.
- **MR scope:** adopted in levels, one MR per level; keeps PHPStan green by shrinking the baseline within
  the same MRs.
- **Required parent:** `rector-php-set` (above).
- **Recommended parent:** `php-cs-fixer` (`php-cs-fixer.md`) — settle styling before these rewrites land, same rationale/
  mechanics as `rector-dead-code`'s own `php-cs-fixer` recommended parent.

### `rector-phpunit-set`

- **Name:** Rector: PHPUnit Set
- **Tool:** Rector (PHPUnit-specific rule set)
- **Purpose:** modernize PHPUnit test code (assertion methods, annotations → attributes, etc.) via Rector's
  PHPUnit rule set.
- **Fulfilment check:** PHPUnit suite enabled and fully applied — no remaining rule findings.
- **MR scope:** adopted in levels, one MR per level.
- **Required parent:** `phpunit` (`phpunit.md`) — this node rewrites PHPUnit-specific code, so it needs PHPUnit (or its
  fait-accompli equivalent, Pest, which the `phpunit` node already recognizes) actually adopted first. No
  longer requires `rector-php-set` directly either (a later restructuring moved that gate to
  `rector-code-quality`'s recommended parent above) — same "no required tie to the static-analyzer choice
  any more" situation as `rector-type-coverage` above, see that node's entry for the caveat.
- **Recommended parents:** `rector-code-quality` (above), `php-cs-fixer` — settle code-quality rewrites first, same
  non-blocking ordering rationale as `rector-type-coverage`'s new recommended parents above.
