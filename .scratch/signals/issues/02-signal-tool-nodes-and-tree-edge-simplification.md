# 2 — Signal-producing tools become tooling-tree nodes (non-gating); three edge simplifications

**What to build:** Resolve the chicken-and-egg problem between "adopt a tool before scanning" and
"scan first, discover missing factors" the deterministic-tools-first principle creates: signal-
producing tools (PHPMD, secret detection) become real, adoptable tooling-tree nodes — not just
documentation in `signals.md` — but carry **no** `resolved` edge into `structural-scan`/
`php-structural-scan`. The existing Safety Net gate is untouched in shape; these new nodes compete for
adoption through the ordinary scan/prioritize proposal cycle like any other node, and once fulfilled,
enrich `signals.md`'s factor catalogue with real tool output via a new node-level **Signal** field.
Alongside this, three edge simplifications to the existing PHP tree, found and verified while
designing the new nodes (test-runner-if-missing dropped from the Safety Net leaves, php-cs-fixer's
gating route simplified, the PHPStan level-chain leaf lowered from 10 to 5).

**Why:** Triggered by the "Signals" work (`signals` ticket 1, PR #65) needing tool-backed evidence
instead of only git-log/manual-judgment heuristics, and by the deterministic-tools-first principle
implying these tools should exist as real adoptable infrastructure, not just be described. Settled via
`/grill-with-docs`, three rounds — the edge simplifications surfaced from close reading of the actual
edge table while scoping where the new nodes should attach, not as a separate motivation.

**Blocked by:** none (builds on `signals` ticket 1 / PR #65).

**Priority:** medium.

**Status:** ready-for-agent

Settled via `/grill-with-docs` (`grilling` + `domain-modeling`, three rounds):

- [x] **Signal-tool nodes never gate `structural-scan`.** The existing Safety Net (13 `php-structural-
  scan` leaves, 3 `structural-scan` leaves) stays exactly as documented today, minus the
  `test-runner-if-missing` simplification below. New signal-tool nodes attach elsewhere in the tree,
  gated only by their own natural prerequisites, and are proposed/ranked through the ordinary
  scan/prioritize cycle — no special-cased admission.
- [x] **New node-level `Signal` field**, format matching the existing `Housekeeping` field precedent
  (`- **Signal:** <factor(s) from signals.md, with a short reason>` in the node's own doc). Once a
  node carrying this field is fulfilled, `refactor-prioritize`'s Select mode prefers its real tool
  output over `signals.md`'s generic (git-log/manual-judgement) recognition method for that factor.
  `CONTEXT.md`'s `Signal` entry is widened to cover both this and the existing candidate-issue field —
  same catalogue, same purpose, two places it shows up, not a second term.
- [x] **PHPMD** (new node, `php-tooling-tree.md`): `composer → phpmd | required` (mirrors `php-cs-
  fixer`/`phpunit`/`composer-audit`/`static-code-analyzer` — no other prerequisite). `Signal:`
  Understandability (the complexity measurement itself) and Defect density (complexity's empirical
  correlation with bugs) — both, with the reasoning noted inline. No `resolved` edge anywhere.
- [x] **Secret Detection** (new node, generic root — `tooling-tree.md`, not the PHP tree):
  `loop-config → secret-detection | required`, same shallow prerequisite `editorconfig`/`ci-runner`
  already use — future language specializations inherit it automatically. `**Tool:** any secret
  scanner`, generic like `test-runner-if-missing.md`'s own `any test runner` — concrete tool
  (gitleaks/detect-secrets/truffleHog, per `.scratch/php-tooling-tree/issues/13`'s own candidate list)
  decided at adoption/design time, not pinned in the tree doc. **No** `resolved` edge to
  `structural-scan` (unlike `editorconfig`/`ci-runner`, which do have one — a deliberate structural
  difference, not an oversight, worth stating explicitly in the node doc so it isn't "fixed" later by
  someone pattern-matching on its neighbors). Scope: only the CI-gate half of ticket 13 (block future
  secrets). The retroactive git-history scan + cleanup-candidate filing half of ticket 13 is explicitly
  out of scope here — noted in the node doc as separate, real follow-up work, not silently dropped.
- [x] **`test-runner-if-missing` dropped from the Safety Net**, no replacement. `phpunit`'s own
  Fulfilment check ("PHPUnit runs green locally") already gives a real, if narrower, guarantee; the
  extra CI-wiring assurance `test-runner-if-missing` added is useful but not safety-critical enough to
  keep gating structural work. `phpunit` itself is completely unaffected — it stays exactly as it is,
  a required leaf on its own.
- [x] **`php-cs-fixer`'s route to `php-structural-scan` simplified.** New `recommended` edge
  `php-cs-fixer → rector-php-set`, alongside the existing `phpstan-level-0`/`psalm → rector-php-set`
  (`required-any`) and `php-minimal-version → rector-php-set` (`recommended`) parents. The direct
  `php-cs-fixer → php-structural-scan` (`resolved`) edge is dropped — verified lossless: `composer`
  already forces `php-cs-fixer` to be proposed early (`required`), and the new recommended edge into
  `rector-php-set` transitively forces `php-cs-fixer` to be *decided* before `rector-php-set` can even
  be proposed, which is itself required before `rector-dead-code`/`rector-code-quality` (which already
  carry their own `resolved` edges to `php-structural-scan`) can ever be reached. Same guarantee, one
  fewer direct edge. The four existing `php-cs-fixer → {rector-dead-code, rector-type-coverage,
  rector-code-quality, rector-phpunit-set}` `recommended` edges are unchanged.
- [x] **PHPStan level-chain leaf lowered from 10 to 5.** `phpstan-level-10 → php-structural-scan |
  resolved` is replaced (not kept alongside) by `phpstan-level-5 → php-structural-scan | resolved`.
  Level 5 is the chain's only existing structural fork point (`phpstan-level-5 → phpstan-deprecation-
  rules | required` already branches there) — not an arbitrary new number. Matches the user's own
  practical experience: stricter array-typing rules start in earnest from level 6 on, a bar that
  shouldn't have to be cleared before ordinary structural refactoring can begin. Levels 6–10 stay
  fully in the tree as ordinary proposable nodes — `phpstan-level-10` becomes an open-ended chain tip,
  no longer load-bearing for the gate. `phpstan-level-3 -.-> rector-type-coverage` and every other
  existing edge involving levels 6-10 are unaffected.
- [x] **Existing "later wave" tickets updated, not superseded wholesale.** `.scratch/php-tooling-tree/
  issues/08` (coverage floor), `09` (mutation testing), `11` (OWASP SAST), `14` (nightly DAST) each get
  a short comment: no `resolved` edge to `structural-scan`/`php-structural-scan` when eventually
  built, matching this ticket's own signal-tool-nodes decision — still open, still their own future
  design/implementation passes, not touched further here. `.scratch/php-tooling-tree/issues/13`
  (secret detection) is implemented by this ticket's Secret Detection node (CI-gate half only) — noted
  as such, and the retroactive-scan half kept open on that same ticket as remaining scope.
- [x] **One combined ADR** covering both the signal-tool-nodes decision and the three edge
  simplifications (Considered Options: PHPStan cutoff at 5 vs. keeping 10 vs. another level; a second
  `Signal`-like field name for nodes vs. reusing `Signal` itself; test-runner-if-missing dropped vs.
  replaced).

## Comments

> **2026-09-07:** Filed after a `/grill-with-docs` session (German — `grilling` + `domain-modeling`),
> three rounds, growing out of a live design discussion following PR #65 — the user's own principle
> ("deterministic tools before agentic analysis") applied to the chicken-and-egg problem of needing
> tools to produce Signals but needing Signals to justify adopting tools. Along the way, three genuine
> simplifications to the existing PHP tree's edge table surfaced from close reading, one verified
> lossless (`php-cs-fixer`), one a deliberate, justified trade-off (`phpstan-level-10` → `-5`), one a
> straightforward drop (`test-runner-if-missing`). User confirmed shared understanding ("ja, passt.").
> Ready to implement.
