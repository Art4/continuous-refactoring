# d14 — The human holds a draft

Played as a walk-through.

## Situation

An onboarded PHP project on GitLab, `acme/shop`, settings `review only`, five rounds, in an environment with a timer.
The agent works under the human's own account. Round 1's review found !30 for ticket #4 mergeable and marked it
ready. During the cadence the human made !30 a draft again, with no comment, and merged !29, so GitLab now reports
!30 `has_conflicts: true`. Ticket #5 is workable. The wake-up has just arrived.

## Call

`/continuous-refactoring`, with the first round done and the wake-up just arrived.

## Expected

- [ ] *Ready* reads !30's timeline: the newest change to draft has no comment of the suite with it, so it is the
      human's hold, although the account is the same.
- [ ] !30 gets no base update, no review and no rework, and no call names #4.
- [ ] Round 2 works #5.
- [ ] Its Status lists !30 as held as a draft by the human, waiting for them.

## Results
