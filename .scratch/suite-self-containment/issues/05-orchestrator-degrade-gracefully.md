# 05 — Make the orchestrator degrade gracefully

**What to build:** `continuous-refactoring` verifies that a loop pass can run end-to-end when none of the global skills (`/grilling`, `/tdd`, `/code-review`, `/codebase-design`, `/domain-modeling`) are installed. The orchestrator documents where each lifecycle skill's inline fallback engages, so a target repo without the global skills still gets a working pass.

**Blocked by:** 02 ✓ done — Make refactor-design self-contained, 03 ✓ done — Make refactor-implement self-contained, 04 ✓ done — Make refactor-review self-contained

**Status:** ready-for-agent

- [ ] A full pass is verified against the suite's own skills only (no global references required)
- [ ] The fallback engagement points are documented in the orchestrator
- [ ] Tier 1 static validation passes (`python3 scripts/validate_skills.py .` exits 0)
