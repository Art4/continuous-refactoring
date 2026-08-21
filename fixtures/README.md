# Continuous Refactoring — Test Fixtures

Test fixture repositories for validating the continuous-refactoring skill suite. Each fixture is a self-contained PHP project that represents a specific state on the tooling tree.

## Structure

```
continuous-refactoring/
├── fixtures/
│   └── php/
│       └── php-project-with-candidates/
│           ├── src/                    # PHP source files
│           ├── composer/               # Composer configuration
│           └── expected/               # Expected scan results
│               ├── issues/             # Expected refactor:candidate issues
│               └── docs/refactoring/   # Expected loop state files
└── scripts/
    └── run-test.sh                     # Test automation script
```

## Available Fixtures

### php-project-with-candidates

A PHP 8.1+ project with planted refactoring candidates. Represents a project where no tooling-tree nodes are fulfilled yet — everything is a structural candidate.

**Components:**
- `src/UserService.php` — Shallow "god service" mixing authentication, profile management, notifications, and reporting
- `src/UserRepository.php` — Contains SQL injection vulnerability and hardcoded secret
- `src/UnusedReportingService.php` — Dead code (never referenced)
- `src/bootstrap.php` — Missing `declare(strict_types=1)`, uses deprecated `each()` function
- `src/User.php` — Entity class

**Dependencies (composer.json):**
- PHP ^8.1
- doctrine/orm ^2.14
- guzzlehttp/guzzle ^7.8
- monolog/monolog ^3.4
- phpunit/phpunit ^10.2 (dev)

## Expected Issues

The fixture contains five planted candidates that a `refactor-scan` should discover:

| # | File | Candidate | Type |
|---|------|-----------|------|
| 001 | `UserService.php` | Shallow god service | Structural |
| 002 | `UserRepository.php` | SQL injection in `searchByName()` | Security |
| 003 | `UserRepository.php` | Hardcoded API key in comment | Security |
| 004 | `UnusedReportingService.php` | Dead code | Structural |
| 005 | `bootstrap.php` | Missing strict types, deprecated function | Tooling pressure |

## Expected Loop State

After a successful loop pass, the fixture should produce:

- `expected/docs/refactoring/config.md` — Loop configuration (cadence: weekly)
- `expected/docs/refactoring/merge-requests.md` — No open merge requests

## Usage

### Manual Testing

1. Copy the fixture to a temporary location:
   ```bash
   cp -r fixtures/php/php-project-with-candidates /tmp/test-fixture
   ```

2. Initialize git (required for some scan operations):
   ```bash
   cd /tmp/test-fixture
   git init && git add -A && git commit -m "Initial fixture state"
   ```

3. Run the continuous-refactoring scan against the fixture

4. Compare results with `expected/` directory

### Automated Testing

Use the test script (see `scripts/run-test.sh`):

```bash
# Run full test cycle (setup → test → clean)
./scripts/run-test.sh auto php-project-with-candidates

# Or run individual steps
./scripts/run-test.sh setup php-project-with-candidates
./scripts/run-test.sh test php-project-with-candidates
./scripts/run-test.sh clean php-project-with-candidates
```

## Adding New Fixtures

1. Create a new directory under `fixtures/php/` (or appropriate language)
2. Include `src/` with planted candidates
3. Add `expected/` with anticipated scan results
4. Document the fixture's purpose and tooling-tree state in this README

## Design Principles

- **Self-contained:** Each fixture is an independent project, not a submodule
- **Deterministic:** Fixtures produce the same scan results every run
- **Resettable:** Fixtures can be restored to their original state via git
- **Documented:** Expected outcomes are explicit in `expected/`
