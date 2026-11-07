# d12 — A conflict after the human merged

Played as a walk-through.

Covers: `skills/continuous-refactoring/SKILL.md`, `skills/continuous-refactoring-run/references/updating-the-base.md`

## Situation

An onboarded PHP project on GitHub, `acme/shop`, settings `review only`, five rounds, in an environment with a timer.
Round 1 ended with two open merge requests the review found mergeable: !12 for ticket #5 (PHP CS Fixer: take in the
rule `ordered_imports`) and !13 for ticket #6 (Rector: Code Quality set), both touching `src/Order/Checkout.php`. Its
history is linear, and !12 and !13 hold only the suite's commits. During the cadence the human merged !12. GitHub now
reports !13 `mergeable: CONFLICTING`: the import block of `Checkout.php`, which the fixer reordered and Rector's run
changed too. Ticket #7, PHPStan Level 3, is workable; nothing else is open. The wake-up has just arrived.

## Call

`/continuous-refactoring`, with the first round done and the wake-up just arrived.

## Expected

- [ ] *Ready* reads the merge state of !13, finds it blocked by a conflict, and has it updated in a run of its own
      that names #6, before the round's run.
- [ ] That run rebases (linear history, only its own commits), resolves the conflict by taking the default branch's
      side and running Rector again, and pushes with `--force-with-lease`.
- [ ] The checks run on the updated branch, and one comment on !13 names `Checkout.php`, !12 as what it collided
      with, and that Rector was run again.
- [ ] No new review is asked for !13: the conflict was in a tool's output.
- [ ] The base update counts as no round and no rework: round 2's run works #7, and the Driver's count of rounds is
      two after it.

## Results

2026-11-05, skill commit bd397e8: pass, every line, as a walk-through. It named one gap: the Driver's call named a
ticket only for a rework, its next part, an answer or the human's wish; a base update is now among them.

2026-11-06, skill commit 9edb93c: still passes; the base update leaves !13's draft or ready state as it was.
