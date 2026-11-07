# d6 — A project without `## Refactoring operations`

Played as a walk-through: the onboarding asks a human.

Covers: `skills/continuous-refactoring/SKILL.md`, `skills/continuous-refactoring-run/SKILL.md`, `skills/continuous-refactoring-run/references/onboarding-setup-interview.md`

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

2026-11-01, skill commit 83f57b2: pass, every line, as a walk-through. An earlier round on the text before it passed too and named where the agent guessed; those gaps were closed and this is the replay.

2026-11-07, on 0e29b63, the first playing of every scenario with the runner and a separate judge: pass, every line, as a walk-through.
