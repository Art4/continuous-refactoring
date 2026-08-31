# 45 — PHPStan family extracted to its own reference file; `phpstan-level-0-baseline` renamed to `phpstan-level-0`

**What to build:** Two related changes to the PHP tooling tree
(`skills/refactor-scan/references/php-tooling-tree.md`), requested together:

- **Rename `phpstan-level-0-baseline` → `phpstan-level-0`** everywhere the slug is load-bearing: the
  Mermaid diagram, the edges table, the node's own heading, `tooling_tree.py` (`detect_nodes()`, `roadmap()`'s
  level-1 predecessor lookup and Psalm-equivalence check, `_LEAF_MIN_PHP_VERSION`), every affected fixture's
  `expected/roadmap.json` (7 fixtures), `fixtures/php/php-clean/project/docs/refactoring/config.md`'s
  `Fulfilled nodes` bullet, and the test suite (`scripts/test_tooling_tree.py`,
  `scripts/test_trigger_controls.py`). ADRs 0007/0016/0018/0019 and prior `.scratch` ticket history keep the
  old slug — historical protocol, not rewritten.
- **Extract the PHPStan family into `skills/refactor-scan/references/php-tooling-tree/phpstan.md`**,
  following ticket 30's per-node reference-file precedent (`composer.md`, `phpunit.md`), with one deliberate
  deviation: **one file for the whole family** (`phpstan-level-0`, the `phpstan-level-1..10` chain,
  `phpstan-deprecation-rules`, and the cross-cutting *`phpstan` equivalents* section) rather than one file
  per `###` heading — these four sections constantly cross-reference each other and read as one continuous
  story. `php-tooling-tree.md` keeps Name/Tool/Purpose stubs per node plus a single shared pointer line.
- **Fix `tree-walk-prompt.md`'s stale instruction** (found during this ticket, bundled in rather than
  deferred): step 1 said the Fulfilment check is "written under the node's own heading" — true only for
  nodes never extracted. Already silently wrong for `composer`/`phpunit` since ticket 30; extracting a third
  family without fixing it would have compounded the same gap. Now also says to follow the stub's pointer
  when a node has been extracted — fixes the gap retroactively for `composer`/`phpunit` too.

**Why:** the user wants to keep detailing the PHPStan nodes further, starting with getting their prose out
of the already-long `php-tooling-tree.md` *Nodes* section and into its own file (reusing ticket 30's
precedent). The rename was raised alongside it — the `-baseline` suffix was a naming leftover from before
the level chain existed (level 0 was the only PHPStan node then); every other level in the ten-node chain is
named `phpstan-level-N` without a descriptive suffix, so the inconsistency stood out once ticket 43 grew the
chain. A third item the user asked about — consolidating `phpstan-level-1`'s prose with `phpstan-level-2..10`'s
— turned out to already be done (both have shared one combined `###` heading since ticket 18/43, never had
separate per-level prose) and was dropped from scope. Full research trail and design discussion: see
[ADR-0020](../../../docs/adr/0020-phpstan-level-0-rename-and-reference-extraction.md).

**Priority:** medium — user-directed documentation/naming cleanup, no behavior change intended (verified,
see below).

**Status:** done

- [x] Renamed `phpstan-level-0-baseline` → `phpstan-level-0` in `php-tooling-tree.md` (diagram, edges table,
      node heading, all cross-references), `tooling_tree.py`, `scripts/test_tooling_tree.py`,
      `scripts/test_trigger_controls.py`, `fixtures/README.md`, and
      `fixtures/php/php-clean/project/docs/refactoring/config.md`.
- [x] Regenerated/verified all 7 affected `expected/roadmap.json` fixtures
      (`php-clean`, `php-p0-empty`, `php-partial`, `php-project-with-candidates`, `php-psalm`,
      `php-p0-nonempty`, `php-empty`) via `fixtures/harness/run.sh roadmap <name>` — all green.
- [x] New `skills/refactor-scan/references/php-tooling-tree/phpstan.md`: full Fulfilment
      check/Config/MR-scope/Stop-conditions/Verification for `phpstan-level-0`, the `phpstan-level-1..10`
      chain, and `phpstan-deprecation-rules`, plus the `phpstan` equivalents section, moved verbatim (only
      cross-reference wording adjusted for the new file boundary).
- [x] `php-tooling-tree.md`'s *Nodes* section: the four PHPStan sections replaced with three stubs
      (Name/Tool/Purpose each) and one shared pointer line to the extracted file.
- [x] `tree-walk-prompt.md` step 1: instruction corrected to follow an extracted node's stub pointer.
- [x] New ADR: `docs/adr/0020-phpstan-level-0-rename-and-reference-extraction.md`.
- [x] `python3 -m unittest discover -s scripts -p 'test_*.py'` — all pass.
      `python3 scripts/validate_skills.py .` — clean.
- [x] Non-regression check: `php-psalm` fixture's roadmap still unlocks `rector-php-set` (and the rest of the
      Rector family) purely via the Psalm equivalence, without ever proposing a PHPStan level node.

## Comments

> **2026-08-31:** User asked (via `/grill-me`-style back-and-forth) to detail the PHPStan nodes further.
> Research in `.scratch` found no open ticket on this — the prior rounds (18, 43) are done. Clarified scope
> directly with the user: reference-file extraction (one file, not per-node), the level-1/2-10 consolidation
> premise turned out to already be true (dropped), the `phpstan-level-0-baseline` → `phpstan-level-0` rename,
> and bundling in ticket 39's fix (tracked separately — see that ticket's own file). The `tree-walk-prompt.md`
> gap was surfaced during exploration (pre-existing, affects `composer`/`phpunit` too) and the user confirmed
> fixing it here rather than deferring.
