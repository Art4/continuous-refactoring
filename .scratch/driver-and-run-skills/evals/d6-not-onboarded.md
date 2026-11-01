# d6 — A project without `## Refactoring operations`

Played as a walk-through: the onboarding asks a human.

## Situation

No `## Refactoring operations` section in the tracker file. A human is in the session and answers.

## Call

`/continuous-refactoring`

## Expected

- [ ] It sees the missing section before any round.
- [ ] It invokes `continuous-refactoring-run` in the main session, not in a subagent, because the onboarding asks.
- [ ] It does not tell the human to call something by hand first.
- [ ] After the onboarding it stops: commit, then call again. No round follows.
- [ ] It sets no cadence and schedules nothing.

## Results
