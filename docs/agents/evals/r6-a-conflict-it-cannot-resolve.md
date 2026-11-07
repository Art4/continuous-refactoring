# r6 — A conflict it cannot resolve

Played as a walk-through.

Covers: `skills/continuous-refactoring-run/references/worklist.md`, `skills/continuous-refactoring-run/references/track-choice.md`, `skills/continuous-refactoring-run/references/updating-the-base.md`

## Situation

An onboarded PHP project on GitLab, `acme/shop`. Its Safety Net is fulfilled. Investigation ticket #21 has open merge
request !40: it extracts the discount rules of `Cart::total()` into a class `DiscountPolicy`, with a pin that passed.
Since !40 was opened, the human merged a change to `Cart::total()` that applies a voucher before the discount instead
of after it. GitLab reports !40 `has_conflicts: true`, in `src/Cart.php`. The project merges with merge commits.
Workable tickets wait in Guardrails.

## Call

`/continuous-refactoring-run do it yourself`

## Expected

- [ ] The worklist gives #21 the state needs base update, and Track choice takes it before any Track.
- [ ] The findings name !40, the conflict, and `src/Cart.php`; the recommendation to update is taken.
- [ ] It merges the default branch in, rather than rebasing.
- [ ] It finds that both sides changed the order of the same calculation, aborts the merge, and pushes nothing.
- [ ] One comment on !40 says in plain words what each side changes and asks which order to keep.
- [ ] The run ends there, without working a Guardrails ticket; its Status names !40 as handed to the human.
- [ ] A second call finds !40 not blocked again while nobody has answered, and goes on to Track choice.

## Results

2026-11-05, skill commit bd397e8: pass, every line, as a walk-through. A later run recognises the handover by the
suite's comment on !40; nothing else marks it.

2026-11-06, skill commit 9edb93c: still passes.

2026-11-07, on 0e29b63, the first playing of every scenario with the runner and a separate judge: fails "One comment on !40 … asks which order to keep": the comment says what each side changes but asks where the voucher step belongs; the other lines hold, the second call on a replay, as a walk-through.
