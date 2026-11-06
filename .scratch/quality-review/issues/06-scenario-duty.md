# 06 — Playing the affected scenarios before a merge

Type: task
Status: open
Blocked by: 05

**What to build** (spec S2.4; Q4, Q8)

- `AGENTS.md`, *Git workflow*: a PR that changes a skill file named in a scenario's `Covers:` line plays those
  scenarios with the runner before it merges, notes the results at its head commit under `## Results`, and names
  them in its description.
- `CONTRIBUTING.md`: the same, for a human contributor.
- No check yet; it becomes one when the duty is broken twice.

**Done when** both files carry the duty and tests and validator are green.
