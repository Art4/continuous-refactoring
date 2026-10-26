# `requireCoverageContribution` as a third coverage-metadata Stage

Type: task

PHPUnit 13.2 added `requireCoverageContribution`: a test that contributes nothing to code coverage is marked risky.
Left out of the two coverage-metadata Stages (`coverage-metadata-required`, `coverage-metadata-strict`, ADR-0090).

Open questions:

- Is it worth a Stage of its own, after `coverage-metadata-strict`, or does it only catch tests that are
  `#[CoversNothing]` by design?
- How does it interact with `#[Medium]`/`#[Large]` integration and functional tests?
- Applies only on PHPUnit 13.2 or newer — `applies_when` like the strict Stage's.
