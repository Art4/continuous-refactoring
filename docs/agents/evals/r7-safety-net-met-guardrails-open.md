# r7 — The Safety Net is met, Guardrails work is open

Played as a walk-through, once per variant.

## Situation

An onboarded PHP application on GitHub, `acme/shop`: `composer.json` has `"type": "project"` and requires
`php: ^8.2`; its tracker file has no **BC promise** operation. Housekeeping is set up, and its ticket is not due. No
Tooling Pack of its own.

Every Safety Net Stage of the generic and the PHP Pack except `roave-bc-check` has a closed ticket whose merge
request was merged: CI Runner, EditorConfig, Composer, PSR-4, PHP CS Fixer adoption, PHPUnit, PHPStan Levels 0 to
5, and the Rector PHP set, dead code, code quality and type coverage Stages. What those tickets set up is in the
repository and runs in CI. `roave-bc-check` has no ticket and no rejection. No rejection is recorded at all, and no
ticket, plan or pull request carries an `Opener:` line.

Two Guardrails tickets are open: #51 "PHPStan Level 6", with open pull request #52, mergeable, CI green; and #53
"PHP CS Fixer rollout", with no merge request, no blocker and no open question. No Investigation ticket is open.

**Variant B.** As above, except that Rector type coverage never had a ticket: CI already ran it before the suite
was installed, and the first Safety Net scan found it in place.

## Call

`/continuous-refactoring-run autonomous`

## Expected

- [ ] The worklist gives #51 the state in review and #53 workable, both in Guardrails.
- [ ] The worklist judges, before any trace is asked, that the generic and the PHP Pack apply and that
      `roave-bc-check` does not, putting it into `not_applicable`.
- [ ] The Safety Net's fulfilment is read from a call with a seed — never from the seedless call — and is
      fulfilled.
- [ ] The run does not end on the Safety Net; no "Safety Net is waiting for merges" or "Safety Net is unfinished".
- [ ] Track choice recommends Guardrails, and selection picks #53, not #51.
- [ ] Variant A: Safety Net has a trace, and no Safety Net scan runs.
- [ ] Variant B: Safety Net has no trace, its scan runs, judges Rector type coverage fulfilled, files nothing, and
      the run goes on to Guardrails within the same run.

## Results

2026-11-06, on 09a6802 with ticket 03 of safety-net-gate: pass, every line, both variants, as walk-throughs. The play
named two gaps, closed in the same change: the pick-up check in `selection.md` asked for the seed from the trace,
which a Track with open tickets never has — it now takes a seed with the Packs and runtime the worklist judged; and
the situation now says that no `Opener:` line exists and that the open pull request is GitHub's #52.

2026-11-07, on the shipped glossary (ticket 03 of quality-review): variant A passes, every line, as a walk-through;
the player looked bold terms up in the glossary. It found no entry for **Investigation**, which the **Track** entry
promises below, nor for **MR scope**, and the **Refactoring operations** entry does not list **Tooling Pack**; all three
are older gaps of the vocabulary, not of the move.

2026-11-07, with the pointer reworded to look a term up only where the text leaves it unclear: variant A passes,
every line, as a walk-through; the player did not open the glossary, every term it met was clear where it was used.
