# `php-minimal-version` only corrects an already-true PHP floor, never raises it

> First ADR for this node. Its original introduction (ticket 35, `.scratch/php-tooling-tree/issues/
> 35-php-upgrade-recommendation-node.md`) shipped straight from a `/grill-me` session with no ADR of
> its own — recapped briefly below before this correction.

## Original design (ticket 35, 2026-08-30/31)

Observed on `Art4/legacy-todo`: the target stayed pinned to an old PHP version throughout, and
adopting PHPStan/Rector was solved by running them in a second, parallel higher-PHP Docker container
rather than by raising the target's own declared floor — nothing in the tree ever surfaced that
mismatch as a candidate. The node shipped with two fulfilment-check rules: (a) the minimum-ever PHP
version of any leaf `php_floor_precheck()` currently reports blocked, (b) the highest PHP version
tested by a CI job that invokes a quality tool (PHPStan/Psalm/Rector/php-cs-fixer). Either rule firing
proposed bumping `composer.json`'s `require.php` to match.

## Decision

Both original rules are wrong, independent of anything else: **a `require-dev` tool's own PHP-version
requirement never needs to be reflected in a package's declared `require.php` at all.** Composer's
dependency resolution for `require-dev` packages only needs the platform actually running
`composer install` (or a pinned `config.platform.php`) to satisfy them — never the project's own
declared floor. A repo can legitimately run its quality tooling under a newer PHP Docker image in CI
while the shipped application still targets, and is tested against, an older floor; that was never a
gap needing a fix. Both rules were answering "what PHP does my dev tooling need," never "what PHP
does my application's own code need" — the question `require.php` is actually supposed to answer.

This surfaced while reviewer-loop-watching `Art4/legacy-todo`: PR #168 raised `require.php` from
`>=7.4.0` to `>=8.3.0` while the app's own runtime/README still targeted 7.4 — a real
**Breaking change** (`CONTEXT.md`) proposed under the refactor label, in direct tension with this
suite's own binding rule (`docs/adr/0004-foundational-refactoring-rules.md`: "A refactor preserves
observable behavior; a behavior change routes to the normal feature/bug path instead, never shipped
under the refactor label"). That rule already existed (2026-08-20) when ticket 35 was designed
(2026-08-30/31) — the original grilling session never checked the new node against it.

**New fulfilment check:** `composer.json`'s declared PHP floor ≥ the PHP-version rule set
`rector-php-set` (`skills/refactor-scan/references/php-tooling-tree/rector.md`) has itself applied.
`rector-php-set`'s own fulfilment already means "fully applied, no remaining findings" — once true,
the codebase genuinely contains that version's syntax, so correcting `require.php` to match is a
**Floor correction** (`CONTEXT.md`), not a **Floor raise**: metadata catching up to reality, nothing
observable changes. No new detection machinery needed — `rector-php-set`'s own applied level (parsed
from its `LevelSetList::UP_TO_PHP_XY` constant) is the only signal.

**Edge reversed:** `php-minimal-version → rector-php-set | recommended` (the original direction —
floor gates the rewrite) is removed. New: `rector-php-set → php-minimal-version | required` — the
node is only proposable once `rector-php-set` is genuinely fulfilled, not merely decided. A rejected
`rector-php-set` leaves `php-minimal-version` permanently unproposable, matching the tree's ordinary
required-parent-rejection-closes-everything-beneath-it convention; no special-casing needed.

**Required parents narrow to one.** `is-php-project` and `ci-runner` — both needed for the old rule
(b)'s CI-job scan — drop as direct required parents; both stay reachable transitively through
`rector-php-set`'s own chain, same shape `rector-dead-code` already uses (only `rector-php-set`
directly).

**The original motivating scenario (dev tooling in a separate, newer-PHP container than the app's own
declared floor) is dropped, not replaced with a different check.** Under Composer's own semantics that
was never actually a gap — a legitimate, durable pattern, not a problem to surface. No node in this
tree addresses it in any form after this change.

**Slug unchanged** (`php-minimal-version`) despite the sharpened meaning — `Art4/legacy-todo`'s own
`bookkeeping.md` already carries `php-minimal-version (#167)` as a historical `Fulfilled nodes` entry;
renaming would be disproportionate to that existing reference, the same reasoning this suite already
applied when it kept "tooling tree" as a name despite "Safety Net" becoming the human-facing framing
elsewhere (ADR-0039).

**`Blocked by: PHP >= X.Y.Z` reversal detection kept, read-only.** A target's own pre-existing
out-of-scope entry from before this change (e.g. `Art4/legacy-todo`'s real `Blocked by: PHP >= 8.3.0`
from its PR #169) still reverses correctly if the floor it names is later satisfied — the detection
function is generic across any rejected node, not specific to how this node used to reach that state.
No path under the new design ever writes a new entry of this shape; the required-parent gate makes a
premature proposal impossible in the first place.

**MR scope unchanged, still narrow:** a `composer.json` edit only, no added verification step —
`rector-php-set`'s own fulfilment is already sufficient proof, and the resulting MR runs through the
loop's ordinary CI gate like any other.

## Considered Options

- **Flag the resulting MR as a breaking change instead of redesigning the signal.** Rejected — doesn't
  fix the underlying problem (the fulfilment check still measures the wrong thing), just adds a label
  on top of a proposal that shouldn't exist as an autonomous candidate at all.
- **Split into "declared floor doesn't match reality" vs. "actually raise what's targeted", keep both
  paths in the tree.** Considered during grilling; converged to only the first case ever being
  legitimate — there's no code-driven signal that would make an autonomous "raise beyond what the code
  needs" proposal correct, so a second path was never actually buildable, just a category with nothing
  real to put in it.
- **Drop the node from the tree entirely, surface only a non-proposing observation (`MR scope: none`,
  like `psalm`).** Rejected — `rector-php-set` already provides a genuine, deterministic, safe trigger;
  losing the ability to auto-propose the correction would be strictly worse with no compensating
  benefit once the breaking-change path is closed off another way.
- **Keep rule (a) (blocked-leaf minimum), drop only rule (b).** Rejected — rule (a) has exactly the
  same defect as rule (b): a `require-dev` tool's own minimum PHP is not a legitimate signal for the
  package's declared floor either, under the same Composer-semantics finding.
- **Also surface "you're running two PHP versions" as a general observation, separate from this
  node.** Considered, not pursued — no compensating value once the underlying scenario is understood
  as a legitimate, durable pattern rather than a problem; would be inventing a new concern with no
  concrete need behind it.

## Consequences

`tooling_tree.py`: `_quality_tooling_ci_php_versions()` and its supporting helpers (`_job_blocks()`,
`_extract_php_versions()`, `_QUALITY_TOOL_NEEDLES`, `_GITLAB_RESERVED_TOP_KEYS`) removed outright —
nothing else called them. `_php_minimal_version_gap()` replaced by a much smaller
`_rector_php_set_level()` (parses `rector.php`/`rector.neon`'s `LevelSetList::UP_TO_PHP_XY` constant),
invoked from inside the existing rector-detection block rather than `php-minimal-version`'s own
(now-removed) standalone block — the node's fulfilment now runs after, not before, `rector-php-set`'s
own detection in `detect_nodes()`. `php_floor_precheck()`/`_LEAF_MIN_PHP_VERSION` (the five-leaf
precheck) and `php_version_reversal_findings()` (the reversal-detection machinery) are both untouched
— separate, generic mechanisms neither specific to nor broken by this change.

`CONTEXT.md` gains three entries: **Floor correction**, **Floor raise**, **Breaking change** — the
last promotes ADR-0004's already-binding rule into the domain glossary for the first time, so a future
grilling session checking new tooling-tree behavior against it doesn't have to already know to go
looking in a skill-reference file.

Fixture fallout: any `fixtures/php/*` project exercising the old two-rule fulfilment check or the old
edge direction needs updating; `expected/roadmap.json` snapshots regenerated as needed per
`CONTRIBUTING.md`'s rule for tooling-tree-parser changes.
