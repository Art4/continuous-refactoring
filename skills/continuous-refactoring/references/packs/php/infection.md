# Infection

The Tool for the Role Mutation Testing in the PHP Pack, proposed only on request: it runs the test suite
hundreds of times, and it pays off only once the tests are worth judging. Infection is no test framework of
its own; it drives the target's — PHPUnit, Pest, PhpSpec or Codeception — through an adapter, and needs a
coverage driver.

**Why this order.** A Guardrails Stage. It requires the Role Testing, filled by PHPUnit or Pest (the `phpunit`
Stage recognizes Pest), not the Stage `phpunit` by name. It waits until the Test Coverage Floor is decided:
that Stage wires the coverage driver Infection needs, and a mutation score over code no test reaches says
nothing new. A target that runs Pest's own mutation testing has the Role filled, and Infection is out
(`pest-mutate.md`).

### `infection`

- **Purpose:** judge the tests by the faults they catch, not by the lines they reach. Infection changes the
  code one small fault at a time — `>` to `>=`, `true` to `false`, a removed call — and runs the tests that
  reach that line; a fault no test notices *escaped*. Once fulfilled, the search for structural candidates
  reads the escaped faults per file for the Untested / hard-to-test signal (`../../signals.md`): a place whose
  tests run its code but catch none of the faults planted there.
- **Fulfilment check:** `infection/infection` is a dev dependency, or its PHAR is committed or fetched by the
  CI job; an Infection config (`infection.json5`, `infection.json5.dist`, `infection.json` or
  `infection.json.dist`) is committed with a minimum score; and once `ci-runner` is fulfilled, a CI job
  invokes Infection. With no CI yet, a local run that meets the minimum fulfils it.
- **MR scope:** the dependency, the config with `testFramework` set to the target's framework (`pest` on a
  Pest project) and a log the search can read back (`logs.json` or `logs.text`), and a CI job limited to the
  changed code: `--git-diff-filter=AM` against the default branch, `--threads` as the runner allows, the
  coverage driver the coverage floor uses. One full local run sets the minimum (below); the merge request
  states the score it measured.
- **Ratchet:** `minMsi` and `minCoveredMsi` in the config start at what the first full run measures and only
  rise, through an ordinary reviewed commit, as `.coverage-floor` does (`coverage-floor.md`).
- **Housekeeping:** run Infection over the whole code; where both scores lie above the minimum, raise it to
  them. The CI job sees only the changed files; this run is what keeps the whole log current for the search.
