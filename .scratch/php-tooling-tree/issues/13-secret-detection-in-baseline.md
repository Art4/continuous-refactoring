# 13 — Add secret detection to the baseline

**What to build:** CI scans the code and git history for secrets, API keys, and tokens (candidates: gitleaks, detect-secrets, truffleHog) so credentials never land in the repo; a gate blocks committing secrets rather than discovering them months later. Historical secrets surface in `refactor-scan` as cleanup candidates (MR type I — secret/credential cleanup).

**Blocked by:** 06 ✓ done — later wave (ADR-0005): all security deferred

**Wave:** later — see `.scratch/php-tooling-tree/spec.md` (not pickable before first-wave tickets 10/18 land)

**Status:** ready-for-agent

- [ ] Secret scan wired into CI (and/or pre-commit) as a gate
- [ ] Historical secrets found are filed as cleanup candidates, not silently ignored
- [ ] Tool choice matches ticket 06's defaults

## Comments

> **2026-08-21:** ADR-0005 — later wave; all security deferred.
> **2026-08-22:** Moved from `suite-self-containment/issues/` to `php-tooling-tree/issues/` — regrouped around the PHP tooling tree.
> **2026-08-23:** Ticket hygiene — added an explicit `Wave:` field so `Status: ready-for-agent` isn't misread as pickable now; the prose in `Blocked by` said "later wave" but nothing machine-scannable enforced it. See `spec.md`'s wave table.
> **2026-09-07:** Signals ticket 2 (`.scratch/signals/issues/02-signal-tool-nodes-and-tree-edge-simplification.md`) implements this ticket's CI-gate half: `secret-detection` is now a real, adoptable node on the generic tooling tree root (`skills/refactor-scan/references/tooling-tree.md`), fulfilled once CI runs a recognized scanner (gitleaks, detect-secrets, trufflehog) — a Signal-producing node (Security), carrying **no** `resolved` edge into `structural-scan`. The retroactive git-history scan half above ("historical secrets surface as candidates") stays open — the node's own entry explicitly scopes it out of the adoption MR as separate follow-up work not yet ticketed. This ticket's checkboxes below still track that open half; the first two checkboxes' CI-gate half can be considered satisfied by the node's adoption on a given target.
