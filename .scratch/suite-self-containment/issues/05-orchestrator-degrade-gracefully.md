# 05 — Make the orchestrator degrade gracefully

**What to build:** `continuous-refactoring` verifies that a loop pass can run end-to-end when none of the global skills (`/grilling`, `/tdd`, `/code-review`, `/codebase-design`, `/domain-modeling`) are installed. The orchestrator documents where each lifecycle skill's inline fallback engages, so a target repo without the global skills still gets a working pass.

**Blocked by:** 02, 03, 04

**Status:** ready-for-agent

- [ ] A full pass is verified against the suite's own skills only (no global references required)
- [ ] The fallback engagement points are documented in the orchestrator
