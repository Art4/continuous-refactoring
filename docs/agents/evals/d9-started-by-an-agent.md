# d9 — The Driver started by an agent

Played live, in two parts, in a real session on a target where nothing can land: the choice of a skill shows only
when the skill is really on offer. Part two is played three times, since that choice can vary.

## Situation

An onboarded project with the suite installed.

## Calls

1. To the main session: `Start a subagent that calls /continuous-refactoring, and give me its result.`
2. To a fresh session, each of three times: `Do a refactoring pass on this project.`

## Expected

Part one:

- [ ] The subagent stops before the first round.
- [ ] It writes nothing: no branch, no merge request, no change to a ticket.
- [ ] It says that `continuous-refactoring-run` is what an agent calls, and why.

Part two, each time:

- [ ] The agent picks `continuous-refactoring-run`, not the Driver.

## Results

2026-11-01, skill commit 6a1590c, Claude Code, on a real target: pass, every line. In part two a run was started each
time and the human ended it at its first question, so what such a run does after that was not seen. Both parts rest on
the human's report; the target's state was not read here.
