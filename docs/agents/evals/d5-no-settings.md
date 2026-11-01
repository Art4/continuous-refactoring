# d5 — A call with no settings

Played as a walk-through. This also covers a call left over from before the breaking change.

## Situation

An onboarded project with enough workable tickets for more than five rounds. Each round ends with a mergeable merge
request, and the human merges it during the cadence, so the limit on open merge requests is never reached. The
environment has a timer.

Played twice, once with each call.

## Calls

- `/continuous-refactoring`
- `/continuous-refactoring do it yourself`

## Expected

- [ ] It asks nothing before it starts.
- [ ] It says back in one sentence: `review only`, five rounds, 30 minutes, no Track.
- [ ] It calls each run in a subagent of its own and autonomous, and hands each the rules of the project's `AGENTS.md`.
- [ ] Each merge request is reviewed in a second subagent that returns only a verdict.
- [ ] It merges nothing.
- [ ] It waits 30 minutes between rounds, counted from the end of the round before.
- [ ] One status line after each round.
- [ ] It ends after the fifth round, and reports.
- [ ] A run's **Next** line is not taken for an instruction to the Driver.

## Results

2026-11-01, skill commit 83f57b2: pass, every line, as a walk-through. An earlier round on the text before it passed too and named where the agent guessed; those gaps were closed and this is the replay.
