# PHPUnit

The recommended Tool for the Role Testing in the PHP Pack. It has a minimum runtime of PHP 5.3 (`pack.json`). Test Coverage Floor (`coverage-floor.md`) builds on it.

**Security advisories.** A known security advisory in a `require-dev` package never blocks the package's adoption (`README.md`, *`require-dev` security advisories*); a known advisory in the only PHP-compatible PHPUnit line does not block this Stage.

### `phpunit`

- **Purpose:** the project's test runner.
- **Fulfilment check:** the dev dependency is installed and runnable (`phpunit` exits green on the existing tests); an equivalent already present (Pest) fulfils the Stage. The test-directory layout below is not part of this check: a project can be fulfilled with only some of the folders in use. Once `ci-runner` is fulfilled, the Stage additionally needs a CI job that invokes the runner (`vendor/bin/phpunit`, or `vendor/bin/pest` when Pest is the adopted equivalent): a self-wired CI gate, with no separate Stage for the job. With no CI yet, local adoption alone still fulfils it.
- **MR scope:** the dependency and a minimal config; no test rewrites. If `tests/README.md` does not exist yet, create it (*Test layout* below) documenting the full seven-folder convention regardless of what is used yet, but scaffold only the folders, `phpunit.xml.dist` testsuites and `composer.json` `autoload-dev` entries that are relevant to what is in the target repo right now: an empty, never-populated testsuite is noise, not structure. If `tests/README.md` already exists, leave it as it is; adopting the Stage never overwrites it. If `ci-runner` is already fulfilled when this merge request lands, it also wires the runner into CI as a gate.

## Test layout

The convention `tests/README.md` documents. A human may adapt it for the target repo, and once they have, their version is the one to follow. Every later run that writes a test reads `tests/README.md` fresh to decide where a new test file belongs; never assume the table below still matches what is written there.

| Folder | For |
|---|---|
| `tests/Unit/` | Classes following PSR-4 |
| `tests/Legacy/` | Functions, classes, or code under test that doesn't follow PSR-4 |
| `tests/Psr0/` | Code under test that follows PSR-0 |
| `tests/Integration/` | Real collaborators together (database, filesystem, multiple units), no test doubles |
| `tests/Functional/` | End-to-end, through the application's real entry points |
| `tests/Fakes/` | Test doubles (fakes, stubs, mocks): support code, not test cases themselves |
| `tests/Fixtures/` | Static test data (sample files, seed data): support code, not test cases themselves |

`Fakes/` and `Fixtures/` never get their own `phpunit.xml.dist` testsuite: nothing in them is a test case, so PHPUnit has nothing to run there.

`autoload-dev` in `composer.json`, one entry per folder actually in use: PSR-4 for `tests/Unit/`, `psr-0` for `tests/Psr0/`, `classmap` for `tests/Legacy/` (it is not autoload-mappable by definition, which is why it is not in `Unit/`). The namespace prefix of `tests/Unit/`: when the Stage `psr-4` (`psr-4.md`) is fulfilled, derive it from the app-source root namespace it declares (root namespace `Art4\LegacyTodo\` gives `Art4\LegacyTodo\Tests\Unit\`), so the target's namespace has one source. When `psr-4` is not fulfilled yet, derive the prefix from `composer.json`'s own `name` field (`art4/legacy-todo` gives `Art4\LegacyTodo\Tests\Unit\`).

## Creating or growing `tests/README.md`

- **Missing entirely:** create it, in any run, not just this Stage's own adoption; a PHPUnit adoption that predates this convention leaves a target without one. Content: the table above in full, plus a one-line note that a folder only gets created once something needs it.
- **Exists:** never regenerated or overwritten by a run; read it fresh each time. A folder the file documents but that does not exist on disk yet is created (with its `phpunit.xml.dist` testsuite and `autoload-dev` entry, per the rules above) the first time a test needs it, one folder at a time, not as a bulk sync.
