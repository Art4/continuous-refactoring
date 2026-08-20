# 16 — Automated test harness for the suite

**Type:** grilling + build

**What to build:** A way to test the suite's skills automatically, so every change to a `SKILL.md` is verified instead of only eyeballed. Based on the established skill-testing methods (static lint tier, deterministic sandbox/artifact assertions, ground-truth benchmarks, trigger/discoverability tests, LLM-judge grading with a CI gate), the ticket first decides the infrastructure and then builds the tiers on it:

- **Decision first (grilling):** which infrastructure — a lightweight custom harness (`opencode run` + fixture repos + assertion scripts, fits the opencode runtime) vs an existing framework (skillkit / coder-eval / skillcheck; mostly Claude/Codex-oriented). Outcome recorded in the ticket or as an ADR.
- **Tier 1 — Static suite validation, no agent:** every `SKILL.md`'s frontmatter, required sections, resolvable local references, no dangling global `/X` references, CONTEXT vocabulary / ADR references. Deterministic, CI-friendly, no LLM.
- **Tier 2 — Deterministic artifact contract tests:** a loop pass (or lifecycle skills) run via opencode in a sandboxed fixture repo; assertions on the produced artifacts — candidate issues with required fields + `refactor:candidate` label, config-file format, `.out-of-scope/` conventions, MR chain ≤ 2, learn effects (ADR/CONTEXT).
- **Tier 3 — Ground-truth fixture repos:** golden PHP repos with planted candidates (shallow module, A03 injection, secret, unused dependency, style violation); `refactor-scan` scored against the planted set (precision/recall), with a saved baseline for regression tracking.
- **Tier 4 — Trigger/discoverability tests:** explicit + implicit invocation per skill; negative controls — orchestrator without a baseline marker must not refactor, a scan on a clean repo reports clean and stops, a non-PHP project gets no PHP baseline.
- **Tier 5 — CI gate + lift measurement:** harness wired into CI with regression baselines; LLM-judge rubric grading; with-skill vs without-skill lift measurement.

**Blocked by:** 01 ✓ done — Fallback convention and audit, 07 — Validate: first loop pass in a PHP target repo

**Status:** ready-for-agent

- [ ] Harness decision made (grilling) and recorded; tiers built on it
- [ ] Tier 1: static validation runs deterministically, no LLM
- [ ] Tier 2: artifact contract assertions over a sandboxed loop run
- [ ] Tier 3: ground-truth repos + precision/recall score + saved baseline
- [ ] Tier 4: trigger tests incl. negative controls
- [ ] Tier 5: CI gate + rubric grading + lift measurement