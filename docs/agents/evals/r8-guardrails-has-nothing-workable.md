# r8 — Guardrails has open tickets, and none is workable

Played as a walk-through, once per variant.

Covers: `skills/continuous-refactoring-run/SKILL.md`, `skills/continuous-refactoring-run/references/worklist.md`, `skills/continuous-refactoring-run/references/track-choice.md`, `skills/continuous-refactoring-run/references/track-scan.md`, `skills/continuous-refactoring-run/references/filing-a-ticket.md`, `skills/continuous-refactoring-run/references/selection.md`, `skills/continuous-refactoring-run/references/tooling-parser.md`

## Situation

An onboarded PHP application on GitHub, `acme/shop`: `composer.json` has `"type": "project"` and requires
`php: ^8.2`; its tracker file has no **BC promise** operation. Housekeeping is set up, and its ticket is not due. No
Tooling Pack of its own, no Twig.

Every Safety Net Stage of the generic and the PHP Pack except `roave-bc-check` has a closed ticket whose merge
request was merged, PHPStan up to Level 5 among them; what they set up runs in CI. `roave-bc-check` has no ticket.
No rejection is recorded, and no ticket, plan or pull request carries an `Opener:` line.

Two Guardrails tickets are open, and no other Guardrails Stage has ever had a ticket:

- #51 "PHPStan Level 6", with open pull request #52, mergeable, CI green.
- #53 "PHP CS Fixer rollout", with no merge request. Its newest comment is an open question of the suite, "Take in
  the `@PER-CS2.0` set rule by rule, or the rules your old config listed first?", with no answer after it.

No PHPMD, coverage floor or coverage metadata is in place; nothing else of Guardrails runs in CI. No Investigation
ticket is open.

**Variant B.** As above, except that #53 carries no open question: it is workable.

**Variant C.** As variant A, a run later: that run's scan filed its tickets, and each of them that was workable now
has an open pull request of the suite, mergeable, CI green. PHPStan Levels 8, 9 and 10 have no ticket.

## Call

`/continuous-refactoring-run autonomous`

## Expected

- [ ] The worklist gives #51 the state in review and, in variant A, #53 waiting; in variant B, #53 workable.
- [ ] Variant A: Guardrails has no workable ticket, so its trace is asked; a Stage that applies has no ticket, so
      its scan is due, and Track choice recommends Guardrails.
- [ ] Variant A: the scan proposes no ticket for PHPStan Level 6 or the PHP CS Fixer rollout, which have theirs,
      and none for a Tool on request.
- [ ] Variant A: filing creates a ticket for each proposal, PHPMD and the coverage floor among them, marking the
      blocked ones as blocked.
- [ ] Variant A: selection picks one of the new tickets whose blockers are done, not #51 or #53; nothing is posted
      on #53.
- [ ] Variant A: the scan proposes PHPStan Level 7, blocked by #51, and no ticket for Levels 8 to 10; its report
      names them in a *Later* line, behind Level 7.
- [ ] Variant B: no Guardrails scan runs; Track choice recommends Guardrails, and selection picks #53.
- [ ] Variant C: the trace finds PHPStan Levels 8 to 10 not known but beyond the horizon, from a parser call with the
      seed from the trace, and counts them as accounted for; no Guardrails scan runs.
- [ ] Variant C: the run finds nothing workable and ends, naming the pull requests that wait for the human.

## Results

2026-11-07, with the rule that a tooling Track's trace is asked once it has no workable ticket: variant B passes,
every line, as a walk-through. Variant A failed one line on the first play: `track-scan.md` skipped a Stage with an
open ticket only in "a scan the call asked for", so the scan proposed PHPStan Level 6 and the PHP CS Fixer rollout
again and filing caught them by search. The row now holds for every scan; the replay passes every line, filing ten
tickets and picking PHPMD.

2026-11-07, on 0e29b63, the first playing of every scenario with the runner and a separate judge: pass, every line, both variants, as a walk-through, by one player.

2026-11-08, on cecafc1 with the decision-point paragraph replaced by a pointer to the run's `SKILL.md`: pass, every line, every variant, as a walk-through, by one player; the decision points keep findings, options and one recommendation.
2026-11-11, on f053957 with a due scan judging only the Stages not known and filing keeping a sibling's ticket out of its hits: pass, every line, both variants, as a walk-through, by one player. Then the text said that such a scan searches every Stage, and that the adoption's merge request closes the rollout's ticket where the code must run without ES2015.
2026-11-11, on 6011078 with the trace asked beside a ticket that has delivered a part, and the baseline ticket defined: pass, every line, both variants, as a walk-through, by one player. Then the trace's sentence was split for reading, and its search keeps only hits that match the Stage.
