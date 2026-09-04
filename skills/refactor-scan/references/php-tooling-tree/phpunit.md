# `phpunit`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** PHPUnit
- **Tool:** PHPUnit
- **Purpose:** the project's test runner.
- **Fulfilment check:** dev dependency installed and runnable (`phpunit` exits green on existing tests); an equivalent already present (Pest) fulfils the node. Test-directory layout (below) is not part of this check — a project can be fulfilled with only some of the folders in use. Once `ci-runner` is fulfilled, the node additionally requires a CI job that actually invokes the runner (`vendor/bin/phpunit`, or `vendor/bin/pest` when Pest is the adopted equivalent) — self-wired CI gate; no separate CI-job node. No CI yet still fulfils the node on local adoption alone.
- **Security advisories:** a known CVE in the only PHP-version-compatible PHPUnit line does not block adoption — see `php-tooling-tree.md`'s `require-dev` security advisories.
- **MR scope:** dependency + minimal config; no test rewrites. Also: if `tests/README.md` doesn't exist yet, create it (*Test layout* below) documenting the full seven-folder convention regardless of what's used yet, but scaffold — as folders, `phpunit.xml.dist` testsuites, and `composer.json` `autoload-dev` entries — only whichever folders are actually relevant to what's in the target repo right now. An empty, never-populated testsuite is noise, not structure. If `tests/README.md` already exists (a prior pass, or a human, wrote it), leave it as-is — this node's own adoption never overwrites it. If `ci-runner` is already fulfilled when this MR lands, it also wires the runner into CI as a gate.

## Test layout

The convention `tests/README.md` documents — a human may adapt it for the target repo, and once they have, their version is the one to follow. Every later pass that writes a test (this node's own first smoke test, or any structural candidate's) reads `tests/README.md` fresh to decide where a new test file belongs; never assume the table below still matches what's actually written there.

| Folder | For |
|---|---|
| `tests/Unit/` | Classes following PSR-4 |
| `tests/Legacy/` | Functions, classes, or code under test that doesn't follow PSR-4 |
| `tests/Psr0/` | Code under test that follows PSR-0 |
| `tests/Integration/` | Real collaborators together (database, filesystem, multiple units) — no test doubles |
| `tests/Functional/` | End-to-end, through the application's real entry points |
| `tests/Fakes/` | Test doubles (fakes, stubs, mocks) — support code, not test cases themselves |
| `tests/Fixtures/` | Static test data (sample files, seed data) — support code, not test cases themselves |

`Fakes/` and `Fixtures/` never get their own `phpunit.xml.dist` testsuite — nothing in them is a test case, so PHPUnit has nothing to run there.

`autoload-dev` in `composer.json`, one entry per folder actually in use: PSR-4 for `tests/Unit/`, `psr-0` for `tests/Psr0/`, `classmap` for `tests/Legacy/` (it isn't autoload-mappable by definition — that's exactly why it's not in `Unit/`). `tests/Unit/`'s namespace prefix: the `psr-4` node (`psr-4.md`) is fulfilled → derive it from that node's own declared app-source root namespace (e.g. root namespace `Art4\LegacyTodo\` → `Art4\LegacyTodo\Tests\Unit\`) — one source of truth for the target's namespace, not two that could drift apart. `psr-4` isn't fulfilled yet → fall back to deriving the prefix independently from `composer.json`'s own `name` field (e.g. `art4/legacy-todo` → `Art4\LegacyTodo\Tests\Unit\`), same as before this node existed.

## Creating or growing `tests/README.md`

- **Missing entirely:** create it (any pass, not just this node's own adoption — e.g. a PHPUnit adoption that predates this convention leaves a target without one). Content: the table above, in full, plus a one-line note that a folder only gets created once something actually needs it.
- **Exists:** never regenerated or overwritten by a pass — read it fresh each time instead. A folder the file documents but that doesn't exist yet on disk gets created (with its `phpunit.xml.dist` testsuite and `autoload-dev` entry, per the rules above) the first time a test actually needs it — one folder at a time, not a bulk sync.
