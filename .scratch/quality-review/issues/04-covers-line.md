# 04 — Every scenario names what it covers

Type: task
Status: open
Blocked by: —

**What to build** (spec S2.1; Q8)

- A `Covers:` line in every scenario under `docs/agents/evals/`, naming the skill files (paths under `skills/`) whose
  behaviour it tests.
- `validate_skills.py`: every scenario has the line, and every path it names exists. A unit test with a negative
  control.
- `docs/agents/evals/README.md`: what the line is for.

**Done when** every scenario has the line, the check is in, and tests and validator are green.
