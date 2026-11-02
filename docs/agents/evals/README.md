# Scenarios

Hand-written tests of the skill text, played before a change to it merges. No runner and no CI step. For a test on a
real target, see [the field eval](../field-eval.md).

Each file is one scenario: the situation, the call, the expected behaviour. A scenario passes when every line of
its list holds.

| Scenario | Covers | How it is played |
|---|---|---|
| `p1-unknown-tool` | the Pack route | live |
| `p2-slug-clash` | the Pack route | live |
| `p3-not-onboarded` | the Pack route | walk-through |
| `d1-nothing-workable` | the Driver | walk-through |
| `d2-only-a-waiting-ticket` | the Driver | walk-through |
| `d3-rework-runs-out` | the Driver | walk-through |
| `d4-three-open-merge-requests` | the Driver | walk-through |
| `d5-no-settings` | the Driver | walk-through |
| `d6-not-onboarded` | the Driver | walk-through |
| `d7-no-timer` | the Driver | walk-through |
| `d8-merge-mode` | the Driver | walk-through |
| `d10-a-stop-after-a-wake-up` | the Driver | walk-through |

## Playing one

Always a fresh subagent, with the skill under test and nothing of the conversation that changed it. Hand it the
scenario's *Situation* and *Call*, **never the expected behaviour**. Hold its result against the list yourself.

- **Live:** on a copy of a fixture, in a temporary folder outside this repository, set up as the scenario says.
  Copy it, run `git init`, commit. The agent works for real on that copy.
- **Walk-through:** there is no forge to work on, so the subagent is told the state and what each step returns. It
  says what it would do, step by step, and writes nothing. It is told to read the skill and to say which skill,
  tool and subagent it would call.

A run of a scenario changes no real skill file and nothing outside the temporary folder. Where a scenario fails, the
finding goes back to the skill text; change a scenario only when the behaviour it expects is meant to change.
Note the result under `## Results` in the scenario's file: date, skill commit, pass or the lines that failed.
