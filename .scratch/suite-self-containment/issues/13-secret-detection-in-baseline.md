# 13 — Add secret detection to the baseline

**What to build:** CI scans the code and git history for secrets, API keys, and tokens (candidates: gitleaks, detect-secrets, truffleHog) so credentials never land in the repo; a gate blocks committing secrets rather than discovering them months later. Historical secrets surface in `refactor-scan` as cleanup candidates (MR type I — secret/credential cleanup).

**Blocked by:** 06 — Decide the baseline tooling details (grilling)

**Status:** ready-for-agent

- [ ] Secret scan wired into CI (and/or pre-commit) as a gate
- [ ] Historical secrets found are filed as cleanup candidates, not silently ignored
- [ ] Tool choice matches ticket 06's defaults