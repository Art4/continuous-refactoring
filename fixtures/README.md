# Continuous Refactoring — Test Fixtures

Test fixture repositories for validating the continuous-refactoring skill suite. Each fixture is a self-contained PHP project that represents a specific state on the tooling tree.

## Structure

```
continuous-refactoring/
├── fixtures/
│   └── php/
│       └── php-empty/                  # example fixture (all follow same shape)
│           ├── project/                # Input — what is mounted/copied to /tmp (no expected here)
│           │   ├── src/                # PHP source files
│           │   ├── composer.json       # Composer configuration (or .github, phpstan.neon, psalm.xml …)
│           │   └── ...
│           └── expected/               # Expected results — stays outside container, sibling to project/
│               ├── roadmap.json        # Next 10 MRs (tooling + structural, required/recommended)
│               ├── issues/             # Expected refactor:candidate issues
│               └── docs/refactoring/   # Expected loop state files (for php-project-with-candidates)
└── scripts/
    └── run-test.sh                     # Test automation script
```

> **Isolation:** `fixtures/harness/run.sh: setup_fixture` copies only `project/` to `/tmp/continuous-refactoring-tests/<fixture>` (`cp -r project/. DST/`). `expected/` is **not** mounted into Docker / not copied — it lives at `fixtures/php/<fixture>/expected/` and is compared on the host via `python3 scripts/lib/tooling_tree.py`. This prevents the code under test from reading the expected results.

## Available Fixtures

### php-project-with-candidates

A PHP 8.1+ project with planted refactoring candidates. Represents a project where no tooling-tree nodes are fulfilled yet — everything is a structural candidate.

### php-empty

Git-only, no `composer.json`. First MR is `composer` + `ci-runner`. Tests the `git → composer` required edge.

### php-partial

`composer.json` + `composer.lock` with `phpunit` and `php-cs-fixer`, no PHPStan. Tests `composer → phpunit/coposer-audit/p0` unblocked; `p0` is next.

### php-p0-empty

`composer` + `php-cs-fixer` + `phpunit` + CI (` .github/workflows/ci.yml`) + `phpstan.neon` level 0 with empty baseline (`ignoreErrors: []`). Tests `p0` fulfilled empty → `p1` is next; also `rector-*` with `p0` required and `cs-fixer`/`p3` recommended outlook.

### php-p0-nonempty

Same as `php-p0-empty` but baseline has 3 `ignoreErrors` (non-empty). Tests **shrink vs raise** gate: `p1` blocked, loop proposes `rector-*` / structural shrink before next level; `phpstan-level-3` recommended outlook on `rector-type-coverage`.

### php-psalm

`composer` with `vimeo/psalm` + `psalm.xml`, no PHPStan. Tests **Psalm equivalence** — `vimeo/psalm` fulfils `phpstan-level-0-baseline`, level chain `p1..3` is not proposable, `rector-*` still via `p0`.

### Roadmap (dry-run, no MR)

Each fixture above has `expected/roadmap.json` — the next 10 MRs the deterministic parser `scripts/lib/tooling_tree.py` predicts (tool → fulfilment, required/recommended edges, empty-baseline gate, Psalm equivalence). Verified by:

```bash
./fixtures/harness/run.sh roadmap php-empty --verbose          # single fixture (deterministic, no LLM)
./fixtures/harness/run.sh roadmap php-p0-nonempty
# all fixtures (also in CI: roadmap matrix)
for f in php-empty php-partial php-p0-empty php-p0-nonempty php-psalm php-project-with-candidates; do
  ./fixtures/harness/run.sh roadmap $f
done
```
Checks: which tools are recognized (`detected` fulfilled), whether decisions follow `docs/php-tooling-tree.md`, correct 10-step order, recommended-edge outlook (`would benefit from …`), and **no MR/branch created** (still 1 commit, no `docs/refactoring/merge-requests.md` or `.scratch`).

**Local with opencode (isolated, advisory):**

The roadmap tier runs in CI **without LLM** (only Python, `pip install pyyaml`). Locally you can additionally start `opencode` as an isolated subprocess — without global skills, only `skills/` from this repo, as a comparison (non-blocking):

```bash
# deterministic + opencode comparison (needs `opencode` binary via npm i -g opencode or npx)
./fixtures/harness/run.sh roadmap php-empty --opencode --verbose
./fixtures/harness/run.sh roadmap php-p0-nonempty --opencode
```

*What `--opencode` does:* `run.sh:roadmap` creates a `.agents/skills → skills/` symlink in the fixture, runs `timeout 60 opencode run "List the next 10 MRs without creating branches/MRs. Use docs/php-tooling-tree.md."` inside the fixture directory (subprocess, only `skills/` from this repo, no `~/.config/opencode/skills`), logs the first 80 lines to `/tmp/opencode-$FIXTURE.log` and advisory-checks whether the first expected node is mentioned. If the binary is missing, it only logs `opencode binary not found — skipping` (no fail). In CI `--opencode` stays **off** — deterministic is the gate, opencode is only local to observe whether the skill interprets the tree the same way.

### Reproducible local opencode test (for humans and agents)

Prerequisites — one-time setup:

```bash
# 1. Python + deps (for deterministic gate)
python3 --version  # ≥3.11
pip install pyyaml

# 2. opencode CLI (provides `opencode` binary)
npm i -g opencode              # or: pnpm add -g opencode / bun add -g opencode
opencode --help | head -n 5
# alternative without global install: npx --yes opencode --help

# 3. Model opencode/muse-spark-1.2-contributor-free (used in this repo)
opencode models | grep -i "muse-spark"   # should list muse-spark-1.2-contributor-free
# If not authenticated: opencode auth  (or set OPENCODE_API_KEY / provider credentials)
opencode run -m opencode/muse-spark-1.2-contributor-free --help | head -n 5
```

Run deterministic gate (always, no LLM, fast):

```bash
# single fixture
./fixtures/harness/run.sh roadmap php-empty --verbose
# all 6 fixtures (same as CI roadmap matrix)
for f in php-empty php-partial php-p0-empty php-p0-nonempty php-psalm php-project-with-candidates; do
  ./fixtures/harness/run.sh roadmap $f
done
# expected: 6× PASS — Detected nodes match, Roadmap order matches, No MR created
```

Run with opencode (isolated, advisory — requires model, ~60s per fixture):

```bash
# single fixture with opencode comparison (deterministic + LLM)
./fixtures/harness/run.sh roadmap php-empty --opencode --verbose
# all 5 new fixtures (opencode advisory)
for f in php-empty php-partial php-p0-empty php-p0-nonempty php-psalm; do
  ./fixtures/harness/run.sh roadmap $f --opencode
done
```

Direct opencode call (what `run.sh --opencode` does internally; useful for agents via subprocess):

```bash
# 1. Prepare fixture copy exactly like the harness (git init)
FIXTURE=php-p0-nonempty
SRC=fixtures/php/$FIXTURE
DST=/tmp/continuous-refactoring-tests/$FIXTURE
rm -rf $DST && mkdir -p $(dirname $DST) && cp -r $SRC $DST
(cd $DST && git init -q && git -c user.name="Test" -c user.email="test@test" add -A && git commit -q -m "init")

# 2a. Run from repo root so opencode finds docs/php-tooling-tree.md (needs --auto to allow reading /tmp fixture)
opencode run -m opencode/muse-spark-1.2-contributor-free --auto \
  --dir /home/artur/projects/continuous-refactoring \
  "For fixture at /tmp/continuous-refactoring-tests/$FIXTURE (copied from fixtures/php/$FIXTURE), show which tools are recognized per docs/php-tooling-tree.md, whether decisions are correct, and list the next 10 MRs in order without creating branches/MRs. Use deterministic tree: required edge gates, recommended only outlook, empty-baseline absent OR empty ignoreErrors, psalm fulfils p0."

# 2b. Alternative: run inside fixture with skills symlink (exactly what run.sh does)
mkdir -p $DST/.agents && ln -sfn /home/artur/projects/continuous-refactoring/skills $DST/.agents/skills
timeout 60 opencode run -m opencode/muse-spark-1.2-contributor-free --auto --dir $DST \
  "List the next 10 MRs for this repo without creating branches/MRs. Use docs/php-tooling-tree.md." 2>&1 | head -n 80
# log: /tmp/opencode-$FIXTURE.log
```

What to expect:

* **Deterministic:** `Detected tools (fulfilled):` (e.g., `php-psalm: psalm fulfils p0`) + `Next 10 MRs` table + `✓ PASS: No MR created — still 1 commit` + `✓ PASS: Roadmap order matches`.
* **With `--opencode`:** same deterministic output **plus** `=== Opencode isolated (advisory) ===` → `Opencode output (first 80 lines)` + `✓ PASS: Opencode (advisory) mentions expected first node: composer` (or `composer-audit`/`p1` depending on fixture). If model not reachable: `Opencode run failed or timed out — see /tmp/opencode-*.log (advisory, not failing test)` — harness still PASS.
* **Logs:** deterministic JSON at `/tmp/roadmap-$FIXTURE.json`, opencode log at `/tmp/opencode-$FIXTURE.log`.

For agents (subprocess):

```python
import subprocess, pathlib
fixture = "php-p0-nonempty"
subprocess.run(["./fixtures/harness/run.sh", "roadmap", fixture, "--opencode", "--verbose"], check=False)
# or direct deterministic check:
import json; from scripts.lib.tooling_tree import detect_and_roadmap
data = detect_and_roadmap(pathlib.Path(f"fixtures/php/{fixture}"), steps=10)
assert data["roadmap"][0]["node"] == "composer-audit"  # etc.
```

Troubleshooting:

* `opencode binary not found` → `npm i -g opencode` or use `npx --yes opencode`.
* `permission requested: external_directory … auto-rejecting` → add `--auto` (the harness does this).
* `File not found: docs/php-tooling-tree.md` when `--dir /tmp/...` → run with `--dir` pointing to repo root and mention fixture path in prompt, or use the `.agents/skills` symlink method.
* Long runtime → harness uses `timeout 60`; increase if model is slow.

### Agent loop test (full pass, subagent-observed)

Formalizes the manual dry-run methodology that validated ADR-0010 (see [ADR-0010](../docs/adr/0010-orchestrator-explicit-data-flow.md) `## Validation`) so it can be repeated against this repo's own fixtures instead of an ad-hoc scratch copy of some other project. Where `roadmap --opencode` drives only `refactor-scan`'s proposal step via `opencode` in Docker, this drives the **full 6-step orchestrator pass** (`skills/continuous-refactoring/SKILL.md`: scan → learn → prioritise → design → implement → learn) via a Claude Code **Agent-tool subagent** — the tool a Claude Code session itself has, not a subprocess this script can launch. So `run.sh agent-loop` only prepares; running the subagent is a manual step, same as `--opencode` staying local-only and out of CI.

```bash
./fixtures/harness/run.sh agent-loop php-partial
```

What it does:

1. Reuses `setup_fixture` — isolated copy at `/tmp/continuous-refactoring-tests/<fixture>`, fresh git repo, no remote (safe to commit/branch inside freely).
2. Seeds a local-markdown issue-tracker override (`docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, `.scratch/refactor/issues/`, a minimal `CONTEXT.md`, `docs/adr/`) — the same convention this repo uses for itself — so the skills never touch a real forge.
3. Writes a ready-to-use prompt to `/tmp/continuous-refactoring-tests/agent-loop-prompt-<fixture>.md`: read `skills/continuous-refactoring/SKILL.md` and follow it literally, one pass, note (don't silently fix) ambiguity, write friction notes to `agent-loop-friction-<fixture>.md`.
4. Prints the sandbox and prompt paths and stops — spawn the subagent yourself (Agent tool, `run_in_background: false`, prompt = the file's contents) and let it run.

Afterwards, inspect the sandbox to see what happened: `git -C /tmp/continuous-refactoring-tests/<fixture> log`, `docs/refactoring/config.md` / `merge-requests.md`, `.scratch/refactor/issues/`, and the friction file. An optional advisory sanity check (not a hard gate — subagent output isn't deterministic):

```bash
source fixtures/harness/lib/assertions.sh
assert_config_format "/tmp/continuous-refactoring-tests/<fixture>/docs/refactoring/config.md"
assert_git_has_new_commits "/tmp/continuous-refactoring-tests/<fixture>" 2   # 2 = after setup_fixture's init + tracker-seed commits
```

`php-partial` is a good default target — no `docs/refactoring/config.md` yet, so a pass exercises the `loop-config` bootstrap exception before reasoning about `composer`'s children. Any fixture name works; nothing here depends on `php-partial` specifically.

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

1. Copy the fixture's `project/` to a temporary location (only `project/`, not `expected/`):
   ```bash
   cp -r fixtures/php/php-project-with-candidates/project /tmp/test-fixture
   # or for a new fixture: cp -r fixtures/php/php-empty/project /tmp/test-fixture
   ```

2. Initialize git (required for some scan operations):
   ```bash
   cd /tmp/test-fixture
   git init && git add -A && git commit -m "Initial fixture state"
   ```

3. Run the continuous-refactoring scan against the fixture

4. Compare results with `fixtures/php/<fixture>/expected/` (sibling to `project/`, not inside `/tmp`)

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

1. Create a new directory under `fixtures/php/` (or appropriate language), e.g., `fixtures/php/my-fixture/`
2. Create `project/` with the input that gets mounted/copied to `/tmp` — e.g., `project/src/` with planted candidates, `project/composer.json` + `project/composer.lock`, `project/phpstan.neon`, `project/.php-cs-fixer.php`, `project/.github/workflows/ci.yml`, etc.
3. Create `expected/` as sibling to `project/` — e.g., `expected/roadmap.json` (next 10 MRs), `expected/issues/` with `refactor:candidate` issues, `expected/docs/refactoring/` — **never inside `project/`** (so it is not mounted into Docker / not visible to the code under test)
4. Document the fixture's purpose and tooling-tree state in this README (see `php-empty` … `php-psalm` examples above)

## Design Principles

- **Self-contained:** Each fixture is an independent project, not a submodule
- **Deterministic:** Fixtures produce the same scan results every run
- **Resettable:** Fixtures can be restored to their original state via git
- **Documented:** Expected outcomes are explicit in `expected/`
