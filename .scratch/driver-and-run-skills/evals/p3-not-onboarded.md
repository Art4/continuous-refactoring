# p3 — A Pack on a project not yet onboarded

Played as a walk-through: the onboarding asks a human.

## Situation

The fixture `php-clean`, with no tracker file and no `## Refactoring operations` section. A human is there and
answers the interview.

## Call

`/<run skill> a Pack of its own for Deptrac`

## Expected

- [ ] Step 1 finds the section missing and runs the onboarding interview, inline.
- [ ] The run ends after the interview, as it does for any other call. No Pack directory is written.
- [ ] The report names the files the interview wrote and recommends committing them and calling again.
- [ ] It says that the Pack is still to come, so the human knows what the next call does.

## Results

2026-11-01, skill commit d53ce5f: pass, every line.
