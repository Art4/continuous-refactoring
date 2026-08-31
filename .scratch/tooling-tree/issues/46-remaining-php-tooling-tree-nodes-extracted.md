# 46 — Remaining PHP tooling-tree nodes extracted to reference files

**What to build:** Extract all fifteen PHP-tree nodes still inline in
`skills/refactor-scan/references/php-tooling-tree.md` (everything except `composer`, `phpunit`, and the
PHPStan family, already done in ticket 30 and ticket 45) into their own reference files under
`skills/refactor-scan/references/php-tooling-tree/`, following ticket 30's stub/pointer convention:

- Nine new files: `ci-runner.md`, `php-minimal-version.md`, `php-cs-fixer.md`, `test-runner-if-missing.md`,
  `composer-audit.md`, `static-code-analyzer.md`, `php-structural-scan.md` (one node each), plus two
  clusters extracted as a single shared file each, following ADR-0020's PHPStan-family precedent:
  `psalm.md` (`psalm` + `psalm-taint-analysis`) and `rector.md` (`rector-php-set`, `rector-dead-code`,
  `rector-type-coverage`, `rector-code-quality`, `rector-phpunit-set`, `rector-early-return`).
- `php-tooling-tree.md` keeps a Name/Tool/Purpose stub per node, and **every node's stub carries its own
  pointer line to its file** — even the six `rector.md` nodes and the three `phpstan.md` nodes, which
  originally shared one collected pointer line each (see 2026-08-31 follow-up comment).
- Every cross-reference that pointed at moved content via "above"/"below" now names the file explicitly
  where the content actually moved elsewhere; references between nodes that landed in the same file keep
  their original "above"/"below" wording.

Full design and rationale for the two clusters and the two standalone plumbing nodes (`static-code-analyzer`,
`php-structural-scan`): [ADR-0021](../../../docs/adr/0021-remaining-php-tooling-tree-nodes-extracted.md).

**Why:** the user asked to continue extracting tooling-tree nodes into reference files after ticket 45's
PHPStan extraction. Research confirmed no other open ticket claims this work, and the doc's *Nodes*
preamble names no required order — user confirmed doing all fifteen remaining nodes in one round (not
node-by-node as ticket 30 originally deferred), file grouping 1:1 except for the two tightly cross-referenced
clusters, and one ticket/one commit for the whole round.

**Priority:** medium — user-directed documentation continuation, no behavior change (verified, see below).

**Status:** done

- [x] Nine new files under `skills/refactor-scan/references/php-tooling-tree/` — see ADR-0021 for the
      per-file node list and grouping rationale.
- [x] `php-tooling-tree.md`'s *Nodes* section: all fifteen remaining nodes reduced to Name/Tool/Purpose
      stubs, each with its own pointer line (no shared pointer even within `rector.md`); node order in the
      document unchanged (only content moved, not position).
- [x] Cross-references between nodes in different files updated to name the file (`psalm.md` ↔
      `phpstan.md`, `rector.md` ↔ `phpstan.md`/`psalm.md`/`php-cs-fixer.md`/`phpunit.md`,
      `composer-audit.md`/`php-structural-scan.md`'s shared thirteen-leaf list); references within the same
      file kept as plain "above"/"below".
- [x] New ADR: `docs/adr/0021-remaining-php-tooling-tree-nodes-extracted.md`.
- [x] `python3 -m unittest discover -s scripts -p 'test_*.py'` — 199/199 pass (no code touched, no new
      cases needed — this ticket is docs-only). `python3 scripts/validate_skills.py .` — clean.
- [x] All 7 PHP fixtures re-verified via `fixtures/harness/run.sh roadmap <name>` — unchanged, as expected
      for a docs-only change (`tooling_tree.py` only parses `## Edges`, never node prose).

## Comments

> **2026-08-31:** Direct follow-up to ticket 45 on the same branch/session. User asked to continue
> extracting nodes; scope (all fifteen remaining, one ticket, 1:1 files except two cross-referenced
> clusters) confirmed via a short round of clarifying questions before implementation.

> **2026-08-31 (follow-up correction, before merge):** the first pass gave `rector.md`'s six nodes one
> shared pointer line after the last stub (`rector-early-return`), mirroring `phpstan.md`'s original shape.
> User asked directly for every node to always link its own reference file, not a collected pointer under
> several nodes. Reworked so each of the six `rector.md` stubs carries its own `Full definition` line
> naming what that specific node's section covers; `phpstan.md`'s three stubs got the same fix in the same
> pass (ADR-0020's own follow-up note). `psalm.md`'s two nodes already had individual pointers going in —
> they aren't adjacent in the parent doc, so no shared line had been written for them — which is what made
> the `rector.md`/`phpstan.md` inconsistency visible.
