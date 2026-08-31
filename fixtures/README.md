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

> **Isolation:** `fixtures/harness/run.sh: setup_fixture` copies only `project/` to `/tmp/continuous-refactoring-tests/<fixture>` (`cp -r project/. DST/`). `expected/` is **not** mounted into Docker / not copied — it lives at `fixtures/php/<fixture>/expected/` and is compared on the host via `python3 skills/refactor-scan/references/tooling_tree.py`. This prevents the code under test from reading the expected results.

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

`composer` with `vimeo/psalm` + `psalm.xml`, no PHPStan. Tests **Psalm equivalence** — `vimeo/psalm` fulfils `phpstan-level-0` (via the `psalm` node, ticket 43), level chain `p1..10` is not proposable, `rector-*` (including the `rector-php-set`-gated family) still via `p0` equivalence — this equivalence is deliberately *not* touched by ticket 37's mutual exclusion (see `php-tooling-tree.md`'s `phpstan` equivalents section). Also carries `docs/refactoring/out-of-scope/phpstan-level-10.md` (ticket 37): the mutual-exclusion housekeeping that resolves `phpstan-level-10` — the PHPStan level chain's `php-structural-scan` leaf — as rejected, since a Psalm-only target never fulfils it. Without that entry `phpstan-level-10` stays neither fulfilled nor rejected and `php-structural-scan`/`structural-scan` stay permanently blocked; this fixture demonstrates the fixed steady state. `psalm` is not itself a `php-structural-scan` leaf (ticket 37 tried that and dropped it as redundant — see `php-tooling-tree.md`'s `psalm` node entry). `psalm-taint-analysis` (ticket 44, a `php-structural-scan` leaf) reads fulfilled here incidentally — the same `vimeo/psalm` dependency and `psalm.xml` satisfy both nodes' detection, and there's no CI here to gate the taint-specific check on.

### php-clean

Every deterministic PHP-tooling-tree leaf resolved: `composer`, `ci-runner`, `php-cs-fixer`, `phpunit` (CI-gated), `composer-audit` (CI-gated, real dependency), `phpstan-level-0` (level 0, empty baseline — this target's declared ceiling), `rector-dead-code`/`rector-type-coverage`/`rector-php-set`/`rector-code-quality`/`rector-phpunit-set`/`rector-early-return` fully adopted (ticket 43's Rector set family — `rector-dead-code`/`rector-code-quality`/`rector-early-return` gated by `rector-php-set` directly, `rector-type-coverage`/`rector-phpunit-set` gated via sibling recommended edges instead, per a later restructuring). Levels 1–10 plus `phpstan-deprecation-rules` are explicitly rejected under `docs/refactoring/out-of-scope/` rather than climbed — climbing them would flip `phpstan-level-0` back to unfulfilled (it only recognizes level *exactly* 0) while `php-structural-scan`'s `resolved` gate only cares about `phpstan-level-10` (ticket 43; was `phpstan-level-3`), so an honest "nothing tooling-side left to propose" state needs the reject path, not the climb (see `docs/refactoring/out-of-scope/phpstan-level-{1..10}.md` and `phpstan-deprecation-rules.md` for the reasoning). Also carries `docs/refactoring/out-of-scope/psalm-taint-analysis.md` (ticket 44): `psalm-taint-analysis` is a `php-structural-scan` leaf too (a deterministic security-scan tool, same gating reasoning as `composer-audit`) and this target never adopted it. `psalm` itself needs no rejection here — it's not a `php-structural-scan` leaf (ticket 37 tried that and dropped it as redundant ceremony). Tests **"scan on clean repo reports clean"** (ticket 27's deterministic Tier 4 negative control) — `next()` holds nothing but the perpetual `structural-scan` invitation, `withheld()` is empty. `expected/roadmap.json`'s 10-step *simulation* still falls back to the open `phpstan-level-11..20` chain (ticket 43: was `4..13`) rather than proposing `structural-scan` — a real gap in `roadmap()`'s simulation loop (it doesn't special-case an already-open `structural-scan` gate the way `next_candidates()` does), tracked separately; **use `next`, not `roadmap`, for this fixture's real signal**, exactly as `refactor-scan`'s own `SKILL.md` already warns.

### Tier 4 — Trigger & Discoverability tests (ticket 27)

Ticket 27's three negative controls split across two layers:

- **Deterministic** (`scripts/test_trigger_controls.py`, CI-gated via the `tier4` job): "scan on clean repo reports clean" is a real, fully-testable property of the deterministic parser — see `php-clean` above. The other two controls are prose-level judgment calls a skill makes, for two distinct reasons: "no git" is `refactor-scan`'s own step-1 precondition — `detect_nodes()` already reports a missing `.git` accurately, but whether that precondition is actually *followed* is a model-behavior question, not something the parser decides; "not a PHP project" is ADR-0008's deliberate carve-out, which keeps language recognition an informal heuristic on purpose ("premature before a second language specialization exists"). Either way, this module only checks the ground-truth *signal* each judgment reads (`detect_nodes()` reports `git`/`composer` accurately), not the judgment itself.
- **Behavioral** (`fixtures/harness/run.sh tier4 <fixture> --opencode`, local-only advisory, same non-CI posture as `roadmap --opencode` and `agent-loop`): runs all three negative controls end-to-end via opencode, plus **explicit + implicit invocation per skill** — for each of the five lifecycle skills, both `/skill-name` and a natural-language paraphrase of its `description` should trigger it; for the orchestrator (`continuous-refactoring`, which ships `disable-model-invocation: true`), only the explicit form should.

```bash
./fixtures/harness/run.sh tier4 php-clean --opencode --verbose
```

Without `--opencode` it just points at the deterministic test module and exits — same degrade-gracefully shape as `roadmap --opencode` when the binary is missing.

### Roadmap (dry-run, no MR)

Each fixture above has `expected/roadmap.json` — the next 10 MRs the deterministic parser `skills/refactor-scan/references/tooling_tree.py` predicts (tool → fulfilment, required/recommended edges, empty-baseline gate, Psalm equivalence). Verified by:

```bash
./fixtures/harness/run.sh roadmap php-empty --verbose          # single fixture (deterministic, no LLM)
./fixtures/harness/run.sh roadmap php-p0-nonempty
# all fixtures (also in CI: roadmap matrix)
for f in php-empty php-partial php-p0-empty php-p0-nonempty php-psalm php-clean php-project-with-candidates; do
  ./fixtures/harness/run.sh roadmap $f
done
```
Checks: which tools are recognized (`detected` fulfilled), whether decisions follow `skills/refactor-scan/references/php-tooling-tree.md`, correct 10-step order, recommended-edge outlook (`would benefit from …`), and **no MR/branch created** (still 1 commit, no `docs/refactoring/merge-requests.md` or `.scratch`).

**Local with opencode (isolated, advisory):**

The roadmap tier runs in CI **without LLM** (only Python, `pip install pyyaml`). Locally you can additionally start `opencode` as an isolated subprocess — without global skills, only `skills/` from this repo, as a comparison (non-blocking):

```bash
# deterministic + opencode comparison (needs `opencode` binary via npm i -g opencode or npx)
./fixtures/harness/run.sh roadmap php-empty --opencode --verbose
./fixtures/harness/run.sh roadmap php-p0-nonempty --opencode
```

*What `--opencode` does:* `run.sh:roadmap` creates a `.agents/skills → skills/` symlink in the fixture, runs `timeout 60 opencode run "List the next 10 MRs without creating branches/MRs. Use skills/refactor-scan/references/php-tooling-tree.md."` inside the fixture directory (subprocess, only `skills/` from this repo, no `~/.config/opencode/skills`), logs the first 80 lines to `/tmp/opencode-$FIXTURE.log` and advisory-checks whether the first expected node is mentioned. If the binary is missing, it only logs `opencode binary not found — skipping` (no fail). In CI `--opencode` stays **off** — deterministic is the gate, opencode is only local to observe whether the skill interprets the tree the same way.

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
for f in php-empty php-partial php-p0-empty php-p0-nonempty php-psalm php-clean php-project-with-candidates; do
  ./fixtures/harness/run.sh roadmap $f
done
# expected: 6× PASS — Detected nodes match, Roadmap order matches, No MR created
```

Run with opencode (isolated, advisory — requires model, ~60s per fixture):

```bash
# single fixture with opencode comparison (deterministic + LLM)
./fixtures/harness/run.sh roadmap php-empty --opencode --verbose
# all 5 new fixtures (opencode advisory)
for f in php-empty php-partial php-p0-empty php-p0-nonempty php-psalm php-clean; do
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

# 2a. Run from repo root so opencode finds skills/refactor-scan/references/php-tooling-tree.md (needs --auto to allow reading /tmp fixture)
opencode run -m opencode/muse-spark-1.2-contributor-free --auto \
  --dir /home/artur/projects/continuous-refactoring \
  "For fixture at /tmp/continuous-refactoring-tests/$FIXTURE (copied from fixtures/php/$FIXTURE), show which tools are recognized per skills/refactor-scan/references/php-tooling-tree.md, whether decisions are correct, and list the next 10 MRs in order without creating branches/MRs. Use deterministic tree: required edge gates, recommended only outlook, empty-baseline absent OR empty ignoreErrors, psalm fulfils p0."

# 2b. Alternative: run inside fixture with skills symlink (exactly what run.sh does)
mkdir -p $DST/.agents && ln -sfn /home/artur/projects/continuous-refactoring/skills $DST/.agents/skills
timeout 60 opencode run -m opencode/muse-spark-1.2-contributor-free --auto --dir $DST \
  "List the next 10 MRs for this repo without creating branches/MRs. Use skills/refactor-scan/references/php-tooling-tree.md." 2>&1 | head -n 80
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
# or direct deterministic check — importlib, not a dotted import: "refactor-scan"'s
# hyphen makes `skills.refactor_scan...` an invalid package path
import importlib.util, json, pathlib
spec = importlib.util.spec_from_file_location("tooling_tree", "skills/refactor-scan/references/tooling_tree.py")
tooling_tree = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tooling_tree)
data = tooling_tree.detect_and_roadmap(pathlib.Path(f"fixtures/php/{fixture}"), steps=10)
assert data["roadmap"][0]["node"] == "composer-audit"  # etc.
```

Troubleshooting:

* `opencode binary not found` → `npm i -g opencode` or use `npx --yes opencode`.
* `permission requested: external_directory … auto-rejecting` → add `--auto` (the harness does this).
* `File not found: skills/refactor-scan/references/php-tooling-tree.md` when `--dir /tmp/...` → run with `--dir` pointing to repo root and mention fixture path in prompt, or use the `.agents/skills` symlink method.
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

### Tier 5 — CI gate, rubric grading, lift measurement (ticket 27)

**Regression-baseline CI gate:** Tier 3's precision/recall baselines live at `fixtures/baselines/` — gitignored ("generated, not committed"), so the CI `tier3` job restores/saves them via `actions/cache` (`.github/workflows/test-harness.yml`) instead. `run_tier3` now compares the freshly-computed recall against whatever baseline the cache restored (`assert_baseline_not_regressed`, `fixtures/harness/lib/assertions.sh`) *before* overwriting it, and fails the job if recall regressed. Caveat worth knowing before you touch this: CI never runs an LLM (see "Roadmap" above), so `found` is always `0` there — the gate is real and will catch a genuine regression the moment a baseline records an actual recall from a local `agent-loop`/`--opencode` run, but inside CI itself today it's comparing `0` against `0` every time. The already-existing `roadmap` matrix (`expected/roadmap.json`, exact match, hard fail on drift) is this harness's other, already-meaningful regression gate — extended to 7 fixtures by `php-clean`.

**LLM-judge rubric grading** (local-only, advisory, non-CI): grades one fixture's post-pass artifacts against `fixtures/harness/rubric.md`'s five dimensions (process fidelity, candidate selection, artifact quality, state hygiene, honesty about ambiguity).

```bash
./fixtures/harness/run.sh judge php-project-with-candidates --opencode
```

**With-skill vs. without-skill lift measurement** (local-only, advisory, non-CI): runs the same prompt twice against the same fixture state — once with `skills/` mounted the way every other `--opencode` check does, once with no skill guidance at all — so the two transcripts can be compared by hand or graded against the rubric above.

```bash
./fixtures/harness/run.sh lift php-partial --opencode
```

Both commands share the same degrade-gracefully behavior as `roadmap --opencode`: no `opencode` binary found → one info line, exit clean, nothing fails.

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
