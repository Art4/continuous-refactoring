# 12 — Deliver each refactor as a merge request

**What to build:** The loop ends with a delivery artifact. For each completed candidate, the learn step creates a merge request on the target repo's forge with a written rationale — what deepened, why, which tests survive, what CI proves — and links it to the candidate issue. A completed pass ships a reviewable, traceable diff instead of only an issue-status change; the loop closes only after the MR exists.

**Blocked by:** 05 — Make the orchestrator degrade gracefully

**Status:** ready-for-agent

- [ ] Each completed candidate produces an MR with a written rationale on the target repo's forge
- [ ] The MR is linked from the candidate issue; the pass closes only once the MR exists
- [ ] Works self-contained (no global-skill dependency)