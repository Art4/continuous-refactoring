# 35 — `php-minimal-version`: recommend a PHP-runtime floor bump as a normal candidate

**Type:** build

**What to build:** A new PHP-tree node, `php-minimal-version`:

- **Name:** PHP Minimum Version
- **Tool:** none — the tree's own gap detection, not a third-party tool.
- **Purpose:** detect a gap between `composer.json`'s declared PHP floor and what the tree actually needs, and propose raising the floor to close it.
- **Required parents:** `loop-config` **and** `ci-runner` — two required parents, same shape as `composer-audit` (required on `ci-runner` + `composer`).
- **Fulfilment check:** `composer.json`'s declared PHP floor ≥ the maximum of:
  (a) the minimum version of every leaf currently blocked by `php_floor_precheck()` (`tooling_tree.py`'s existing `_LEAF_MIN_PHP_VERSION` computation — reused directly, no new mechanism), and
  (b) the highest PHP version tested by a **quality-tooling CI job** (the jobs that run phpstan/rector/etc., not an arbitrary compatibility-matrix job that legitimately tests multiple PHP versions for unrelated reasons).
  Below that maximum → proposable, exactly the tree's ordinary "propose when not yet fulfilled" shape. No new edge type.
- **MR scope:** narrow — bump `composer.json`'s `require.php` constraint, plus the CI job that tests the app itself if a single unified job exists. Explicitly **out of scope**: consolidating a separate tooling container/job if one exists (e.g. a second, higher-PHP Docker container running dev tooling) — that's a distinct, later concern from the gap this node closes.
- **Autonomy:** an ordinary candidate like every other node — the agent designs, implements, and opens the MR; a human reviews and merges, same gate as everything else. No "advisory only, never build" concept needed; `refactor-design`/`refactor-implement` need no changes.
- **Relationship to `rector-php-set`:** becomes its **recommended parent** (ADR-0016 decided-gate semantics — `rector-php-set`'s PHP-version-targeted rule set assumes the floor already covers the syntax it rewrites to, which today it has no dependency on at all). Rejecting `php-minimal-version` still releases `rector-php-set` once decided; it just can't jump ahead of an undecided floor question.
- **Scope:** PHP-specific — sibling of `composer`/`ci-runner` under `loop-config` in `php-tooling-tree.md`'s edge table. No generic-tree shape attempted; no second language specialization exists yet to validate one against.
- **Re-triggering property:** the fulfilment check is a relative comparison against a moving target, not a one-time artefact check. If a later tool raises its minimum, or a new quality-tooling CI job tests a higher version, the same floor that used to satisfy the check can stop satisfying it — the node becomes proposable again on the next pass. This needs no special mechanism: every fulfilment check in the tree is already re-derived fresh from live repo state each pass (same principle `php_floor_precheck()` itself already relies on); it's simply more visible here because the condition is comparative rather than presence-based. Not retroactive — an already-decided `rector-php-set` candidate is unaffected; only still-open proposals are held back again. See [ticket 38](38-housekeeping-recurring-node.md) for the sibling, time-driven (not fact-driven) case of a node whose fulfilment can flip back to false.

**Why:** Observed on the `Art4/legacy-todo` run: the target stayed pinned to PHP 5.6 throughout, and adopting PHPStan/Rector (both require PHP 7.2+/8.0+) was solved by running them in a second, parallel Docker container (PHP 8.3) rather than by proposing a PHP-runtime bump for the target itself — even though this same target repo has precedent for exactly that kind of candidate: an earlier, unrelated run's merged `PR #45 "Tool/Build: bump PHP runtime floor to 7.2"`. Maintaining two permanently-parallel PHP versions (one for the app, one for its own dev tooling) is a plausible interim state, but not obviously the suite's intended steady state, and nothing in the tree today ever raises "you now have two PHP versions in play" as a thing worth surfacing.

**Blocked by:** none.

**Priority:** not set during this grilling session — no urgency signal beyond the original observation; set when scheduled.

**Status:** ready-for-agent

- [ ] `php-minimal-version` node entry added to `skills/refactor-scan/references/php-tooling-tree.md` (Name, Tool, Purpose, Fulfilment check, MR scope) and its edge-table rows (`loop-config → php-minimal-version` required, `ci-runner → php-minimal-version` required, `php-minimal-version → rector-php-set` recommended)
- [ ] Fulfilment check implemented in `tooling_tree.py`, reusing `php_floor_precheck()`'s existing minimum-version computation for signal (a)
- [ ] Quality-tooling-CI-job PHP-version detection implemented for signal (b), scoped to the jobs that actually invoke phpstan/rector/etc. (reuse the same CI-job-detection style as `composer-audit`/`phpunit`'s own CI-gating checks), not arbitrary compatibility-matrix jobs
- [ ] `rector-php-set`'s node entry gains `php-minimal-version` as a recommended parent
- [ ] `next_candidates()`/`roadmap()` exercise the new node with no special-casing beyond the ordinary required/recommended-edge machinery
- [ ] MR-scope implementation bumps `composer.json`'s floor + the unified app-CI-job version only — no container/job consolidation logic

**Out of scope:** consolidating a separate tooling container/job into the app's own PHP version (a later, distinct concern); a generic (language-neutral) version of this node.

## Comments

> **2026-08-29:** Filed from the legacy-todo reviewer-loop findings log
> (`.scratch/legacy-todo-loop-observation/findings.md`, "Finding — PHPStan läuft jetzt korrekt in
> separatem Docker/PHP-8.3-Container, aber kein PHP-Upgrade-Vorschlag") after the user asked for it to be
> turned into a ticket, explicitly framed as "we need to think about this" rather than a ready spec —
> kept as `needs-triage` rather than `ready-for-agent`/`ready-for-human` for that reason.

> **2026-08-30:** Design settled via a `/grill-me` session (in German), two question rounds plus one
> follow-up. All four original open questions resolved:
> - Dedicated node, not an ad hoc outlook observation — `php_floor_precheck()` already computes the needed
>   fact; a dedicated node consumes it once instead of repeating the recommendation across every blocked
>   leaf's outlook.
> - Autonomy: an ordinary candidate MR like every other node, not an "advisory only, never build" node —
>   the existing human-merge-review gate already covers the risk; a new "propose but never build" category
>   (which `refactor-design`/`refactor-implement` don't have any concept of today, confirmed by re-reading
>   both skills in full) would be a lot of new design weight for a benefit the existing gate already gives.
> - Edge-table placement: sibling of `composer`/`ci-runner` under `loop-config`, two required parents
>   (`loop-config`, `ci-runner`) — not a structurally novel parentless/trigger-based node. `ci-runner` as an
>   explicit required edge (not just an implicit dependency inside the fulfilment check) was the user's own
>   call, matching `composer-audit`'s existing two-required-parent precedent.
> - Scope: PHP-specific, no generic-tree shape.
>
> Plus follow-on decisions beyond the ticket's original four questions: the trigger condition combines
> `php_floor_precheck`'s blocked-leaf signal with a second, quality-tooling-CI-job-version signal (the
> user's own addition, catching the observed "tooling runs in a separate higher-PHP container" pattern
> before someone even builds that workaround); MR scope stays narrow (floor bump only, no workaround
> consolidation); the node's slug is `php-minimal-version` (the user's own choice, deliberately avoiding
> "upgrade" to not collide with `rector-php-set`'s "PHP-upgrade rule set" wording, which is a different
> concern — syntax modernization, not the runtime floor); and `php-minimal-version` becomes a recommended
> (not required) parent of `rector-php-set`, closing a real gap (`rector-php-set` has no floor dependency
> today) without permanently blocking it on a rejected floor-bump.
>
> A late follow-up question — can this node re-trigger, or is it fulfilled once and done — surfaced that
> its fulfilment check is a moving-target comparison rather than a one-time artefact check, so yes, it can
> become proposable again without any extra mechanism (see *Re-triggering property* above). This is now a
> second, already-decided precedent for the tree's fulfilled-flag-can-flip-back-to-false question that
> [ticket 38](38-housekeeping-recurring-node.md) has open for its own (time-driven) reason — noted there.
