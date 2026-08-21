# 12 — Deliver each refactor as a merge request

**What to build:** The loop ends with a delivery artifact. For each completed candidate, the learn step creates a merge request on the target repo's forge with a written rationale — what deepened, why, which tests survive, what CI proves — and links it to the candidate issue. A completed pass ships a reviewable, traceable diff instead of only an issue-status change; the loop closes only after the MR exists. Each MR carries a typed rationale from the brainstorming's extended MR types (e.g. Psalm-taint fix, Semgrep OWASP violation, secret/credential cleanup, vulnerable-dependency update), so the reviewable unit also states which quality dimension it moved. The MR carries the delivery rules: one candidate per MR, atomic commits following the target repo's commit convention, and a description that ends with an outlook — what this refactor unlocks short- and mid-term, i.e. which deeper tools or techniques become viable once it lands (a cleaner seam enabling Psalm taint analysis, tests enabling mutation testing, a Composer layout enabling the next baseline tools). Review comments are addressed in follow-up commits; recurring feedback patterns feed the learn step (ADR, `CONTEXT.md`, or a new scan signal) so the loop gets better at predicting what reviewers reject. A pass may ship more than one MR: parallel MRs when they do different, independent things (e.g. introducing a Rector rule *and* a composer audit scan); chained MRs when one builds on another — but never more than two in a chain, so the first MR demonstrates what the second one will enable before the second lands.

**Blocked by:** 05 ✓ done — Make the orchestrator degrade gracefully

**Status:** ready-for-agent

- [ ] Each completed candidate produces an MR with a written rationale on the target repo's forge
- [ ] The MR is linked from the candidate issue; the pass closes only once the MR exists
- [ ] Works self-contained (no global-skill dependency)
- [ ] Each MR carries a typed rationale naming the quality dimension it addresses
- [ ] One candidate per MR; commits are atomic and follow the target repo's commit convention
- [ ] MR description includes an outlook: what the refactor enables short/mid-term and which tools/techniques it unlocks
- [ ] Review comments are addressed; recurring feedback feeds the learn step (ADR / CONTEXT / scan signal)
- [ ] Multiple parallel MRs allowed for independent work; chained MRs allowed but never more than 2 in a chain — the first shows what the second unlocks