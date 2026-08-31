# Remaining PHP tooling-tree nodes extracted to reference files

> Continues ADR-0020's PHPStan extraction with the rest of `php-tooling-tree.md`'s `## Nodes` section, using
> the same ticket-30 stub/pointer convention. `skills/refactor-scan/references/php-tooling-tree.md` now holds
> only stubs (Name/Tool/Purpose per node) plus its two non-node cross-cutting sections and the *Nodes*
> preamble — every node's Fulfilment check/MR scope lives in `php-tooling-tree/`.

Ticket 30 established one-file-per-node extraction, deferred "one node at a time." ADR-0020 (ticket 45)
deviated once, for the PHPStan family, because its four sections constantly cross-referenced each other.
With `composer`, `phpunit`, and the PHPStan family already extracted, fifteen nodes remained inline, several
of them the doc's longest entries (`psalm` ~39 lines, `rector-php-set` ~23 lines) — worth finishing in one
pass rather than the doc staying a mix of stubs and full prose indefinitely.

## Decision

Extract all fifteen remaining nodes into nine new files under `skills/refactor-scan/references/php-tooling-tree/`:
`ci-runner.md`, `php-minimal-version.md`, `php-cs-fixer.md`, `test-runner-if-missing.md`,
`composer-audit.md`, `static-code-analyzer.md`, `php-structural-scan.md` — one node each — plus two clusters
extracted the way ADR-0020 did the PHPStan family:

- **`psalm.md`** — `psalm` and `psalm-taint-analysis`. `psalm-taint-analysis`'s Co-presence caveat and
  `psalm`'s own Co-presence bullet already cross-referenced each other before extraction; splitting them
  into separate files would have meant each pointing out to the other rather than reading as one story.
- **`rector.md`** — `rector-php-set`, `rector-dead-code`, `rector-type-coverage`, `rector-code-quality`,
  `rector-phpunit-set`, `rector-early-return`. `rector-php-set` is the hub the other three (`rector-dead-code`/
  `rector-code-quality`/`rector-early-return`) read their static-analyzer gate through transitively;
  `rector-type-coverage` and `rector-phpunit-set` each explicitly cite the other's entry for a shared
  caveat. Same reasoning as the PHPStan level chain: one family, one file.

`static-code-analyzer` and `php-structural-scan` — both pure-plumbing nodes that sit *between* two other
clusters rather than belonging to either — stay standalone rather than folded into `psalm.md` or `rector.md`:
`static-code-analyzer` gates `phpstan-level-0` and `psalm` equally; `php-structural-scan` aggregates all
thirteen `resolved` leaves across every cluster.

Every stub keeps Name/Tool/Purpose inline (the established shape); every node — including each node inside
a shared cluster file — carries its own `Full definition (...): <file>.md` pointer line naming exactly what
that node's own section covers (e.g. `rector-early-return`'s pointer names "Fulfilment check, MR scope,
Required parent, Recommended parent", not "see the whole family"), so no stub depends on a neighboring
stub's proximity to know where its own definition lives. Cross-reference prose that pointed at another
node's content via "above"/"below" now names the file when that content moved to a different file
(`psalm.md` ↔ `phpstan.md`'s *Equivalents* section, `rector.md` ↔ `phpstan.md`/`psalm.md`'s `required-any`
parents, `composer-audit.md`/`php-structural-scan.md`'s shared thirteen-leaf list) and keeps plain
"above"/"below" only where both sides of the reference stayed in the same file.

> **2026-08-31 (follow-up correction, before merge):** the Decision text above originally read "a node
> whose file covers more than one node states so in a single shared pointer line" (one pointer after the
> cluster's last stub, mirroring how `phpstan.md`'s three stubs first shipped in ADR-0020). The user asked
> for every node to always link its own reference file rather than several nodes sharing one collected
> pointer — `rector.md`'s six stubs (which had the single-shared-pointer shape) and `phpstan.md`'s three
> were reworked to each carry an individual pointer; `psalm.md`'s two nodes already had individual pointers
> (they aren't adjacent in the parent doc, so a shared line was never written for them), which is what
> surfaced the inconsistency. Reworded above to match what's actually in `php-tooling-tree.md` now.

## Considered Options

- **Strict one-file-per-node, no exceptions** (revert to ticket 30's original rule, splitting `psalm`/
  `psalm-taint-analysis` and all six Rector nodes into eight further files). Rejected: would have meant
  `rector-type-coverage.md` and `rector-phpunit-set.md` each holding a one-sentence pointer into the other's
  file for a caveat that reads as a single idea, and `rector-php-set.md` explaining three siblings' gating
  logic that a reader would then have to open three more files to see stated. ADR-0020 already established
  that a tightly cross-referenced cluster reads better as one file.
- **Multiple tickets, one per node or per cluster** (closer to ticket 30's "one node, one ticket").
  Rejected by the user directly for this round: the whole remaining set was requested together, and
  splitting the bookkeeping into many tickets for a mechanical, non-controversial continuation of an
  already-decided pattern would have added overhead without a corresponding decision to isolate.
- **Leave `static-code-analyzer` and `php-structural-scan` inline** (too small/plumbing-only to be worth a
  file). Rejected for consistency: the user asked for all fifteen remaining nodes: leaving two inline while
  extracting everything else would make `php-tooling-tree.md`'s *Nodes* section a mix of stubs and two
  leftover full entries for no reason a future reader could infer from the doc itself.

## Consequences

`php-tooling-tree.md`'s *Nodes* section shrinks from ~330 lines to ~190 lines (stubs plus the *PHP floor
precheck* and `require-dev` security advisories sections, which are not nodes and stay put). Every PHP-tree
node's full definition now lives under `php-tooling-tree/`, closing out ticket 30's original deferred scope
(its own stale candidate list — written when the level chain still ran 0–3 and before `psalm`/`rector-php-set`
existed — is now moot without editing that historical ticket). No behavior change: `tooling_tree.py` only
parses `## Edges`, never node prose (reconfirmed here as it was for ADR-0020); verified against all 7 PHP
fixtures' `roadmap` checks, unchanged.
