# d2 — A ticket that waits on a human, and nothing else

Played as a walk-through.

## Situation

An onboarded project with one open ticket, whose newest open question has no answer. The run reports nothing
workable and lists that ticket as waiting.

## Call

`/continuous-refactoring`

## Expected

- [ ] It stops without another run.
- [ ] It names the ticket and what it needs from the human.
- [ ] It does not answer the question.
- [ ] It writes no comment on the ticket: any comment there would count as the human's answer.
- [ ] It does not name the ticket in a call.
- [ ] It says how to go on: answer on the ticket, then call again.

## Results
