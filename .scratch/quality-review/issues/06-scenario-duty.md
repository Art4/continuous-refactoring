# 06 — Playing the affected scenarios before a merge

Type: task
Status: done
Blocked by: —

**What to build** (spec S2.4; Q4, Q8)

- `AGENTS.md`, *Git workflow*: a PR that changes a skill file named in a scenario's `Covers:` line plays those
  scenarios with the runner before it merges, notes the results at its head commit under `## Results`, and names
  them in its description.
- `CONTRIBUTING.md`: the same, for a human contributor.
- No check yet; it becomes one when the duty is broken twice.

**Done when** both files carry the duty and tests and validator are green.

## Comments

- 2026-11-07: Done, with the duty narrowed (spec Q26): the `Covers:` line is where the choice starts; a PR plays
  those covering scenarios whose expected lines bear on what it moves, and names the ones it left out with the
  reason. `AGENTS.md`, *Git workflow*, `CONTRIBUTING.md`, the scenarios README and the runner's *Pick* say so.
