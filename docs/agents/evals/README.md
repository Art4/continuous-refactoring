# Scenarios

Hand-written tests of the skill text, played before a change to it merges, with the repository's own skill
`/play-scenarios`. No CI step. For a test on a real target, see [the field eval](../field-eval.md); what held in the field is in [the field record](../field-results.md).

Each file is one scenario: the situation, the call, the expected behaviour. Its prefix names what it tests: `p`
the Pack route, `d` the Driver, `r` a run. A scenario passes when every line of
its list holds.

Under its title, a `Covers:` line names the skill files whose behaviour the scenario tests, as paths under
`skills/`. A change to one of those files starts from the scenarios that name it, and plays those whose expected lines bear on
what the change moves. The validator checks that every scenario
has the line and that each path exists; which files belong on it is the author's judgement.

| Scenario | Tests | How it is played |
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
| `d9-started-by-an-agent` | the Driver | live, in a real session |
| `d10-a-stop-after-a-wake-up` | the Driver | walk-through |
| `d11-the-human-asks-for-changes` | the Driver | walk-through |
| `d12-a-conflict-after-a-human-merge` | the Driver | walk-through |
| `d13-a-draft-left-behind` | the Driver | walk-through |
| `d14-the-human-holds-a-draft` | the Driver | walk-through |
| `r1-opener-seen` | a run | walk-through |
| `r2-opener-after-rejection` | a run | walk-through |
| `r3-a-security-plan-picks-its-tool` | a run | walk-through |
| `r4-tests-that-check-little` | a run | walk-through |
| `r5-the-tool-is-in-place` | a run | walk-through |
| `r6-a-conflict-it-cannot-resolve` | a run | walk-through |
| `r7-safety-net-met-guardrails-open` | a run | walk-through |
| `r8-guardrails-has-nothing-workable` | a run | walk-through |
| `r9-frontend-without-a-linter` | a run | walk-through |
| `r10-frontend-already-linted` | a run | walk-through |

## Playing one

Always a fresh subagent, with the skill under test and nothing of the conversation that changed it. Hand it the
scenario's *Situation* and *Call*, **never the expected behaviour**. A second fresh subagent, the judge, holds its
record against the list line by line.

- **Live:** on a copy of a fixture, in a temporary folder outside this repository, set up as the scenario says.
  Copy it, run `git init`, commit. The agent works for real on that copy.
- **Walk-through:** there is no forge to work on, so the subagent is told the state and what each step returns. It
  says what it would do, step by step, and writes nothing. It is told to read the skill and to say which skill,
  tool and subagent it would call.

A run of a scenario changes no real skill file and nothing outside the temporary folder. Where a scenario fails, the
finding goes back to the skill text; change a scenario only when the behaviour it expects is meant to change.
Note the result under `## Results` in the scenario's file: date, skill commit, pass or the lines that failed.
