# 11 — Encode repeated rule violations as checks

Type: task
Status: open

When the same rule is violated or restated twice (e.g. forge-facing text citing suite paths, docs citing ADR numbers), add it as a check in scripts/validate_skills.py instead of another paragraph. Possibly: have the findings log surface repeated violations as a proposal.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

**Tooling-tree table:** the planned check that every `Requires` parent carries its child's Tracks is a case of this rule and belongs in the validator or parser, not in prose. A tooling node itself is the structured form of a lesson, which supports keeping tools as nodes rather than prose.

## Comments
