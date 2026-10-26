# Coverage metadata: two Stages after the coverage floor

> Amends [ADR-0044](0044-coverage-floor-node.md): the floor may go down once, when a metadata Stage changes what is
> measured.

The coverage floor counted a class as covered when any test ran it, also the test of another class passing through.
The search for structural candidates reads the per-file numbers for the Untested / hard-to-test signal, so a class
reached only by accident looked tested. The rule that a new type gets a test of its own was checked only in review;
the old test staying green hides its absence. PHPUnit has two settings for this: one makes every test declare what it
covers (`requireCoverageMetadata`, `forceCoversAnnotation` up to PHPUnit 9), the other marks a test risky when it runs
code it neither covers nor names as used (`beStrictAboutCoverageMetadata`). Neither has a baseline or a switch per
test directory, and a risky test fails the run only with `failOnRisky` and adds nothing to the coverage.

## Decision

- **Two Guardrails Stages of the coverage floor's Tool**, both recommended through it: `coverage-metadata-required`
  requires `coverage-floor`, `coverage-metadata-strict` requires it. They change what the Role Test Coverage measures,
  so they belong to its Tool; a second Tool for the Role would be out, and a Role of their own is more than they need.
  Two Stages because each switch holds for the whole suite at once; the split is the only way to stage the work. The
  Tool's slug becomes `test-coverage-floor`, since a Tool shares its slug with a Stage only when it has one.
- **`failOnRisky` from the first Stage.** Without it, a test without metadata is only risky, and its coverage is
  silently dropped.
- **A unit test covers exactly one class**, everything else it runs it uses. A convention the Stage's merge request
  writes into the target's `tests/README.md` and carries out, not part of the Fulfilment check: checking it would
  need a script over every test class.
- **Integration tests are `#[Medium]`, functional tests `#[Large]`** under the strict Stage. PHPUnit skips the strict
  check for those sizes, so tests with real collaborators keep `#[CoversClass]` and need no list of what they use.
- **The strict Stage applies only on PHPUnit 10 or newer, not on Pest.** The size exemption is documented from 10;
  Pest has no counterpart to `#[UsesClass]`.
- **The metadata's form follows the target**: attributes from PHPUnit 10, annotations below, the form the file already
  uses; no `waits_for` on Rector's PHPUnit Set, which converts annotations anyway.
- **The floor holds, with one exception.** The merge request writes the tests a class lacks once incidental coverage
  is no longer counted. Where they do not fit into one reviewable merge request, the plan decides to measure the floor
  again and sets it once; the merge request names both values and the classes left without a test. No ticket for them:
  the signal finds them. Infection's minimum follows the same rule.
- **An existing `tests/README.md` gains the Stage's rule**, the one addition a run makes to that file.
- **No Housekeeping line.** The settings hold in every coverage run.

## Considered Options

- **A Stage of the PHPUnit Tool.** The strict check runs only when coverage is collected; its gate is the coverage job.
  Rejected.
- **One Stage for both settings.** One larger merge request, and a target with metadata already gets nothing for it.
  Rejected.
- **`#[CoversNothing]` for integration and functional tests.** No lists, but their coverage drops out, and on targets
  tested mostly that way the floor exception would become the rule. Rejected.
- **Integration tests list everything they use.** Lists that change with every extract. Rejected.
- **The floor never goes down; the Stage waits until it holds.** It would wait for good on weakly tested targets,
  where it helps most. Rejected.
- **`requireCoverageContribution` (PHPUnit 13.2) as a third Stage**: a test that contributes nothing to coverage is
  risky. Left for later.

## Consequences

- A target with the coverage floor is proposed the two Stages in Guardrails. A ticket or rejection on record for the
  Tool's old slug now names the Stage `coverage-floor`, which both new Stages require, so it closes them as before.
- After an extract under the strict Stage, the old tests list the new class as used; `coverage-floor.md` says this is
  the metadata following the code, not a weaker check.
- Infection judges a mutant only by the tests that cover its line, so its score can drop with the first Stage.
