# r3 — A Security plan picks its tool

Played as a walk-through, once per case.

Covers: `skills/continuous-refactoring-run/references/design-point.md`, `skills/continuous-refactoring-run/references/packs/php/psalm.md`, `skills/continuous-refactoring-run/references/packs/php/semgrep.md`

## Situation

An onboarded PHP project on GitHub, `acme/shop`. Its Safety Net is fulfilled; `ci-runner` is fulfilled by a GitHub
Actions workflow. Semgrep and Psalm Taint Analysis are not in place, have no ticket and no rejection. No ADRs, no
glossary. The open Investigation ticket is the only workable one; it names the signal Security and was filed by an
earlier exploration that read the code.

- **Case A.** PHPStan is fulfilled up to Level 5. Ticket #31: "`OrderController::index` passes `$_GET['sort']`
  into the `ORDER BY` of the SQL string `OrderRepository::list` builds, unchecked." The repository's other
  queries use bound parameters.
- **Case B.** As case A, but PHPStan is fulfilled only up to Level 2, and Psalm is not in the project.
- **Case C.** PHPStan is fulfilled up to Level 5. Ticket #32: "`UserService::register` hashes passwords with
  `md5()` and compares them with `==`." The tests reach `UserService`.

## Call

`/continuous-refactoring-run autonomous`

## Expected

- [ ] The run works the ticket. Its design ends in a `Plan` comment, or, where it judges the fix a change of
      behaviour, in an open question; the Opener line stands in whichever it posts, written with the Tool's key.
- [ ] Case A: one Opener line, `Opener: psalm-taint-analysis — …`, and none for `semgrep`.
- [ ] Case B: one Opener line, `Opener: semgrep — …`, and none for `psalm-taint-analysis`.
- [ ] Case C: one Opener line, `Opener: semgrep — …`.
- [ ] In every case the run files no tooling ticket and does not set the tool up itself.

## Results

2026-11-03, skill commit 9654c4b: pass, every line and case, as a walk-through. The first play named two gaps, closed in that
commit: a design that ends on a change of behaviour wrote no plan and so lost its Opener (case C), and the line named
the Tool by its name instead of its key (case A). In the replay both A and C judged the fix a change of behaviour and
carried the line in the open question; B planned and carried it under `Decisions`.

2026-11-07, on 0e29b63, the first playing of every scenario with the runner and a separate judge: pass, every line, every case, as a walk-through, the three cases by one player.
