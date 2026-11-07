# 04 — Every scenario names what it covers

Type: task
Status: done
Blocked by: —

**What to build** (spec S2.1; Q8)

- A `Covers:` line in every scenario under `docs/agents/evals/`, naming the skill files (paths under `skills/`) whose
  behaviour it tests.
- `validate_skills.py`: every scenario has the line, and every path it names exists. A unit test with a negative
  control.
- `docs/agents/evals/README.md`: what the line is for.

**Done when** every scenario has the line, the check is in, and tests and validator are green.

## Comments

- 2026-11-07: Done. All 24 scenarios carry the line under their title; `scenario_covers_issues` checks the line,
  that it names at least one path, and that each path lies under `skills/` and exists. The README's table column
  "Covers" became "Tests" so it does not read as the line. Which files a scenario names is judgement: the files
  whose rules its expected lines hold the agent to, not every file a run reads on the way.
