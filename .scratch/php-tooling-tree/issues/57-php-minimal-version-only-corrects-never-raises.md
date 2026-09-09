# 57 — `php-minimal-version` only corrects an already-true floor, never raises it

**What to build:** Redesign `php-minimal-version`'s fulfilment check and edge placement so it can only
ever propose a **Floor correction** (bringing `composer.json`'s declared PHP floor in line with syntax
the codebase already demonstrably contains) — never a **Floor raise** (committing the application to a
newer PHP than its own code currently requires, a real **Breaking change**, ADR-0004's binding "no
breaking changes" rule). The three new glossary terms above land in `CONTEXT.md`.

- **New fulfilment check:** `composer.json`'s declared PHP floor ≥ the PHP-version rule set
  `rector-php-set` has fully applied (`rector.md`'s own node entry — its Fulfilment check already
  reads "no remaining rule findings", so once fulfilled, the codebase genuinely contains that
  version's syntax). Drops both of today's two rules entirely: (a) a blocked leaf's own minimum PHP,
  (b) the highest PHP version a quality-tooling CI job happens to run under — neither is a legitimate
  signal for raising `require.php` at all, since a `require-dev` tool's own PHP floor never needs to
  be reflected in the package's declared floor under Composer's own dependency-resolution semantics
  (only the platform actually running `composer install` needs to satisfy it).
- **Edge reversed:** `php-minimal-version → rector-php-set | recommended` removed. New:
  `rector-php-set → php-minimal-version | required` — the node is proposable only once `rector-php-set`
  is genuinely *fulfilled* (a level truly landed), not merely decided.
- **Required parents narrow to one:** `is-php-project` and `ci-runner` drop as direct required
  parents (both already transitive through `rector-php-set`'s own chain) — mirrors how
  `rector-dead-code` needs only `rector-php-set` directly.
- **Slug unchanged** (`php-minimal-version`) — legacy-todo's own `bookkeeping.md` already carries
  `php-minimal-version (#167)` as a historical `Fulfilled nodes` entry; renaming would be
  disproportionate to that (and any other target's) existing reference, matching this suite's own
  established precedent for not renaming a settled, widely-referenced slug over a meaning refinement.
- **`Blocked by: PHP >= X.Y.Z` reversal detection kept, read-only** — an existing out-of-scope entry
  written under the old design (e.g. legacy-todo's own real `Blocked by: PHP >= 8.3.0` from its PR
  #169) still reverses correctly if the floor it names is later satisfied. No node under the new
  design ever writes a new entry of this shape — a premature MR can no longer be proposed in the
  first place, the required-parent gate does that job instead.
- **MR scope unchanged, still narrow:** a `composer.json` edit only, no added verification step —
  `rector-php-set`'s own fulfilment already means "fully applied, no remaining findings", and the
  resulting MR runs through the loop's ordinary CI gate like any other.
- **Housekeeping field, re-triggering property, ADR-0037's "day-one-fulfilled" exception:** all
  unchanged in substance — the exception (loop-config's first MR carries the Housekeeping line when
  this node is already fulfilled the moment it's first evaluated) still applies exactly as documented,
  it's just now keyed to the new signal.
- **The original motivating scenario (a target's dev tooling running in a separate, newer-PHP Docker
  container than the app's own declared floor) is no longer addressed by this node at all** — under
  Composer's own semantics that was never actually a gap needing a floor raise; a legitimate, durable
  pattern, not a problem to surface. Dropped, not replaced.
- **First-ever ADR for this node** — its original introduction (ticket 35) shipped straight from a
  `/grill-me` session with no ADR of its own; this correction becomes the first, briefly recapping the
  original design before recording this one.

**Why:** Surfaced while reviewer-loop-watching `Art4/legacy-todo`: PR #168 raised `require.php` from
`>=7.4.0` to `>=8.3.0` while the app's own runtime/README still targeted 7.4 (a container-level PHP
upgrade was an explicit, separate, not-yet-done backlog item) — a real breaking change proposed under
the refactor label, rejected by the human. Investigating why the tree ever proposed it found the root
cause one level deeper than the single incident: the node's own two fulfilment-check rules both
measure what PHP version *dev tooling* needs, never what the *application's own code* needs — the
question `require.php` is actually supposed to answer. Settled via `/grill-with-docs`
(`grilling` + `domain-modeling`), several rounds, growing out of the legacy-todo reviewer-loop
findings log.

**Blocked by:** none.

**Priority:** medium — not urgent (no target repo is currently mid-incident on this), but a real,
previously-undetected gap in a foundational-rule guardrail, not cosmetic.

**Status:** done

- [x] `tooling_tree.py`: removed the two old fulfilment-check rules and their supporting detection
  (`_quality_tooling_ci_php_versions()`, `_job_blocks()`, `_extract_php_versions()`,
  `_QUALITY_TOOL_NEEDLES`, `_GITLAB_RESERVED_TOP_KEYS`, `_php_minimal_version_gap()` — nothing else
  called any of them); new `_rector_php_set_level()` reads `rector-php-set`'s own applied-level state
  directly, invoked from inside the existing rector-detection block (php-minimal-version's own
  `set_node` call now runs after, not before, rector-php-set's). `php_floor_precheck()` and
  `_LEAF_MIN_PHP_VERSION` untouched — a separate mechanism gating the five leaf tools, not this node's
  own fulfilment.
- [x] `php_version_reversal_findings()`/the `Blocked by` reversal-detection machinery: untouched,
  generic across any rejected node — confirmed still reads correctly against a pre-existing old-style
  entry; no code path writes a new one.
- [x] Edge table (`php-tooling-tree.md`): removed `php-minimal-version → rector-php-set | recommended`
  row and diagram line; added `rector-php-set → php-minimal-version | required` row and diagram line;
  removed the `is-php-project → php-minimal-version`/`ci-runner → php-minimal-version` required rows.
- [x] `php-minimal-version.md`: rewritten — Purpose/Fulfilment check/Re-triggering to the new signal,
  the old "explicitly out of scope: consolidating a separate tooling container" bullet dropped
  entirely (the scenario it referred to isn't this node's concern in any form now).
- [x] `rector.md`: `rector-php-set`'s own entry gains `php-minimal-version` as a required child,
  replacing the old recommended-parent language pointing the other way.
- [x] `CONTEXT.md`: three new entries — **Floor correction**, **Floor raise**, **Breaking change**.
- [x] New ADR (0041) — recaps ticket 35's original design, then records this correction.
- [x] Tests: `PhpMinimalVersionTests` rewritten for the new fulfilment signal and edge shape (fulfilled
  once the level is applied and the floor already matches; proposable once the level is applied and
  the floor lags; permanently unproposable while `rector-php-set` itself is unfulfilled or rejected; a
  `require-dev` tool's own PHP floor never creates a gap). `PhpVersionReversalTests` untouched — not
  specific to this node. Full suite green (275 tests).
- [x] `.changelog.d/` fragment.
- [x] Fixture fallout: `php-clean`'s own `composer.json` floor (`^8.1`) was genuinely behind its
  `rector.php`'s already-applied `UP_TO_PHP_82` — a real, previously-invisible gap the new signal
  correctly caught; bumped to `^8.2` (a genuine Floor correction) to keep that fixture's own "nothing
  but structural-scan left" negative-control property intact. All 8 `expected/roadmap.json` snapshots
  regenerated; `fixtures/harness/run.sh roadmap` verified exact-match on all 8, `tier2` spot-checked.

## Comments

> **2026-09-08:** Filed after a `/grill-with-docs` session (German — `grilling` + `domain-modeling`),
> growing directly out of the `Art4/legacy-todo` reviewer-loop findings log's PR #168 escalation
> (rejected floor raise) and the follow-on finding that the tree itself has no guardrail against a
> tooling-tree node proposing a breaking change, despite ADR-0004's binding rule. Key fact found during
> grilling (not asked of the user — established from Composer's own dependency-resolution semantics):
> a `require-dev` tool's own PHP-version requirement never needs to be reflected in a package's
> declared `require.php` — only the platform actually running `composer install` needs to satisfy it —
> so both of the node's original two fulfilment-check rules were answering the wrong question from the
> start, independent of the breaking-change framing. `rector-php-set`'s own existing fulfilment check
> ("PHP-version rule set applied, no remaining findings") turned out to already be the clean,
> deterministic, already-built signal this node needed — reusing it (with the edge direction reversed)
> needed no new detection machinery. User confirmed the full design across several rounds, closing with
> "passt so."
