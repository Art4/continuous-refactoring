# d4 — `review only` with three open merge requests

Played as a walk-through. The limit is "more than three", so this is its boundary.

## Situation

`review only`. Three merge requests of the Driver are open and mergeable; none has been merged. Workable tickets
remain.

## Call

`/continuous-refactoring`

## Expected

- [ ] With three open it does not stop: three is not more than three.
- [ ] It works one more round, and that round ends with a fourth merge request, mergeable.
- [ ] Now more than three are open: it stops, and starts no further run.
- [ ] It merges none of them.
- [ ] It lists the open merge requests as waiting for the human.

## Results
