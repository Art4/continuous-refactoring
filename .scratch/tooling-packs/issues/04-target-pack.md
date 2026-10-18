# 04 — The target's own Pack

Type: task
Status: ready-for-agent
Blocked by: 01

**What to build**

- A target may keep a Pack of its own in the format of `pack.json`, with `"$schema"` pointing at the
  suite's schema; `## Refactoring operations` names where it lives (`refactoring-operations.md`).
- It may add Tools, Stages and Roles, never redefine or remove the suite's (D21); a collision ends the
  parser with exit code 2, and the run names it.
- The scan and the parser read it beside the suite's Packs; its *Applies when* is judged like theirs.
- An example of a target's Pack, and the onboarding or Housekeeping text that offers it — where the
  example lives is this ticket's decision (D17).
- Docs: `README.md` or a playbook section on adding a tool of one's own; FAQ; a changelog fragment.

**Done when** a fixture target with its own Pack gets its Stages in the parser's output, a fixture whose
Pack reuses a suite slug ends with exit code 2, and tests and validator are green.

## Comments
