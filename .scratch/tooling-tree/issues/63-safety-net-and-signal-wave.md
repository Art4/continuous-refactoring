# 63 — Onboarding/Safety Net split; Signal wave nodes wait for the Safety Net to close

**What to build:** Grilled jointly (`/grill-with-docs`, several rounds) against a real UX complaint: security-relevant nodes (`composer-audit`, `secret-detection`, …) were being proposed in the very first wave, before the deterministic Safety Net had even closed. Splits "the tree" into an **Onboarding** phase (new `CONTEXT.md` term) ending once `structural-scan` opens, with a narrower **Safety Net** (also new) inside it, and moves every node that doesn't belong in that narrower set into a new **Signal wave** (also new) that only opens once the Safety Net does.

1. **Rename `php-structural-scan` → `php-safety-net`.** Same node, same mechanism (still resolved once its nine leaves are resolved, still the sole `resolved` parent PHP contributes to `structural-scan`), new name that says what it actually means now that other nodes read its resolved-ness too, not just `structural-scan`. Update every reference across `tooling-tree.md`, `php-tooling-tree.md` (table, diagram, prose), `tooling_tree.py`, `tree-walk-prompt.md`, `SKILL.md` files, and the ADR-0017/ADR-0040 cross-references.

2. **Two Safety Net leaves reclassified as Signal wave nodes** (drop their `resolved` edge into `php-safety-net`, gain `php-safety-net` as an *additional* required parent alongside their existing one — chosen over full replacement because their existing parent's real fulfilment, not just "decided", is load-bearing for their own purpose):
   - `composer-audit`: required parents become `composer` + `php-safety-net`. `ci-runner` downgraded from required to recommended. Fulfilment check gains a second path: a CI job running `composer audit` (unchanged), **or** a committed line for this node in `housekeeping-template.md` (no proof of a completed run needed — see point 4).
   - `phpstan-deprecation-rules`: required parents become `phpstan-level-5` + `php-safety-net`.

   `php-safety-net`'s own leaf count drops from eleven (as `php-structural-scan`) to nine: `psr-4`, `phpunit`, `phpstan-level-5`, `rector-dead-code`, `rector-type-coverage`, `rector-php-set`, `rector-code-quality`, `rector-phpunit-set`, `psalm-taint-analysis`. `psalm-taint-analysis` stays a Safety Net leaf, unchanged — its findings (a refactor introducing a new taint bug) genuinely could collide with structural work, unlike `composer-audit`'s third-party-CVE findings.

3. **Four more PHP-tree nodes gated on `php-safety-net`, additively** (existing required parent kept for the same reason as point 2 — a rejected `phpstan-level-5`/`phpunit`/`rector-php-set` must still permanently close its dependent, which a bare `php-safety-net` required-edge alone would not do, since a rejected resolved-parent still counts as resolved):
   - `phpmd`: `composer` + `php-safety-net` (was `composer` alone).
   - `coverage-floor`: `phpunit` + `php-safety-net` (was `phpunit` alone).
   - `php-minimal-version`: `rector-php-set` + `php-safety-net` (was `rector-php-set` alone).
   - `phpstan-level-6`: `phpstan-level-5` + `php-safety-net` (was `phpstan-level-5` alone). Levels 7–10 need no edge of their own — they inherit the wait transitively through the existing chain.

4. **`semgrep` fully repointed** (the one node where full replacement is correct, not additive — its own doc already states Semgrep needs no Composer at all; the old `composer` required parent was purely an incidental rejection-cascade-closure technicality, made redundant by `php-safety-net`): required parent becomes `php-safety-net` alone (drops `composer`); the `recommended` parent `psalm-taint-analysis` is dropped too (redundant — `psalm-taint-analysis` is one of `php-safety-net`'s own nine leaves, so it's always already decided by the time `php-safety-net` resolves). `ci-runner` downgraded required → recommended, same Housekeeping-line fulfilment fallback as `composer-audit` (point 2) — scoped to these two audit-style nodes for now, not a tree-wide mechanism, but documented as a reusable pattern for future audit nodes (more are planned).

5. **`secret-detection` repointed at the generic root's own gate**: required parent becomes `structural-scan` (was `loop-config`) — stays outside `php-safety-net` since it's language-neutral (no PHP-specific gate needed; it doesn't care which specialization, if any, is active).

6. **`CONTEXT.md`**: new **Onboarding**, **Safety Net**, **Signal wave** entries (already written — see below), plus a clarifying aside on **Tooling tree**'s existing `_Avoid_: onboarding` note distinguishing "the tree as a whole" from the new bounded-phase term.

7. **`tooling_tree.py` code changes** (not a pure doc change, unlike ADR-0040's own edge simplifications — flagging this explicitly so `/implement` doesn't assume otherwise):
   - Rename every `"php-structural-scan"` string literal to `"php-safety-net"`.
   - `_composer_audit_extra_gate()`: currently checks "every other leaf feeding `php-structural-scan`" as a fallback so a dependency-free target still resolves the leaf — this whole fallback is moot now that `composer-audit` isn't a `php-safety-net` leaf at all; remove the function and its call site, and drop `composer-audit.md`'s "Stop conditions" bullet (b) (bullet (a), "real `require` dependency exists", stays — it's an independent proposability guard, not related to unblocking `structural-scan`).
   - New helper(s) for the Housekeeping-line fulfilment path: `_has_housekeeping_line_for(repo, node_name)` (or similar), reading `housekeeping-template.md` for a contributed line naming the node — reused by both `composer-audit` and `semgrep`'s fulfilment checks.

**Why:** Two orthogonal axes were being conflated: **Signal** (which `signals.md` factor a node feeds — unaffected by any of this) and **wave** (when a node is proposed). `composer-audit`/`psalm-taint-analysis` are both Security-signal nodes, but only `psalm-taint-analysis` belongs in the Safety Net (its findings are the kind agent-driven structural work could introduce or collide with); `composer-audit`'s CVE findings don't have that property and its Safety Net membership predates ADR-0040's Safety-Net/Signal distinction, never re-examined against it until now. Gating the PHP-specific Signal wave nodes on `php-safety-net` (rather than a persisted `is-php-project` bookkeeping flag, considered and rejected) falls out for free from the existing "Known gap" in `is-php-project.md`: `php-safety-net` (like `php-structural-scan` before it) can only ever resolve via the PHP recognition path today, so a non-PHP target never opens the PHP Signal wave either, no new mechanism needed. The Housekeeping-line fulfilment fallback (rather than requiring proof of a completed run) matches every other CI-gated fulfilment check already in this tree, which treats "job exists/invokes the tool" as sufficient — `continuous-housekeeping` itself deliberately keeps no local "last run" record (the forge's own issue history is the record), so demanding proof of a completed run here would mean either duplicating that state locally or giving the otherwise pure-filesystem `tooling_tree.py` parser forge access, both disproportionate for two nodes.

**Priority:** medium — nothing is broken today, but every pass against a target already climbing the PHP tree proposes nodes in an order this ticket changes; worth doing before more audit-style Signal wave nodes (planned) compound the same "proposed too early" complaint.

**Status:** open

- [x] `CONTEXT.md`: **Onboarding**, **Safety Net**, **Signal wave** entries added; **Tooling tree**'s `_Avoid_` note clarified.
- [ ] `skills/refactor-scan/references/tooling-tree.md`: `secret-detection`'s required parent → `structural-scan`; diagram/table/prose updated.
- [ ] `skills/refactor-scan/references/php-tooling-tree.md`: `php-structural-scan` renamed `php-safety-net` throughout (table, diagram, prose); `composer-audit`/`phpstan-deprecation-rules` resolved edges removed, required parents updated; `phpmd`/`coverage-floor`/`php-minimal-version`/`phpstan-level-6` gain `php-safety-net` as an additional required parent; `semgrep`'s required/recommended parents repointed; leaf-count prose (eleven → nine) updated.
- [ ] `skills/refactor-scan/references/php-tooling-tree/composer-audit.md`: required parents, `ci-runner` required→recommended, Fulfilment check's new OR-branch, Stop-conditions bullet (b) removed.
- [ ] `skills/refactor-scan/references/php-tooling-tree/semgrep.md`: required/recommended parents repointed, obsolete composer-justification paragraph removed, `ci-runner` recommended + Fulfilment OR-branch added.
- [ ] `skills/refactor-scan/references/php-tooling-tree/phpmd.md`, `coverage-floor.md`, `php-minimal-version.md`, `phpstan.md` (deprecation-rules, level-6): required-parent bullets updated.
- [ ] `skills/refactor-scan/references/tooling_tree.py`: rename, `_composer_audit_extra_gate()` removed, new Housekeeping-line helper(s) added and wired into `composer-audit`/`semgrep`'s fulfilment checks.
- [ ] `skills/refactor-scan/references/tree-walk-prompt.md`: rename; note that a required parent may itself be a resolved-gated node (treat "fulfilled" as "resolved" for such a parent).
- [ ] `scripts/test_tooling_tree.py`: updated/new assertions for every edge change above.
- [ ] `fixtures/php/*/expected/roadmap.json`: regenerated against `fixtures/harness/run.sh`, verified per fixture.
- [ ] New ADR: `docs/adr/0054-onboarding-safety-net-and-signal-wave.md`, amending ADR-0040 and ADR-0017.
- [ ] `python3 -m unittest discover -s scripts -p 'test_*.py'` and `python3 scripts/validate_skills.py .` both green.

## Comments

> **2026-09-17:** Grilled (`/grill-with-docs`, three rounds) directly against `skills/refactor-scan/references/{tooling-tree.md,php-tooling-tree.md}` and the affected node files, following a live UX complaint (security-relevant nodes proposed too early, ahead of the deterministic Safety Net). All decisions above confirmed by the maintainer, including the vocabulary additions and the additive-vs-replace distinction per node. Ships already fully spec'd (ready-for-agent) rather than needs-triage.
