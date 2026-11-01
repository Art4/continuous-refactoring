# Scenarios for the Pack route and the Driver

Written before the skill text of tickets 02 and 03, so that text is held against expectations set beforehand.
Each file is one scenario: the situation, the call, the expected behaviour. A scenario passes when every line of
its list holds.

| Scenario | Needed by | How it is played |
|---|---|---|
| `p1-unknown-tool` | 02 | live |
| `p2-slug-clash` | 02 | live |
| `p3-not-onboarded` | 02 | walk-through |
| `d1-nothing-workable` | 03 | walk-through |
| `d2-only-a-waiting-ticket` | 03 | walk-through |
| `d3-rework-runs-out` | 03 | walk-through |
| `d4-three-open-merge-requests` | 03 | walk-through |
| `d5-no-settings` | 03 | walk-through |
| `d6-not-onboarded` | 03 | walk-through |
| `d7-no-timer` | 03 | walk-through |
| `d8-merge-mode` | 03 | walk-through |

## Playing one

Always a fresh subagent, with the skill under test and nothing of this effort's conversation. Hand it the
scenario's *Situation* and *Call*, **never the expected behaviour**. Hold its result against the list yourself.

- **Live:** on a copy of a fixture, in a temporary folder outside this repository, set up as the scenario says.
  Copy it, run `git init`, commit. The agent works for real on that copy.
- **Walk-through:** there is no forge to work on, so the subagent is told the state and what each step returns. It
  says what it would do, step by step, and writes nothing. It is told to read the skill and to say which skill,
  tool and subagent it would call.

A run of a scenario changes no real skill file and nothing outside the temporary folder. Where a scenario fails, the
finding goes back to the skill text; change a scenario only when the decision behind it changed in `../spec.md`.
Note the result under `## Results` in the scenario's file: date, skill commit, pass or the lines that failed.

The Pack scenarios call the run skill: `continuous-refactoring` until ticket 03, `continuous-refactoring-run` after.
