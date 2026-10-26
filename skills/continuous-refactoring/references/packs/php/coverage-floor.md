# Test Coverage Floor

The Tool for the Role Test Coverage in the PHP Pack; measured with PHPUnit's own coverage report, PCOV or Xdebug as the driver. The concrete driver is chosen at adoption time and not pinned here. Its Stages are `coverage-floor`, then `coverage-metadata-required` and `coverage-metadata-strict`, which make the coverage count only what a test means to test.

**Why this order.** It needs `phpunit`: coverage is a report over an existing test suite, and there is nothing to measure before a runner exists. A Guardrails Stage: workable only once the Safety Net is fulfilled. Adopting it never holds structural work up. The two metadata Stages come after the floor because they change what it measures, and one after the other because PHPUnit has neither a baseline for risky tests nor a switch per test directory: each switch holds for the whole suite at once, so two smaller merge requests are the only way to stage the work.

### `coverage-floor`

- **Purpose:** turn test coverage from an assumption into measured evidence: a self-tightening floor (the Ratchet below) that only ever climbs, plus real per-file numbers. Once fulfilled, the search for structural candidates reads the coverage report's per-file numbers (Clover XML) for the Untested / hard-to-test signal (`../../signals.md`) instead of the generic "read the test suite" heuristic: a file more than 20 percentage points under the current `.coverage-floor` value is this factor's own evidence, not a separate criterion.
- **Fulfilment check:** `phpunit.xml.dist` (or `phpunit.xml`) declares a `<coverage>` report section, and a coverage-floor value is committed to the target: `.coverage-floor`, a file containing a single numeric percentage such as `62.5`. An absent or unparseable file counts as no floor set, which keeps the Stage unfulfilled. Once `ci-runner` is fulfilled it additionally needs a CI job that invokes the coverage-enabled run (the check looks for the `--coverage` invocation in the CI job files, tolerant of whichever concrete flag the runner uses). It is a self-wired CI gate, the same shape as PHPUnit's; with no CI yet, local adoption alone still fulfils it. The check never looks for "pcov" or "xdebug" by name, only for coverage configured and, once CI exists, enforced.
- **MR scope:** `phpunit.xml.dist`'s `<coverage>` section with Clover XML as report format (the format the search for structural candidates reads back), a coverage driver wired into the local and CI run, the initial `.coverage-floor` value (whatever the very first coverage run measures, never invented) and, once `ci-runner` is fulfilled, a CI step that fails when a fresh run drops below the committed floor. PCOV is the default driver, faster than Xdebug with no debugging overhead. A reviewer who prefers Xdebug can ask for it in review without the Stage being blocked or rejected.

### `coverage-metadata-required`

- **Purpose:** every test states what it covers, so a class counts as covered only where a test means to test it, not where a test of another class runs through it. The per-file numbers the search reads then show the classes that have no test of their own.
- **Fulfilment check:** the PHPUnit config sets `requireCoverageMetadata="true"` (`forceCoversAnnotation="true"` up to PHPUnit 9) and lets a risky test fail the run: `failOnRisky="true"` or `failOnAllIssues="true"`, and no `doNotFailOnRisky`. A test without coverage metadata is only marked risky, and a risky test adds nothing to the coverage, so without the failing the switch would lower the coverage silently. The coverage-enabled run is green.
- **MR scope:** the two config settings, and the metadata on every test class, in the form the target's PHPUnit reads and the test file already uses — attributes (`#[CoversClass]`, `#[UsesClass]`) from PHPUnit 10, annotations (`@covers`, `@uses`) below it, Pest's `covers()` on Pest; no file mixes both forms.
  - A unit test covers exactly one class, the one it tests; another class it runs is listed as used, not covered.
  - A class whose coverage came only from the test of another class gets a test of its own, so the floor holds (the Ratchet's one exception, below, is for where it cannot).
  - A test in `tests/Integration/` or `tests/Functional/` covers the class it enters through.
  - `tests/README.md` gains the rule "a unit test covers exactly one class, the one it tests; everything else it runs it uses", added to the target's file as it stands.
  - Where Infection is fulfilled (`infection.md`), it is run again in full: a mutant is now judged only by the tests that cover its line, so the score can drop, and its minimum follows the same rule as the floor.

### `coverage-metadata-strict`

Applies only on PHPUnit 10 or newer, and not on Pest: Pest has no counterpart to `#[UsesClass]`, so a Pest test that runs a collaborator has no way to name it. On PHPUnit 9 the Stage applies once the target moves to PHPUnit 10.

- **Purpose:** every test also names what it runs without covering it, so code a test reaches by accident makes it risky instead of counting as covered. A class an extract creates then cannot slip in without its own test and without the old test saying it uses it.
- **Fulfilment check:** the config of `coverage-metadata-required` and `beStrictAboutCoverageMetadata="true"`; the coverage-enabled run is green. PHPUnit applies this check only in a run that collects coverage, so the coverage floor's CI job is the gate, not the plain test job.
- **MR scope:** the setting; `#[UsesClass]` (or `#[UsesMethod]`) on every unit test for the code it runs but does not cover; `#[Medium]` on the test classes in `tests/Integration/` and `#[Large]` on those in `tests/Functional/`. PHPUnit skips this check for medium and large tests, so tests that run real collaborators keep their `#[CoversClass]` and need no list of everything behind it. `tests/README.md` gains the rule "a unit test lists what it uses; an integration test is `#[Medium]`, a functional test `#[Large]`", added to the target's file as it stands. Infection as for `coverage-metadata-required`.

## The Ratchet: a floor that only climbs

A fixed percentage picked once (70%, 80%, …) would be unreachable on day one for plenty of legacy targets and would block the Stage for good instead of building gradual pressure. `.coverage-floor` instead starts at whatever the target's first real coverage run measures and only ever rises from there, through an ordinary human-reviewed commit, never a value the CI writes back by itself even when a run exceeds it. Coverage rising is what happens when someone adds or strengthens a test; that should not force a merge request of its own, but it should not happen silently outside version control either. A normal commit bumping `.coverage-floor` is the right amount of ceremony, as `phpstan-baseline.neon` only ever shrinks through a real, committed code change.

**The one exception.** A metadata Stage changes what is measured: coverage a class got only from the test of another class is no longer counted. Its merge request writes the missing tests so the floor holds. Where they do not fit into one reviewable merge request, the floor is measured again with the Stage's settings and set to that value, once. That is a decision of the plan (`../../design-point.md`), asked where the run asks; the merge request names the old and the new value and the classes left without a test of their own. They need no ticket: the per-file numbers show them to the search for structural candidates. Infection's `minMsi` and `minCoveredMsi` follow the same rule in the same merge request.

## Working under the metadata Stages

The rules are the target's `tests/README.md`; this is what they mean for a change.

- A new class gets a test of its own that covers it.
- After an extract or a move, the tests that now run the new class without covering it list it as used. That is the metadata following the code, not a weaker check: the test's assertions stay as they are.
- A test that covers the new class too, besides its own, is wrong under the rule; the new class's own test covers it.
