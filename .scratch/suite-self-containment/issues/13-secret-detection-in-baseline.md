# 13 — Add secret detection to the baseline

**What to build:** CI scans the code and git history for secrets, API keys, and tokens (candidates: gitleaks, detect-secrets, truffleHog) so credentials never land in the repo; a gate blocks committing secrets rather than discovering them months later. Historical secrets surface in `refactor-scan` as cleanup candidates (MR type I — secret/credential cleanup).

**Blocked by:** 06 ✓ done — later wave (ADR-0005): all security deferred

**Status:** ready-for-agent

- [ ] Secret scan wired into CI (and/or pre-commit) as a gate
- [ ] Historical secrets found are filed as cleanup candidates, not silently ignored
- [ ] Tool choice matches ticket 06's defaults

## Comments

> **2026-08-21:** ADR-0005 — later wave; all security deferred.