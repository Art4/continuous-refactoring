# d7 — An environment with no timer, and a call inside the cadence

Played as a walk-through, in two steps.

## Situation

An onboarded project with workable tickets. The environment offers no way to wake a session. Step one is the first
call. Step two is a second call five minutes after the first ended.

## Calls

1. `/continuous-refactoring`
2. `/continuous-refactoring` again, five minutes later

## Expected

Step one:

- [ ] It works one round.
- [ ] It does not hold the session with a sleep or a busy loop.
- [ ] It ends and says when the next round is due.
- [ ] It sets up no schedule of its own and does not ask for one.

Step two:

- [ ] It starts a round: how often the skill is called is the user's. It neither refuses nor delays.
- [ ] It reads no time of the last round from the forge.

## Results

2026-11-01, skill commit 83f57b2: pass, every line, as a walk-through. An earlier round on the text before it passed too and named where the agent guessed; those gaps were closed and this is the replay.
