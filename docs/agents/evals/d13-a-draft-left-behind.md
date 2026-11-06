# d13 — A draft left behind

Played as a walk-through.

## Situation

An onboarded PHP project on GitHub, `acme/shop`, settings `review only`, five rounds, in an environment with a timer.
The session of an earlier Driver ended while its run was opening a merge request: !21 for ticket #9 (PHPStan Level 2)
is open as a draft, its CI green, with no comment on it. The Driver never reviewed it. Ticket #10 is workable; nothing
else is open.

## Call

`/continuous-refactoring`

## Expected

- [ ] *Ready* finds !21 a draft of the suite — opened as a draft and never ready — with no comment of the Driver
      since its last commit.
- [ ] With its checks green, the round goes on at the review with !21; no new run starts for #9.
- [ ] A mergeable verdict marks !21 ready with `gh pr ready`, and the round ends only once the forge shows it ready;
      the comment says it is mergeable, and the merge stays the human's.
- [ ] Round 2 works #10, and its merge request opens as a draft.

## Results

2026-11-06, skill commit 9edb93c: pass, every line, as a walk-through.
