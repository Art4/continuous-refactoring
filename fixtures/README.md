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
│               ├── issues/             # Expected refactor:candidate issues
│               └── docs/refactoring/   # Expected loop state files (for php-project-with-candidates)
└── scripts/
    └── run-test.sh                     # Test automation script
```

> **Isolation:** `fixtures/harness/run.sh: setup_fixture` copies only `project/` to `/tmp/continuous-refactoring-tests/<fixture>` (`cp -r project/. DST/`). `expected/` is **not** mounted into Docker / not copied — it lives at `fixtures/php/<fixture>/expected/`, read only by the host-side checks. This prevents the code under test from reading the expected results.

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

`composer` with `vimeo/psalm` + `psalm.xml`, no PHPStan. Tests **Psalm equivalence** — `vimeo/psalm` fulfils `phpstan-level-0` (via the `psalm` node, ticket 43), level chain `p1..10` is not proposable, `rector-*` (including the `rector-php-set`-gated family) still via `p0` equivalence — this equivalence is deliberately *not* touched by ticket 37's mutual exclusion (see `php-tooling-tree.md`'s `phpstan` equivalents section). Also carries `docs/refactoring/out-of-scope/phpstan-level-10.md` (ticket 37): the mutual-exclusion housekeeping that resolves `phpstan-level-10` — the PHPStan level chain's `php-safety-net` leaf (renamed from `php-structural-scan`) — as rejected, since a Psalm-only target never fulfils it. Without that entry `phpstan-level-10` stays neither fulfilled nor rejected and `php-safety-net`/`structural-scan` stay permanently blocked; this fixture demonstrates the fixed steady state. `psalm` is not itself a `php-safety-net` leaf (ticket 37 tried that and dropped it as redundant — see `php-tooling-tree.md`'s `psalm` node entry). `psalm-taint-analysis` (ticket 44, a `php-safety-net` leaf) reads fulfilled here incidentally — the same `vimeo/psalm` dependency and `psalm.xml` satisfy both nodes' detection, and there's no CI here to gate the taint-specific check on.

### php-clean

Every deterministic PHP-tooling-tree node resolved (fulfilled or explicitly rejected): `composer`, `psr-4` (ticket 50: a real `autoload.psr-4` mapping declared and verifiably in use — `src/Greeter.php` under the mapped `App\` namespace), `ci-runner`, `php-cs-fixer`, `phpunit` (CI-gated), `phpstan-level-0` (level 0, empty baseline — this target's declared ceiling), `rector-dead-code`/`rector-type-coverage`/`rector-php-set`/`rector-code-quality`/`rector-phpunit-set` fully adopted (ticket 43's Rector set family — `rector-dead-code`/`rector-code-quality` gated by `rector-php-set` directly, `rector-type-coverage`/`rector-phpunit-set` gated via sibling recommended edges instead, per a later restructuring; ticket 48 later dropped the family's sixth node, `rector-early-return`, folding its scope into `rector-code-quality`). Levels 1–10 plus `phpstan-deprecation-rules` are explicitly rejected under `docs/refactoring/out-of-scope/` rather than climbed — climbing them would flip `phpstan-level-0` back to unfulfilled (it only recognizes level *exactly* 0) while `php-safety-net`'s `resolved` gate only cares about `phpstan-level-10` (ticket 43; was `phpstan-level-3`), so an honest "nothing tooling-side left to propose" state needs the reject path, not the climb (see `docs/refactoring/out-of-scope/phpstan-level-{1..10}.md` and `phpstan-deprecation-rules.md` for the reasoning). Also carries `docs/refactoring/out-of-scope/psalm-taint-analysis.md` (ticket 44): `psalm-taint-analysis` is a `php-safety-net` leaf too (a deterministic security-scan tool) and this target never adopted it. `psalm` itself needs no rejection here — it's not a `php-safety-net` leaf (ticket 37 tried that and dropped it as redundant ceremony). `composer-audit`, `phpmd`, `coverage-floor`, `php-minimal-version`, `phpstan-level-6`, and `semgrep` all moved to (or joined) the **Signal wave**, gated on `php-safety-net` in addition to (or, for `semgrep`, instead of) their own domain-specific parent — this fixture keeps every one of them genuinely fulfilled (CI-gated `composer audit`/Semgrep, `phpmd`/`coverage-floor`/`php-minimal-version` adopted) so the invariant below still holds now that `php-safety-net` resolving makes them all proposable in principle. Tests **"scan on clean repo reports clean"** (ticket 27's deterministic Tier 4 negative control) — `next()` holds nothing but the perpetual `structural-scan` invitation, `withheld()` is empty. This fixture's `project/` also carries the Refactoring Notes' `fulfilled-set.json` seed (every node resolved), so the graph logic reads the same state the tree docs describe.

### non-php-project

A static HTML/CSS/JS site — `index.html`, `styles.css`, `script.js` — no `composer.json`, no `*.php` file
anywhere. Stands in for a target like `continuous-refactoring.de`. Tests **`is-php-project`'s gate**
(`skills/refactor-scan/references/tooling-tree.md`, ADR-0022): `is-php-project` unfulfilled keeps
`composer`/`php-minimal-version` and everything beneath them out of `next` — only `onboarding-setup`
(fulfilled by the dispatcher's onboarding step before any scan in a real pass), `ci-runner`, and
`editorconfig` (all language-neutral) are in the parser's `next`; `next` is the fixture's real signal
for the gate.

### php-decision-gate-bypass

Not a tooling-tree fixture — no deterministic ground truth (local-only, advisory). Two independent retry-with-backoff implementations with genuinely different observable
contracts, plus a pre-seeded `.scratch/refactor/issues/01-unify-retry-logic.md` (Local Markdown
tracker) already carrying `refactor:candidate, ready-for-agent` and claiming to be fully specified.
Exists solely for the Tier 5 **decision-gate bypass regression** below (ADR-0053) — see
`expected/behavior.md` for what a `refactor-design`/`refactor-scan` pass should do with it.

### php-onboarding-* (dispatcher onboarding step)

Not tooling-tree fixtures — no deterministic ground truth (local-only, advisory), exercised through the
`agent-loop` mode below. Three targets that have never run the loop, so `/continuous-refactoring` onboards
them as step 0 of the dispatcher and ends the invocation
(`skills/continuous-refactoring/references/onboarding-setup-interview.md`): `php-onboarding-fresh` (no
engineering-skills setup — the setup-gap question, all three questions, every file written),
`php-onboarding-set-up` (both `docs/agents/` files present — no setup-gap question, no tracker question,
existing files untouched) and `php-onboarding-interrupted` (everything written except `bookkeeping.md` —
resumes without re-asking what is on record). See each fixture's `expected/behavior.md`; the second
invocation, which selects a Track and starts the scan, is what the `php-safety-net-first-run` family
already covers.

### php-safety-net-* (Safety Net Track, ADR-0055)

Not tooling-tree fixtures — no deterministic ground truth (local-only, advisory): the whole point
under test is that a Safety Net Track node's fulfilment is agent-judged against its own Purpose, so
there's no fixed deterministic ground truth to assert `tier2`/`tier3` against here. Each fixture
exercises one checklist item from
`skills/refactor-scan/references/safety-net-track.md` / `skills/refactor-learn/references/
safety-net-write.md`; see each fixture's own `expected/behavior.md` for the full expected behavior.

- **php-safety-net-purpose-recognition** — `laravel/pint` installed and configured, no
  `friendsofphp/php-cs-fixer` anywhere. Expects `php-cs-fixer` judged fulfilled via its own Purpose
  statement (Pint genuinely serves it), and never proposed as a candidate.
- **php-safety-net-open-blocks-rescan** — `docs/refactoring/bookkeeping.md`'s `## Safety Net` section
  holds a non-empty `Open` (`php-cs-fixer (#5)`, already `ready-for-agent` with a plan) and a `Last
  scan` far past the default 90-day `Cadence`. Expects the existing `Open` entry resumed straight to
  `refactor-implement`, not a fresh Track walk proposing the project's other genuinely-missing nodes.
- **php-safety-net-first-run** — every Safety Net Track node already resolved (fulfilled or rejected
  under `out-of-scope/`), no `## Safety Net` section yet (never run). Expects the section created with
  `Last scan` written even though nothing was missing, so the target isn't rescanned every pass.
- **php-safety-net-rejection-symmetry** — `## Safety Net`'s `Open` names `php-cs-fixer (#5)`; the
  candidate's own issue is already closed `wontfix` with a maintainer's load-bearing structural reason.
  Expects it removed from `Open`, `out-of-scope/php-cs-fixer.md` written, and a pointer added under
  `Out-of-scope` — the same merge/rejection symmetry every other rejection in the suite already
  follows.
- **php-safety-net-old-schema** — `docs/refactoring/bookkeeping.md` still in the pre-ADR-0055 shape
  (`Fulfilled nodes`, global `Pending candidates`, no `## Safety Net` section at all), with real
  Safety-Net-Track work still open (`psr-4`, `static-code-analyzer`/`phpstan-level-0` genuinely
  missing). Expects a normal pass — no error on, or migration of, the pre-existing old-shape fields.
- **php-safety-net-rejection-cascade** — `## Safety Net`'s `Open` names `phpstan-level-3 (#12)`,
  `phpstan-level-4`, `phpstan-level-5`; level 3's issue is closed `wontfix` with a structural reason.
  Unlike the rejection fixtures above (`php-cs-fixer` has no required descendants), `phpstan-level-3`
  has required descendants. Expects the rejection recorded once (`out-of-scope/phpstan-level-3.md` plus
  the `Out-of-scope` pointer), `phpstan-level-4`/`-5` leaving `Open` with no files of their own, and —
  once the rejection is reversed by hand — the next scan re-adding `phpstan-level-3`, `-4`, `-5` in
  order (spec case 6; cascade verified with `tooling_tree.py`).
- **php-safety-net-old-meaning-open** — `## Safety Net` still written under the old `Open` meaning
  (`phpstan-level-1 (#7)` as the only list entry, plus `Fulfilled nodes`/`Focus areas` residue),
  `Last scan` recent, and a pass that names the Safety Net Track explicitly. Expects no error, no
  migration, and **no forced scan**: a selected Track with a non-empty `Open` works its `Open` walk
  (`phpstan-level-1`), leaving `Open`/`Last scan` alone; the scan that runs once `Open` is empty records
  the complete backlog. Deviates from the spec's case 10 ("forced rescan via override").

```bash
./fixtures/harness/run.sh safety-net-track php-safety-net-purpose-recognition --opencode
./fixtures/harness/run.sh safety-net-track php-safety-net-open-blocks-rescan --opencode
./fixtures/harness/run.sh safety-net-track php-safety-net-first-run --opencode
./fixtures/harness/run.sh safety-net-track php-safety-net-rejection-symmetry --opencode
./fixtures/harness/run.sh safety-net-track php-safety-net-old-schema --opencode
./fixtures/harness/run.sh safety-net-track php-safety-net-rejection-cascade --opencode
./fixtures/harness/run.sh safety-net-track php-safety-net-old-meaning-open --opencode
```

Same non-CI, local-only, advisory posture as `decision-gate-bypass`/`judge`/`lift` — a real, file-level
grep against the fixture's own post-run `docs/refactoring/bookkeeping.md`/`out-of-scope/` where the
check can be made deterministic that way (mirroring `decision-gate-bypass`'s own label check), an
advisory transcript grep otherwise (LLM output isn't deterministic). Uses `opencode run --auto` for the
same reason `decision-gate-bypass` does — see its own note below.

### php-guardrails-* (Guardrails Track, ADR-0055, ticket 02)

Not tooling-tree fixtures — no deterministic ground truth (local-only, advisory), same reasoning as
`php-safety-net-*` above. The Guardrails Track's own counterpart, reusing the
exact same mechanism (`skills/refactor-scan/references/guardrails-track.md` /
`skills/refactor-learn/references/guardrails-write.md`) against a second node set — the nodes required
on `structural-scan`/`php-safety-net` themselves (PHP: `composer-audit`, `phpmd`, `coverage-floor`,
`php-minimal-version`, `phpstan-level-6` and above, `phpstan-deprecation-rules`, `semgrep`), reachable
only once the Safety Net has closed. Every fixture below seeds the Safety Net already fully closed
(`php-safety-net` resolved), so its own Guardrails nodes are genuinely reachable; see each fixture's
own `expected/behavior.md` for the full expected behavior.

- **php-guardrails-purpose-recognition** — `composer.json` defines a `scripts.security-check` entry
  whose command is literally `composer audit`, invoked from CI as `composer run security-check` — the
  literal substring `composer audit` never appears in any CI workflow file, only inside `composer.json`
  itself, so no literal-text check would ever see it. Expects `composer-audit` judged fulfilled
  via its own Purpose statement (the CI gate is real, just invoked through one level of indirection),
  and never proposed as a candidate.
- **php-guardrails-open-blocks-rescan** — `docs/refactoring/bookkeeping.md`'s `## Guardrails` section
  holds a non-empty `Open` (`phpmd (#5)`, already `ready-for-agent` with a plan) and a `Last scan` far
  past the default 60-day `Cadence`. Expects the existing `Open` entry resumed straight to
  `refactor-implement`, not a fresh Track walk proposing the project's other genuinely-missing
  Guardrails nodes (`composer-audit`, `coverage-floor`, `php-minimal-version`, `phpstan-level-6`,
  `phpstan-deprecation-rules`, `semgrep`).
- **php-guardrails-first-run** — every Guardrails Track node already resolved (fulfilled, or
  effectively rejected via `phpstan-level-1`'s own cascading closure), no `## Guardrails` section yet
  (never run) — the Safety Net is closed the same "declared ceiling level 0" way `php-clean` already
  uses. Expects the section created with `Last scan` written even though nothing was missing, so the
  target isn't rescanned every pass.
- **php-guardrails-rejection-symmetry** — `## Guardrails`'s `Open` names `phpmd (#5)`; the candidate's
  own issue is already closed `wontfix` with a maintainer's load-bearing structural reason (complexity
  enforced purely by PR review, no tool). Expects it removed from `Open`,
  `out-of-scope/phpmd.md` written, and a pointer added under `Out-of-scope` — the same merge/rejection
  symmetry every other rejection in the suite already follows.
- **php-guardrails-old-schema** — deliberately a different scenario from `php-safety-net-old-schema`
  (a target still fully on the pre-ADR-0055 shape never reaches the Guardrails Track in the same pass —
  the Safety Net Track outranks it and is more overdue). This fixture instead seeds a target
  mid-migration: `## Safety Net` already present and closed (ticket 01 has already run on it), but
  `Fulfilled nodes` still carries pre-ADR-0055 residue for nodes the Safety Net Track has since taken
  over (`composer`, `php-cs-fixer`, `phpunit`, `psr-4`, `phpstan-level-0`, the `rector-*` family), and
  no `## Guardrails` section yet. Expects a normal pass — no error on the coexistence, and real,
  still-open Guardrails work (`composer-audit`, `phpmd`, `coverage-floor`, `php-minimal-version`,
  `phpstan-level-6`, `phpstan-deprecation-rules`, `semgrep` are all genuinely missing) recorded as
  `Open` (the complete backlog, in the script's order) rather than filed.
- **php-guardrails-scan-fills-open** — Safety Net closed; `## Guardrails` present, due
  (`overdue_ratio ≈ 1.33`) with an **empty** `Open`; all eleven Guardrails scope nodes missing, four of
  them blocked (`phpstan-level-7..10`). Expects the scan to record `Open` as the complete backlog in
  the script's deterministic order (`phpmd`, `coverage-floor`, `composer-audit`, `phpstan-level-6`
  through `-10`, `phpstan-deprecation-rules`, `php-minimal-version`, `semgrep` — computed with
  `tooling_tree.py` and a seed, not guessed), blocked nodes included, plus `Last scan`, and no
  candidate issue filed (spec case 4).

```bash
./fixtures/harness/run.sh guardrails-track php-guardrails-purpose-recognition --opencode
./fixtures/harness/run.sh guardrails-track php-guardrails-open-blocks-rescan --opencode
./fixtures/harness/run.sh guardrails-track php-guardrails-first-run --opencode
./fixtures/harness/run.sh guardrails-track php-guardrails-rejection-symmetry --opencode
./fixtures/harness/run.sh guardrails-track php-guardrails-old-schema --opencode
./fixtures/harness/run.sh guardrails-track php-guardrails-scan-fills-open --opencode
```

Same non-CI, local-only, advisory posture as `safety-net-track`/`decision-gate-bypass`/`judge`/`lift`.

### php-scheduler-* (Track scheduler, ADR-0055, tickets 04/05)

Not tooling-tree fixtures — no deterministic ground truth (local-only, advisory), same reasoning as
`php-safety-net-*`/`php-guardrails-*` above. Exercises the orchestrator's own new Track-selection step
(`skills/continuous-refactoring/SKILL.md` step 1, algorithm in
`skills/continuous-refactoring/references/track-scheduler.md`) — real competition between every
currently-wired Track, replacing each Track's own earlier standalone "is my Track due?" check. See each
fixture's own `expected/behavior.md` for the full expected behavior.

- **php-scheduler-staleness-selection** — spec Testing Decision #2 ("Track selection under simple
  staleness"). Safety Net closed (`php-safety-net` resolved), both `## Safety Net`
  (`Cadence: 90`, `Last scan: 2026-06-16`, `overdue_ratio ≈ 1.056`) and `## Guardrails`
  (`Cadence: 60`, `Last scan: 2026-04-22`, `overdue_ratio = 2.5`) due, neither holding `Open` work.
  Expects **Guardrails** selected — its ratio is the higher one, even though Safety Net outranks it in
  the fixed tie-break order (Safety Net > Guardrails > Housekeeping > Investigation). The fixed order
  only ever breaks a tie or resolves two "never run" Tracks with no ratio to compare; it must not
  override a genuine, non-tied staleness difference.

```bash
./fixtures/harness/run.sh scheduler php-scheduler-staleness-selection --opencode
```

Same non-CI, local-only, advisory posture as `safety-net-track`/`guardrails-track`. Each Track's own
`Open`-empty eligibility precondition and `Open`-non-empty-blocks-rescan behavior (ticket 04's own
checklist item 2) is unchanged and already covered by `php-safety-net-open-blocks-rescan`/
`php-guardrails-open-blocks-rescan` above — this tier only adds the cross-Track ratio-competition case
those single-Track fixtures couldn't exercise on their own.

- **php-scheduler-investigation-fallback** (ticket 05, Investigation Track wired into the scheduler).
  Same deterministic node inventory as `php-clean` — Safety Net **and** Guardrails both fully resolved —
  but `## Safety Net` (`Cadence: 90`, `Last scan: 2026-09-01`, `overdue_ratio ≈ 0.2`) and `## Guardrails`
  (`Cadence: 60`, `Last scan: 2026-09-10`, `overdue_ratio ≈ 0.15`) are both **not due**; `## Investigation`
  (`Cadence: continuous`) carries no numeric Cadence at all, so it's always due and always eligible.
  Expects **Investigation** selected — the only due-and-eligible Track this pass, winning purely as the
  scheduler's own fallback rather than by out-ranking a real ratio — and `structural-scan` proposed by
  `refactor-scan`'s own `investigation-track.md`, confirming the Track gate this ticket adds (before it,
  `structural-scan` was proposed unconditionally, with no Track selection involved at all).

```bash
./fixtures/harness/run.sh scheduler php-scheduler-investigation-fallback --opencode
```

Same non-CI, local-only, advisory posture as the fixture above.

- **php-scheduler-housekeeping-competes** (ticket 06, Housekeeping Track wired into the scheduler). Same
  deterministic node inventory as `php-clean`/`php-scheduler-investigation-fallback` — Safety Net **and**
  Guardrails both fully resolved. `## Safety Net` (`Cadence: 90`, `Last scan: 2026-09-01`,
  `overdue_ratio ≈ 0.2`) is **not due**; `## Guardrails` (`Cadence: 60`, `Last scan: 2026-07-01`,
  `overdue_ratio ≈ 1.33`) **is due**; `## Housekeeping` (`Cadence: 7`, `Last scan: 2026-08-20`,
  `overdue_ratio ≈ 4.29`) **is due at a materially higher ratio**. Expects **Housekeeping** selected —
  proving its real, hand-editable day-count `Cadence` wins the genuine ratio comparison even though the
  fixed tie-break order (Safety Net > Guardrails > Housekeeping > Investigation) ranks Guardrails above
  it — the same point `php-scheduler-staleness-selection` already established one level up the order.
  Unlike the other `php-scheduler-*` fixtures, selecting Housekeeping doesn't hand off to `refactor-scan`
  at all: the run continues into `housekeeping-track.md`'s own process (reconcile,
  open this cycle's issue from the one contributed `housekeeping-template.md` line, work the checklist,
  quality gate), stopping at `opening-a-merge-request.md`'s "no forge/remote available" branch (this
  sandbox has no git remote) — confirming the pre-existing `continuous-housekeeping` process content
  still runs correctly once triggered via the new scheduler-driven path instead of its own retired
  standalone due-check.

```bash
./fixtures/harness/run.sh scheduler php-scheduler-housekeeping-competes --opencode
```

Same non-CI, local-only, advisory posture as the two fixtures above.

- **php-scheduler-bootstrap-investigation** / **php-scheduler-bootstrap-guardrails** /
  **php-scheduler-bootstrap-housekeeping** / **php-scheduler-bootstrap-resumes** (ticket 07, the one-time
  exception that overrides ordinary ratio/tie-break selection for exactly three turns right after Safety
  Net's own `Open` first empties). Each exercises one turn of the sequence Investigation → Guardrails →
  Housekeeping, plus the "retired permanently afterward" case — see each fixture's own
  `expected/behavior.md` for the full seeded state and reasoning.
  - **php-scheduler-bootstrap-investigation** — `## Safety Net` just closed (`Open` list `- none`, `Last scan`
    one day old); `## Guardrails`/`## Housekeeping`/`## Investigation` all absent (never run). Under
    *ordinary* selection alone this would tie all three as "never run" and the fixed tie-break order
    would pick Guardrails; the one-time exception must instead pick **Investigation** — this ticket's own
    adversarial case, a more-overdue-by-the-ordinary-rules Track losing to the exception's own order.
  - **php-scheduler-bootstrap-guardrails** — same Safety Net state; `## Investigation` now present with
    `Pending candidates: none` (its own turn already fully delivered, not just proposed); `##
    Guardrails`/`## Housekeeping` still absent. Expects **Guardrails** selected, confirming the sequence
    advances instead of re-selecting Investigation — otherwise the scheduler's permanent fallback.
  - **php-scheduler-bootstrap-housekeeping** — `## Investigation` and `## Guardrails` both present (their
    own turns done); `## Housekeeping` still absent. Expects **Housekeeping** selected, the sequence's
    third and final turn.
  - **php-scheduler-bootstrap-resumes** — all four sections present (every one-time-exception turn long
    finished); `## Guardrails` genuinely overdue (`overdue_ratio ≈ 1.33`), `## Safety Net`/`##
    Housekeeping` not due. Expects **Guardrails** selected via ordinary ratio comparison, confirming the
    exception is permanently retired — not re-triggered by Investigation being technically due "by
    elimination," and not re-triggered by Safety Net's `Open` still reading empty.

```bash
./fixtures/harness/run.sh scheduler php-scheduler-bootstrap-investigation --opencode
./fixtures/harness/run.sh scheduler php-scheduler-bootstrap-guardrails --opencode
./fixtures/harness/run.sh scheduler php-scheduler-bootstrap-housekeeping --opencode
./fixtures/harness/run.sh scheduler php-scheduler-bootstrap-resumes --opencode
```

Same non-CI, local-only, advisory posture as the three fixtures above.

- **php-scheduler-safety-net-blockade** (ticket 08, Safety Net blockade with nothing workable). `##
  Safety Net` `Open` is non-empty (`phpstan-level-6`, `coverage-floor`) but both entries are non-workable
  (blocked by prerequisite, flagged `needs-info`). Expects **Safety Net** selected — the blockade is
  unconditional: while Safety Net `Open` is non-empty, it is selected and nothing else runs, even if no
  node is currently workable; what it waits on is reported. Guardrails (due at `overdue_ratio ≈ 1.33`),
  Housekeeping, and Investigation are all blocked by the blockade despite being otherwise eligible.

- **php-scheduler-guardrails-stalled** (ticket 08, Guardrails yields when nothing workable). `##
  Guardrails` `Open` is non-empty (`phpstan-level-6`, `coverage-floor`) but both entries are
  non-workable (blocked or `needs-info`). Per the Eligibility rule, Guardrails with `Open` non-empty but
  nothing workable yields — it drops out of ratio comparison. Expects **Housekeeping** selected (ratio
  ≈4.29, the highest among remaining due Tracks). Guardrails' `Open` stays as it is; no node is removed.

- **php-scheduler-housekeeping-preempts-guardrails** (ticket 08, Housekeeping preempts Guardrails
  backlog). `## Guardrails` `Open` is non-empty with workable entries (`composer-audit`, `phpmd`); `##
  Housekeeping` is due at `overdue_ratio ≈ 4.29`. Expects **Housekeeping** selected — the preemption
  rule fires: Housekeeping preempts Guardrails for one pass when due (`overdue_ratio >= 1`), even though
  Guardrails has higher tie-break priority. Guardrails resumes afterwards.

- **php-scheduler-bootstrap-guardrails-open** (ticket 08, bootstrap exception advances past Guardrails'
  non-empty `Open`). `## Guardrails` is present with non-empty `Open` (`phpstan-level-6`,
  `coverage-floor`) from its own bootstrap scan; `## Housekeeping` is absent. The one-time exception's
  condition 3 fires (Housekeeping absent) — it reads only section *existence*, not `Open` *emptiness*.
  Expects **Housekeeping** selected, confirming the bootstrap sequence advances regardless of Guardrails'
  `Open` state.

```bash
./fixtures/harness/run.sh scheduler php-scheduler-safety-net-blockade --opencode
./fixtures/harness/run.sh scheduler php-scheduler-guardrails-stalled --opencode
./fixtures/harness/run.sh scheduler php-scheduler-housekeeping-preempts-guardrails --opencode
./fixtures/harness/run.sh scheduler php-scheduler-bootstrap-guardrails-open --opencode
```

### php-track-open-* (Track Open walk, ticket 07)

Not tooling-tree fixtures — no deterministic ground truth (local-only, advisory), same reasoning as
`php-safety-net-*`/`php-guardrails-*` above. Exercises the orchestrator's own `Open` walk behavior
(`skills/refactor-scan/references/track-open-processing.md`) — top-to-bottom processing,
Fulfilment re-check, and non-workable node collection. See each fixture's own
`expected/behavior.md` for the full seeded state and reasoning.

- **php-track-open-hand-adopted** — `## Safety Net`'s `Open` lists `php-cs-fixer (#5)` at the top,
  but `friendsofphp/php-cs-fixer` is already installed and configured (adopted by hand after the
  scan). Expects the re-check to find `php-cs-fixer` fulfilled, remove it from `Open` without a
  merge request, and continue to the next workable node (`phpunit`).

- **php-track-open-blocked-in-between** — `## Safety Net`'s `Open` lists `phpunit (#6)`,
  `phpstan-level-0 (#7)`, `php-cs-fixer (#5)`. `phpstan-level-0` is blocked by `static-code-analyzer`
  (required parent not fulfilled). Expects `phpunit` worked (first workable node), `phpstan-level-0`
  skipped with reason ("blocked by static-code-analyzer") in the pass report, and `php-cs-fixer` not
  worked (exactly one node per pass).

- **php-track-open-priority-vs-top** — `## Safety Net`'s `Open` lists `phpunit (#6)`. A separate
  `refactor:priority`-labeled structural candidate (`01-shallow-user-service.md`) exists on the
  tracker. Expects the Safety Net blockade to remain active (Open non-empty), the `Open` walk to
  process `phpunit`, and the priority issue to wait — Rank mode is not invoked, and the priority
  issue does not bypass the blockade.

- **php-track-open-priority-guardrails** — Guardrails counterpart of the fixture above. Safety Net is
  closed (`Open` list `- none`), `## Guardrails`'s `Open` is the complete Guardrails backlog as a list, `phpmd (#5)` first (workable), Housekeeping is not
  due, and a separate `refactor:priority`-labeled structural candidate (`01-shallow-user-service.md`)
  exists on the tracker. Expects Guardrails selected, the `Open` walk to work `phpmd` this pass, and
  the priority issue to wait until Guardrails has no workable node left — the label narrows the Rank
  pool, is otherwise only a tie-breaker between equally ranked candidates, and never preempts an `Open`
  walk; Rank mode is not invoked.

```bash
./fixtures/harness/run.sh safety-net-track php-track-open-hand-adopted --opencode
./fixtures/harness/run.sh safety-net-track php-track-open-blocked-in-between --opencode
./fixtures/harness/run.sh safety-net-track php-track-open-priority-vs-top --opencode
./fixtures/harness/run.sh guardrails-track php-track-open-priority-guardrails --opencode
```

Same non-CI, local-only, advisory posture as the scheduler fixtures above.

### php-housekeeping-* (Housekeeping Track, ticket 09)

Not tooling-tree fixtures — no deterministic ground truth (local-only, advisory), same reasoning as
`php-safety-net-*`/`php-guardrails-*` above. Exercises the Housekeeping Track's reconciliation sweep
(`skills/continuous-housekeeping/references/housekeeping-track.md`): each cycle it checks only the
nodes that carry a `Housekeeping` field and judges their Fulfilment check itself (agent judgement) —
it no longer reads the retired `Fulfilled nodes` cache (ADR-0056). See each fixture's own
`expected/behavior.md` for the full expected behavior.

- **php-housekeeping-hand-adopted-guardrails** — `composer-audit` adopted by hand (CI runs
  `composer audit` through a workflow step) with no delivering merge request anywhere in the
  tracker's history; `## Guardrails` already closed (`Open` list `- none`), `## Housekeeping` due
  (`Cadence: 7`, `Last scan: 2026-09-01`), no `housekeeping-template.md` yet (first cycle). Expects
  the reconciliation to judge the `Housekeeping`-fielded nodes fulfilled by their Purpose —
  `composer-audit`, `phpstan-level-0`, `php-minimal-version` get their lines, `semgrep` (absent)
  doesn't — so the hand-adopted Guardrails tool gets its Housekeeping checklist line at the next
  cycle even though no merge request ever delivered it and this target's bookkeeping.md carries no
  `Fulfilled nodes` at all.

- **php-housekeeping-old-schema** — `docs/refactoring/bookkeeping.md` still in the pre-ADR-0055
  shape (`Fulfilled nodes` populated, global `Pending candidates`, no Track sections anywhere),
  with the listed nodes genuinely fulfilled by the project. Expects a normal Housekeeping pass: the
  retired `Fulfilled nodes` field is ignored — never read as an input, not migrated, left exactly as
  it was — while the reconciliation judges fulfilment itself, creates
  `housekeeping-template.md`, and the closing call writes `## Housekeeping` around the old content.

```bash
./fixtures/harness/run.sh housekeeping-track php-housekeeping-hand-adopted-guardrails --opencode
./fixtures/harness/run.sh housekeeping-track php-housekeeping-old-schema --opencode
```

Same non-CI, local-only, advisory posture as `safety-net-track`/`guardrails-track`/`scheduler`.

### Tier 3 — Ground Truth (local-only, advisory — ADR-0055, ticket 03)

Not CI-gated (as of ADR-0055's ticket 03 — it used to gate CI, alongside `tier1`/`tier2`, in a
dedicated `tier3` job). `tier3` measures precision/recall — planted candidates
(`expected/issues/*.md`) vs. what a run actually filed under `.scratch/**/issues/` — and, per
ticket 27's Tier 5, checks that recall against a committed baseline (`fixtures/baselines/`,
gitignored). It used to be downstream of `tooling_tree.py`'s own deterministic,
hardcoded-dependency-name detection for every node — stale for exactly the Safety Net/Guardrails
nodes ADR-0055 (tickets 01/02) moved to agent judgement against each node's own Purpose statement,
and a detection ADR-0056 has since deleted outright. CI has no model credentials to run the
agent-judged check that would actually be accurate instead, so `tier3` runs local-only/advisory now
too — same posture as `tier4`'s non-deterministic parts, `judge`, `lift`, `agent-loop`, and
`decision-gate-bypass`. `tier1` (static validation) and `tier2` (artifact contracts) are unaffected
and still gate CI.

```bash
./fixtures/harness/run.sh tier3 php-project-with-candidates
```

### Tier 4 — Trigger & Discoverability tests (ticket 27)

Ticket 27's three negative controls split across two layers:

- **Deterministic** (`scripts/test_trigger_controls.py`, CI-gated via the `tier4` job): "scan on clean repo reports clean" is a real, fully-testable property of the deterministic graph logic — see `php-clean` above. The other two controls are prose-level judgment calls a skill makes, for two distinct reasons: "no git" is `refactor-scan`'s own step-1 precondition — whether that precondition is actually *followed* is a model-behavior question, not something the script decides; "not a PHP project" is ADR-0008's deliberate carve-out, which keeps language recognition an informal heuristic on purpose ("premature before a second language specialization exists"). Either way, this module only checks the ground-truth *signal* each judgment reads (the tree's edges keep every PHP-tree leaf gated behind `composer`/`is-php-project`, so nothing past the generic root is proposable without them), not the judgment itself.
- **Behavioral** (`fixtures/harness/run.sh tier4 <fixture> --opencode`, local-only advisory, same non-CI posture as `agent-loop`): runs all three negative controls end-to-end via opencode, plus **explicit + implicit invocation per skill** — for each of the five lifecycle skills, both `/skill-name` and a natural-language paraphrase of its `description` should trigger it; for the orchestrator (`continuous-refactoring`, which ships `disable-model-invocation: true`), only the explicit form should.

```bash
./fixtures/harness/run.sh tier4 php-clean --opencode --verbose
```

Without `--opencode` it just points at the deterministic test module and exits — same degrade-gracefully shape as every other `--opencode` tier when the binary is missing.

### Tooling-tree script (dry-run, no MR) — seed input, backlog output

The forward-simulating `roadmap` tier and its fixture matrix are gone: with the parser's detection
code deleted (ADR-0056), `skills/refactor-scan/references/tooling_tree.py` detects nothing and no
longer predicts a next-10-MRs chain, and the eight `expected/roadmap.json` files were removed with
it. What the script does today is the tree's graph logic only — dry-run, no mutation,
deterministic given its inputs:

- **Input:** the tree docs plus the recorded rejections, and a fulfilled set — either handed over
  as a seed file (the `--seed` argument or the Refactoring Notes' `fulfilled-set.json`, a
  `{node_slug: true/false}` JSON: the scan pass's agent judgement as a file — the agent judges,
  the script orders) or, when no seed is given, derived from `bookkeeping.md`'s Track sections (a
  scope node neither in `Open` nor in `Out-of-scope` is fulfilled).
- **Output** (JSON): `backlog` — the ordered `Open` a scan should record: every unresolved node of
  the Track's scope in tree order, blocked ones included; `next` — the currently-workable nodes;
  `withheld`/`withheld_with_reasons` — nodes held back, with the reasons the stalled report needs;
  `closed_by_rejection` — nodes derived as closed by a rejected required ancestor;
  `reversals`/`php_floor_blocked` — the PHP-version findings; `detected` — the resolved fulfilled
  map the outputs were computed from; `tree.edges`. `--unblocked-by NODE` adds the merge-request
  outlook view: every node NODE's fulfilment newly makes proposable.

```bash
python3 skills/refactor-scan/references/tooling_tree.py fixtures/php/php-clean/project            # seed auto-discovered from the Refactoring Notes
python3 skills/refactor-scan/references/tooling_tree.py <repo> --seed fulfilled-set.json          # explicit seed (the scan-pass contract)
python3 skills/refactor-scan/references/tooling_tree.py <repo> --unblocked-by composer           # outlook: what landing `composer` unblocks
```

The contract is pinned deterministically by `scripts/test_tooling_tree.py` (CI-gated via
`python3 -m unittest discover -s scripts -p 'test_*.py'`); the drift check comparing the manual
tree-walk fallback's prose rules with the script's graph logic on shared seeds is
`scripts/drift_check.py` (advisory, run manually — not collected by CI's `test_*.py` discovery).

For agents (subprocess):

```python
# direct deterministic check — importlib, not a dotted import: "refactor-scan"'s
# hyphen makes `skills.refactor_scan...` an invalid package path
import importlib.util, json, pathlib
spec = importlib.util.spec_from_file_location("tooling_tree", "skills/refactor-scan/references/tooling_tree.py")
tooling_tree = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tooling_tree)
data = tooling_tree.detect_and_roadmap(pathlib.Path("fixtures/php/php-p0-nonempty"), fulfilled={"git": True})
assert "composer" in data["backlog"]  # etc. — workable: data["next"], withheld: data["withheld_with_reasons"]
```

### Reproducible local opencode test (for humans and agents)

Prerequisites — one-time setup, shared by every `--opencode` tier in this README (`tier4`, `judge`,
`lift`, `decision-gate-bypass`, and the Track tiers):

```bash
# 1. Python + deps (for deterministic checks)
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

Every `--opencode` tier documents its own run command in its own section above; all of them share
`run_opencode_advisory`'s isolated invocation (only `skills/` from this repo via an
`.agents/skills` symlink — no `~/.config/opencode/skills`) and its degrade-gracefully behavior: no
`opencode` binary found → one info line, exit clean, nothing fails.

Troubleshooting:

* `opencode binary not found` → `npm i -g opencode` or use `npx --yes opencode`.
* `permission requested: external_directory … auto-rejecting` → add `--auto` (the harness does this).
* Long runtime → harness uses `timeout 60`; increase if model is slow.

### Agent loop test (full pass, subagent-observed)

Formalizes the manual dry-run methodology that validated ADR-0010 (see [ADR-0010](../docs/adr/0010-orchestrator-explicit-data-flow.md) `## Validation`) so it can be repeated against this repo's own fixtures instead of an ad-hoc scratch copy of some other project. Where the `--opencode` tiers above drive single skills or single checks via an isolated `opencode` subprocess, this drives the **full 6-step pass** (`skills/refactor-loop/SKILL.md`, reached from `skills/continuous-refactoring/SKILL.md` via the selected Track's own skill: scan → learn → prioritise → design → implement → learn) via a Claude Code **Agent-tool subagent** — the tool a Claude Code session itself has, not a subprocess this script can launch. So `run.sh agent-loop` only prepares; running the subagent is a manual step, same as `--opencode` staying local-only and out of CI.

```bash
./fixtures/harness/run.sh agent-loop php-partial
```

What it does:

1. Reuses `setup_fixture` — isolated copy at `/tmp/continuous-refactoring-tests/<fixture>`, fresh git repo, no remote (safe to commit/branch inside freely).
2. Seeds `docs/agents/triage-labels.md`, a minimal `CONTEXT.md`, and `docs/adr/` — but deliberately **not** `docs/agents/issue-tracker.md`: with no `origin` remote in this sandbox, that file is left for the dispatcher's own onboarding interview (`skills/continuous-refactoring/references/onboarding-setup-interview.md`) to create (the `php-onboarding-*` fixtures bring their own `docs/agents/` state and are not seeded), converging on Local Markdown on its own — pre-seeding it would skip the one thing this dry-run mode exists to actually exercise.
3. Writes a ready-to-use prompt to `/tmp/continuous-refactoring-tests/agent-loop-prompt-<fixture>.md`: read `skills/continuous-refactoring/SKILL.md` and follow it literally, one invocation (a sandbox with no Refactoring Notes is onboarded and the invocation ends there; the prompt then has the subagent commit the files and run a second invocation, which is the ordinary pass), note (don't silently fix) ambiguity, follow the interview's own "no human present" fallback if nobody's here to answer it, write friction notes to `agent-loop-friction-<fixture>.md`.
4. Prints the sandbox and prompt paths and stops — spawn the subagent yourself (Agent tool, `run_in_background: false`, prompt = the file's contents) and let it run.

Afterwards, inspect the sandbox to see what happened: `git -C /tmp/continuous-refactoring-tests/<fixture> log`, `docs/refactoring/bookkeeping.md` / `merge-requests.md`, `.scratch/refactor/issues/`, and the friction file. An optional advisory sanity check (not a hard gate — subagent output isn't deterministic):

```bash
source fixtures/harness/lib/assertions.sh
assert_config_format "/tmp/continuous-refactoring-tests/<fixture>/docs/refactoring/bookkeeping.md"
assert_git_has_new_commits "/tmp/continuous-refactoring-tests/<fixture>" 2   # 2 = after setup_fixture's init + tracker-seed commits
```

`php-partial` is a good default target — no `docs/refactoring/bookkeeping.md` yet, so the first invocation is the dispatcher's onboarding step (it ends after writing the setup files); the second invocation, run once those files are committed, is the ordinary pass that reasons about `composer`'s children. The prompt tells the subagent to run both. The `php-onboarding-*` fixtures target the onboarding invocation alone. Any fixture name works; nothing here depends on `php-partial` specifically.

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

### Tier 5 — regression baseline, rubric grading, lift measurement (ticket 27)

**Regression-baseline gate (local-only, advisory — ADR-0055, ticket 03):** Tier 3's precision/recall baselines live at `fixtures/baselines/` — gitignored ("generated, not committed"). Before ticket 03, a dedicated CI `tier3` job restored/saved them via `actions/cache` (`.github/workflows/test-harness.yml`) and failed the build on regression; that job is gone along with `tier3`'s own CI gating (see "Tier 3" above) — run it locally instead:
```bash
./fixtures/harness/run.sh tier3 php-project-with-candidates
```
`run_tier3` compares the freshly-computed recall against whatever baseline is on disk (`assert_baseline_not_regressed`, `fixtures/harness/lib/assertions.sh`) *before* overwriting it, and reports a regression if recall dropped. Caveat worth knowing before you touch this: without a real `agent-loop`/`--opencode` run first, `found` is always `0` (nothing files under `.scratch/**/issues/` from a dry deterministic pass alone), so the check is comparing `0` against `0` until a baseline records an actual recall from one of those runs. The `roadmap` fixture matrix that used to sit alongside it as this harness's other regression check is gone — removed together with the forward-simulating `roadmap` output and the parser's detection code (ADR-0056; see "Tooling-tree script" above).

**LLM-judge rubric grading** (local-only, advisory, non-CI): grades one fixture's post-pass artifacts against `fixtures/harness/rubric.md`'s five dimensions (process fidelity, candidate selection, artifact quality, state hygiene, honesty about ambiguity).

```bash
./fixtures/harness/run.sh judge php-project-with-candidates --opencode
```

**With-skill vs. without-skill lift measurement** (local-only, advisory, non-CI): runs the same prompt twice against the same fixture state — once with `skills/` mounted the way every other `--opencode` check does, once with no skill guidance at all — so the two transcripts can be compared by hand or graded against the rubric above.

```bash
./fixtures/harness/run.sh lift php-partial --opencode
```

Both commands share the same degrade-gracefully behavior as every other `--opencode` tier: no `opencode` binary found → one info line, exit clean, nothing fails.

**Decision-gate `ready-for-agent` bypass regression** (local-only, advisory, non-CI; fixture: `php-decision-gate-bypass`, ADR-0053): reproduces the bug ADR-0053 fixes — an externally-labeled candidate issue pre-tagged `ready-for-agent`, describing a change that isn't actually fully specified (two retry implementations with genuinely different backoff contracts). Runs `refactor-design` against the seeded issue (`.scratch/refactor/issues/01-unify-retry-logic.md`), then checks — a real grep against the committed fixture, not a judgment call — whether the pre-existing `ready-for-agent` got actively cleared and `needs-info` added, per `skills/refactor-design/references/decision-gate.md`. A second pass then runs `refactor-scan` and looks (advisory, LLM output isn't deterministic) for it correctly holding the candidate back instead of routing it to `refactor-implement`. Full expected behavior: `fixtures/php/php-decision-gate-bypass/expected/behavior.md`.

```bash
./fixtures/harness/run.sh decision-gate-bypass php-decision-gate-bypass --opencode
```

Unlike the other `--opencode` checks above, this one passes `opencode run` the `--auto` flag directly (this scenario's broader, unattended-mode prompt was observed to make the model explore outside its working directory, tripping the permission wall `--auto` avoids — see Troubleshooting below) — same degrade-gracefully behavior otherwise.

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

- `expected/docs/refactoring/bookkeeping.md` — Loop configuration (cadence: weekly)
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
3. Create `expected/` as sibling to `project/` — e.g., `expected/behavior.md`, `expected/issues/` with `refactor:candidate` issues, `expected/docs/refactoring/` — **never inside `project/`** (so it is not mounted into Docker / not visible to the code under test)
4. Document the fixture's purpose and tooling-tree state in this README (see `php-empty` … `php-psalm` examples above)

## Design Principles

- **Self-contained:** Each fixture is an independent project, not a submodule
- **Deterministic:** Fixtures produce the same scan results every run
- **Resettable:** Fixtures can be restored to their original state via git
- **Documented:** Expected outcomes are explicit in `expected/`
