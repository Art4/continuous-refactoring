# 16 — Automated test harness — Tier 1: static suite validation

**Type:** build

**What to build:** The no-agent, deterministic static validation tier of the suite harness. Every `skills/*/SKILL.md` is checked without an LLM — frontmatter (required fields, name matches the directory, naming constraints), required sections, resolvable local references, no dangling global `/X` references, CONTEXT vocabulary / ADR references. Deterministic, CI-friendly, exit-code based.

- [x] Tier 1 runs deterministically with no LLM, local and in CI
- [x] Frontmatter validation on all `skills/*/SKILL.md` (fields, name = directory name, kebab-case)
- [x] Required sections enforced per skill
- [x] No dangling global `/X` references (audited against `docs/agents/skill-references.md`)
- [x] Local references resolve; CONTEXT vocabulary / ADR references checked

**Blocked by:** 01 ✓ done — Fallback convention and audit (provides the `/X` reference ledger)

**Status:** ready-for-agent

## Comments

> **2026-08-20:** Tier 1 isolated here; Tiers 2–5 (harness decision, artifact contracts, ground truth, triggers, CI gate + lift) moved to ticket 17. Research done on tooling. Off-the-shelf: `skill-validator` (agent-ecosystem, Go CLI) covers frontmatter/structure/token/link checks and is CI-ready (exit codes, `--strict`, GitHub annotations, multi-skill dirs); needs `--allow-extra-frontmatter` because opencode's `disable-model-invocation` is not a spec field. `skills-ref` (agentskills.io, Python) is explicitly demo-only. Suite-specific checks — dangling `/X` refs vs the ledger, required sections, CONTEXT/ADR refs — need a small bespoke script (repo currently has zero tooling, no CI). Verified: all 7 current skills pass the basic checks today.

> **2026-08-20:** Implemented. `scripts/validate_skills.py` (Python stdlib + pyyaml, no LLM) with `scripts/test_validate_skills.py` (41 unittest cases, TDD at the function seams + one end-to-end test against the real repo) and a GitHub Actions gate `.github/workflows/skills-validation.yml` (runs tests, then `--strict` on push/PR touching `skills/`, `docs/`, `CONTEXT.md`, `scripts/`). Checks: frontmatter (name = directory, kebab-case, description, known fields incl. opencode extensions), required sections (`## Completion criterion` everywhere, `## Process` on lifecycle skills / `## The pass` on the orchestrator, `## Fallback` on ADR-0003-shipped skills per the ledger), bidirectional `/X`↔ledger consistency, local `docs/`/`CONTEXT.md`/`*.md` refs resolve (target-repo artifacts exempt), `ADR-NNNN` resolves, glossary terms in use + avoid-term scan with one documented allowlist entry. Required rewording 5 avoid-term uses in skills (session→conversation, grilling session→grilling, pain point→hot spot); `boundary` in refactor-design kept via allowlist as it defines the `seam` term. Exit codes 0/1/2 (warnings with `--strict`).