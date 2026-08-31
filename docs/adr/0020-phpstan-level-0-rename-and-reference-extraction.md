# `phpstan-level-0-baseline` renamed to `phpstan-level-0`; PHPStan family extracted to its own reference file

> Renames the node ADR-0018/ADR-0019 discuss as `phpstan-level-0-baseline`; every occurrence of the slug in
> those two ADRs still refers to what is now `phpstan-level-0` — historical ADR text is not rewritten, this
> entry records the rename going forward. Also extends the ticket-30 per-node reference-file precedent
> (`skills/refactor-scan/references/php-tooling-tree/composer.md`, `.../phpunit.md`) to the PHPStan family.

Ticket 43 extended the PHPStan level chain from `phpstan-level-1..3` to `phpstan-level-1..10`. Once the chain
reached ten ordinary level nodes plus the introduce node, `phpstan-level-0-baseline`'s slug stood out: every
other level in the chain is named `phpstan-level-N`, but level 0 alone carried an extra `-baseline` suffix —
a naming leftover from before the chain existed, when this node was the only PHPStan node and its slug
needed to say more about what it did. Raised directly by the user while asking to extract the PHPStan
family's prose into its own reference file (`php-tooling-tree.md`'s *Nodes* section was growing long, and the
PHPStan cluster — introduce node, ten-level chain, deprecation-rules leaf, and the Psalm-equivalence prose —
was its largest single block).

## Decision

**Rename:** `phpstan-level-0-baseline` → `phpstan-level-0`, everywhere the slug is load-bearing (the Mermaid
diagram, the edges table, `tooling_tree.py`'s `detect_nodes()`/`roadmap()`/`_LEAF_MIN_PHP_VERSION`, every
fixture's `expected/roadmap.json`, `fixtures/php/php-clean/project/docs/refactoring/config.md`'s
`Fulfilled nodes` bullet, and the test suite). "PHPStan Level 0" (the node's **Name**, used in issue/MR
titles) is unaffected — it was already just "Level 0", not "Level 0 Baseline". Historical documents (ADR-0007,
ADR-0016, ADR-0018, ADR-0019; `.scratch` ticket history) keep the old slug — they're protocols of decisions
already made, not living documentation.

**Extraction:** a new `skills/refactor-scan/references/php-tooling-tree/phpstan.md`, following ticket 30's
precedent (`composer.md`, `phpunit.md`) with one deliberate deviation — **one file for the whole family**
(`phpstan-level-0`, the `phpstan-level-1`–`10` chain, `phpstan-deprecation-rules`, and the *`phpstan`
equivalents* cross-cutting section), not one file per `###` heading. The level chain already reads as one
continuous story spread across four headings that constantly cross-reference each other (the level nodes'
*Stop conditions* cite the Equivalents section; the Equivalents section cites `phpstan-level-0`'s Psalm
branch); splitting them into separate files would have meant either duplicating that cross-referenced prose
or scattering one story across four files a reader has to open together anyway. `php-tooling-tree.md` keeps
stubs (Name/Tool/Purpose per node, per the established convention) with one shared pointer line to the new
file.

**`tree-walk-prompt.md` fix (bundled in, not deferred):** step 1's instruction — "evaluate its Fulfilment
check, written under the node's own heading" — predates ticket 30 and was never updated once `composer`/
`phpunit` were extracted; it already silently under-served those two nodes. Extracting a third node family
without fixing the same gap would have made it worse for one more entry. The instruction now also says to
follow the stub's pointer when a node has been extracted — a correction that also fixes the pre-existing gap
for `composer`/`phpunit`, not just this ADR's own new extraction.

## Considered Options

- **Rename only, no extraction; extraction only, no rename.** Rejected as sequencing, not substance: both
  were requested together, and doing the rename first (before extracting) meant the new reference file was
  authored with the final name from the start, rather than extracting the old name and immediately touching
  it again.
- **Split into `phpstan-level-0.md` / `phpstan-level-1-10.md` / `phpstan-deprecation-rules.md`** (strict 1:1
  with `php-tooling-tree.md`'s `###` headings, matching `composer`/`phpunit` exactly). Rejected: the
  Equivalents section isn't itself a node with its own heading-per-file home, and splitting the level chain
  from the node whose Psalm-equivalence branch it depends on (`phpstan-level-0`) would have forced a reader
  chasing "why doesn't the level chain apply under Psalm" through three files instead of one.
- **Rewrite ADR-0007/0016/0018/0019 to use the new slug.** Rejected: those are historical decision records;
  rewriting them to match a later rename would misrepresent what was actually decided at the time and set a
  precedent of editing past ADRs whenever a later one renames something they discuss.
- **Leave `tree-walk-prompt.md`'s stale wording alone, file a separate ticket for it.** Rejected by the user
  directly: extracting a third node family would compound the same gap a fourth time; fixing it once, here,
  closes it for every extraction made so far and going forward.

## Consequences

`php-tooling-tree.md`'s *Nodes* section shrinks by roughly 80 lines (three stubs plus a pointer replacing
four full node sections); `skills/refactor-scan/references/php-tooling-tree/phpstan.md` is the new
self-contained home for PHPStan's Fulfilment checks, Config, MR scope, Stop conditions, and the Psalm
equivalence. No behavior change: `tooling_tree.py` only parses the edges table, never node prose, so the
extraction is docs-only (confirmed by ticket 30 and re-confirmed here); the rename touches code, but is a
pure identifier substitution with no logic change, verified by running every PHP fixture's `roadmap` check
against the regenerated `expected/roadmap.json` files. `tree-walk-prompt.md`'s fix is retroactive: a
tree-walk that previously mis-served `composer`/`phpunit` (by looking for their Fulfilment check under the
stub heading instead of following the pointer) now reads correctly for all three extracted node families.

> **2026-08-31 (follow-up correction, before merge):** the "one shared pointer line after the group's last
> stub" shape above was reworked once a fourth node family (ADR-0021) made the pattern's cost visible: a
> reader landing on `phpstan-level-1`'s stub had no pointer of its own, only an implicit "the file named
> three stubs down applies to me too." Each of the three PHPStan stubs now carries its own `Full definition
> (...): phpstan.md` line instead — same target file, but no node's stub depends on a neighbor's proximity
> to know where its own definition lives. ADR-0021's `rector.md` cluster had the same shared-pointer shape
> and got the same fix in the same pass; its `psalm.md` cluster's two nodes happened to already carry
> individual pointers (not adjacent in the parent doc, so a single shared line was never written for them),
> which is what made the inconsistency visible in the first place.
