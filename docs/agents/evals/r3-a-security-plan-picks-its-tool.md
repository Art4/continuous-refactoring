# r3 — A Security plan picks its tool

Played as a walk-through, once per case.

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
