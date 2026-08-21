# 20 — Tier 2 Validator: semantic and cross-skill checks

**Type:** build

**What to build:** Extend the Tier 1 static validator (`scripts/validate_skills.py`) with four deterministic Tier 2 checks that catch architectural drift the structural checks miss. No LLM required — all checks are regex/keyword-based.

The four checks:

- **ADR-0004 rule propagation:** every rule keyword from ADR-0004 (`behavior-preserving`, `Strangler Fig`, `Kent Beck`, `deterministic tools`, `own branch`) must appear in at least one of `refactor-design` or `refactor-implement`. A missing keyword flags a silently dropped rule.
- **Cross-skill contract consistency:** the orchestrator's description of each lifecycle step's output must mention that step's completion-criterion terms. If the orchestrator says "loop implement → review until clean" but the review skill's completion criterion uses different wording, the mismatch is flagged.
- **Glossary reverse check:** domain vocabulary used in 2+ skills but absent from `CONTEXT.md` is flagged. Catches terms like `slice`, `design tree`, `frontier`, `smell` that drift into use without a glossary entry.
- **ADR staleness detection:** ADRs containing `retired`, `supersedes`, or `amends` are parsed into a dependency graph. Skills referencing a superseded ADR without noting the successor are flagged.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] ADR-0004 rule-propagation check implemented and tested
- [ ] Cross-skill contract-consistency check implemented and tested
- [ ] Glossary reverse check implemented and tested
- [ ] ADR staleness check implemented and tested
- [ ] All new checks wired into `validate_repo()` and CI
- [ ] Unit tests for each check (valid + invalid cases)
- [ ] `validate_skills.py --help` updated to document Tier 2 checks

## Comments

> **2026-08-21:** Created from architecture review candidate 4 (Strong recommendation). Source: HTML report at `/tmp/architecture-review-20260821.html`. Related existing ticket: 17 (Tier 2–5 runtime harness — this ticket covers the static/deterministic Tier 2 checks; 17 covers sandbox/artifact-based Tier 2+).
