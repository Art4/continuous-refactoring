# r7 — The Safety Net is met, Guardrails work is open

Played as a walk-through, once per variant.

Covers: `skills/continuous-refactoring-run/references/worklist.md`, `skills/continuous-refactoring-run/references/reconcile.md`, `skills/continuous-refactoring-run/references/design-point.md`, `skills/continuous-refactoring-run/references/track-choice.md`, `skills/continuous-refactoring-run/references/track-scan.md`, `skills/continuous-refactoring-run/references/filing-a-ticket.md`, `skills/continuous-refactoring-run/references/selection.md`, `skills/continuous-refactoring-run/references/tooling-parser.md`, `skills/continuous-refactoring-run/references/planning-a-baseline-ticket.md`, `skills/continuous-refactoring-run/references/packs/php/php-cs-fixer.md`

## Situation

An onboarded PHP application on GitHub, `acme/shop`, as the fixture `fixtures/php/php-app-onboarded/project`
holds it: `composer.json` has `"type": "project"` and requires `php: ^8.2`, and no release is tagged. Its tracker
file holds the GitHub template's operations (Claim, Linked merge request, Rejected as an issue closed as not planned)
and a **Housekeeping** bullet; no Candidate, Priority, Ready after plan or **BC promise**. Housekeeping is set up, and
its ticket is not due. No Tooling Pack of its own.

Every Safety Net Stage of the generic and the PHP Pack except `roave-bc-check` and `bc-promise` has a closed ticket whose merge
request was merged: CI Runner, EditorConfig, Composer, PSR-4, PHP CS Fixer adoption, PHPUnit, PHPStan Levels 0 to
5, and the Rector PHP set, dead code, code quality and type coverage Stages. What those tickets set up is in the
repository and runs in CI. `bc-promise`, a Tool on request, was never asked for, and neither it nor `roave-bc-check` has a ticket or a rejection. No rejection is recorded at all, and no
ticket, plan or pull request carries an `Opener:` line.

Two Guardrails tickets are open: #51 "PHPStan Level 6", with open pull request #52, mergeable, CI green; and #53
"PHP CS Fixer: take in the remaining rules", with no merge request, no blocker and no open question. No Investigation ticket is open.

**Variant C.** As variant A, except that #53 carries the suite's plan from an earlier run, its newest comment: take in
`single_quote` for `src/` first. No merge request came of it, and the main config still marks `single_quote`
`Not yet:`, with no rollout file.

**Variant B.** As above, except that Rector type coverage never had a ticket: CI already ran it before the suite
was installed, and the first Safety Net scan found it in place.

## Call

`/continuous-refactoring-run autonomous`

## Expected

- [ ] The worklist gives #51 the state in review and #53 workable, both in Guardrails.
- [ ] Reconcile names #51 as in review in one sentence and lays out no decision point for it.
- [ ] The worklist judges, before any trace is asked, that the generic and the PHP Pack apply and that
      `roave-bc-check` does not, putting it into `not_applicable`.
- [ ] The Safety Net's fulfilment is read from a call with a seed — never from the seedless call — and is
      fulfilled.
- [ ] The run does not end on the Safety Net; no "Safety Net is waiting for merges" or "Safety Net is unfinished".
- [ ] Track choice recommends Guardrails, and selection picks #53, not #51.
- [ ] Variant A: the design point finds no plan on #53 that stands and goes on to *Who plans*, which says in one
      sentence that the suite plans, as the run is autonomous; the plan follows `planning-a-baseline-ticket.md`.
- [ ] Variant A: the plan takes in `native_function_casing`, the rule in the fewest files. A part that takes it whole
      plans no rollout file and one commit; a part that cuts it creates the rollout file in three commits, each
      leaving `check` green: by hand the file, its cache in `.gitignore` and `rolled out via` on the `Not yet:`
      line; the formatting run; by hand the CI step running `check` with it.
- [ ] Variant C: the design point finds that #53's plan stands, since `single_quote` and `src/` are not taken in yet;
      no new plan is written, and the run goes on to the implement point with it.
- [ ] Variant C: the implementation creates the rollout file in the three commits variant A's line lists, its
      formatting run being the rollout file's, then the main config's.
- [ ] Variant A: Safety Net has a trace, and no Safety Net scan runs.
- [ ] Variant B: Safety Net has no trace, its scan runs, judges Rector type coverage fulfilled, and proposes no
      ticket to work for it.
- [ ] Variant B: filing creates one ticket for Rector type coverage and closes it at once as done, its text naming
      what was found in place; the run goes on to Guardrails within the same run.

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

2026-11-07, with the rule that a tooling Track's trace is asked once it has no workable ticket: variant A passes,
every line, as a walk-through; #53 is workable, so no Guardrails scan runs.

2026-11-07, on 0e29b63, the first playing of every scenario with the runner and a separate judge: pass, every line, both variants, as a walk-through, by one player.

2026-11-08, on c11f6d4 with the in-place ticket for a tool a scan finds with no ticket: pass, every line, both variants, as a walk-through, by one player. The hand-on line for in-place tickets alone was then written out (back to Track choice, the Track marked as tried), wording only.
2026-11-11, on f053957 with a due scan judging only the Stages not known and filing keeping a sibling's ticket out of its hits: pass, every line, both variants, as a walk-through, by one player. Then the text said that such a scan searches every Stage, and that the adoption's merge request closes the rollout's ticket where the code must run without ES2015.
2026-11-11, on 6011078 with the trace asked beside a ticket that has delivered a part, and the baseline ticket defined: pass, every line, both variants, as a walk-through, by one player. Then the trace's sentence was split for reading, and its search keeps only hits that match the Stage.
2026-11-12, on 882656b with reconcile's In review line as information, never a finding: variant A passes, every line, as a walk-through, by one player.
2026-11-12, on 14d424b with a baseline ticket with no plan that stands going on to *Who plans*: variant A passes, every line, as a walk-through, by one player. The interactive recommendation was played as a probe beside it (p1 B: pass).
