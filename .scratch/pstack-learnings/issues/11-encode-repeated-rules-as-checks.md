# 11 — Encode repeated rule violations as checks

Type: task
Status: done

When the same rule is violated or restated twice (e.g. forge-facing text citing suite paths, docs citing ADR numbers), add it as a check in scripts/validate_skills.py instead of another paragraph. Possibly: have the findings log surface repeated violations as a proposal.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

**Tooling-tree table:** the planned check that every `Requires` parent carries its child's Tracks is a case of this rule and belongs in the validator or parser, not in prose. A tooling node itself is the structured form of a lesson, which supports keeping tools as nodes rather than prose.

## Comments

### 2026-10-16 — gap check against `skills/`: partial

`scripts/validate_skills.py`, the changelog check and the trigger-control tests exist, and `foundational-refactoring-rules.md` already says "deterministic tools over agents". No habit or step that turns a repeated rule violation into a check.

### 2026-10-17 — grilled; decisions

- Maintainer rule in `CONTRIBUTING.md` plus one line in `AGENTS.md`: a rule broken twice becomes a check in `validate_skills.py` with a unit test; what no tool can decide stays prose. Nothing in the skill texts.
- First check built: `README.md` and `docs/**` (not `docs/adr/`, `docs/agents/`) cite no `ADR-NNNN`, `docs/adr/NNNN-` path, `PR #N`; `.scratch/` paths only in the reviewer-loop playbook. "ticket 42" stays legal as a call example.
- Deferred: the check that every `Requires` parent carries its child's Tracks — belongs to the tooling-tree-as-tables decision.
- Reviewer loop: one sentence in the playbook (a violation standing in the log twice is named to the maintainer as a missing check); no automatic detection.
- "Docs stay in sync" stays a written rule (not mechanically checkable). No ADR, glossary word or FAQ.
- Noted for later: rework the playbooks so they can ship with the suite.
