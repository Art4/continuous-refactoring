# field-test-2026-11-21

**Status:** open — five candidates filed on 2026-11-21, to be gone through with the maintainer one by one

What a watched Driver run on a real target showed on 2026-11-21: a PHP library, consumed by other projects, on GitHub,
with a BC promise added by the maintainer during the run. The Driver ran with `review only` and a content goal as its
End ("compatible with PHP 7.4 through 8.5"). It stopped when the merge request that extends the CI matrix to 8.5 was
mergeable, i.e. when the goal was reached.

Observed from this repository through the forge only; questions the Driver asked in its own session are not in the
record. Deviations from the skill text that the maintainer called fine are not tickets: filing the Roave Stage on a
consumed library, and pursuing a goal no Stage leads to.

## Candidates

- `issues/01-roave-recommended-invocation.md` — the Pack's recommended Roave invocation fails out of the box, and the
  ignore file did not take effect with it
- `issues/02-release-bound-obligations.md` — a one-off task due after the next release has no home
- `issues/03-red-check-caused-outside-the-mr.md` — the Driver's review has no rule for a red check the merge request
  did not cause, and settled its own open question
- `issues/04-candidate-mark-on-new-tickets.md` — tickets filed after the Candidate operation appeared lack its mark
- `issues/05-goal-as-driver-end.md` — a content goal as the Driver's End works but is not in its settings
