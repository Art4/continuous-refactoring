# Expected behavior — Track scheduler, Investigation as permanent fallback

The orchestrator's own Track-selection step (`skills/continuous-refactoring/SKILL.md` step 1, algorithm
in `skills/continuous-refactoring/references/track-scheduler.md`) picking **Investigation**
(`CONTEXT.md`) — this ticket's own core case: a Track with no numeric `Cadence`, always due and always
eligible, selected purely because nothing else with a real ratio is due this pass, then handed off to
`refactor-scan`'s own `skills/refactor-scan/references/investigation-track.md`.

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks or scheduling
at all; this is a behavioral property of `continuous-refactoring/SKILL.md` and `track-scheduler.md`,
checked the same non-CI, local-only, advisory way `safety-net-track`/`guardrails-track`/
`php-scheduler-staleness-selection` already are. Run via `fixtures/harness/run.sh scheduler
php-scheduler-investigation-fallback --opencode`.

## Seeded state

The Safety Net **and** the Guardrails are both fully closed — same deterministic node inventory as the
`php-clean` fixture (`composer`, `psr-4`, `ci-runner`, `php-cs-fixer`, `phpunit` CI-gated,
`phpstan-level-0`, the `rector-*` family, `composer-audit`, `phpmd`, `coverage-floor`,
`php-minimal-version`, `semgrep`; `phpstan-level-1..10`, `phpstan-deprecation-rules`, and
`psalm-taint-analysis` explicitly rejected under `out-of-scope/`) — confirmed via a direct
`tooling_tree.py` run before trusting this file: `php-safety-net: true`, and `next` holds nothing but
`structural-scan`.

`.scratch/refactor/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-01` (18 days before this fixture's reference date
  of 2026-09-19 → `overdue_ratio ≈ 0.2`), `Open` list `- none`. **Not due.**
- `## Guardrails` — `Cadence: 60`, `Last scan: 2026-09-10` (9 days before → `overdue_ratio = 0.15`),
  `Open` list `- none`. **Not due.**
- `## Investigation` — `Cadence: continuous`, `Last scan: 2026-08-01`. No `Open` field at all (this
  section never carries one). Per `track-scheduler.md`'s own Eligibility section, a `continuous` Cadence
  carries no day-count to divide by — always due, no ratio to compute — and Investigation is always
  eligible regardless (no `Open` precondition). `Last scan`'s own value is irrelevant to this due-check,
  unlike the other two sections' own `Last scan`.

Neither Safety Net nor Guardrails is due this pass — the *only* due-and-eligible Track is Investigation,
which wins not by outranking either on staleness (it never produces a comparable ratio at all) but
because nothing else qualifies. This is the scenario the spec's own "always eligible, lowest tie-break
priority" line describes: Investigation as the scheduler's guaranteed fallback whenever nothing else is
due, confirmed here with a fixture where two other real, numerically-scored Tracks are wired and simply
aren't stale enough to compete.

## Expected: `continuous-refactoring` pass, Track-selection step

Run the orchestrator's Track-selection step (step 1), then hand off to `refactor-scan` for that Track
only — stop there, don't continue through design/implement. It should:

1. Read `## Safety Net`, `## Guardrails`, and `## Investigation`; compute (or, for Investigation, note the
   absence of) each `overdue_ratio`.
2. Recognize Safety Net (`≈0.2`) and Guardrails (`≈0.15`) are both **not due** — neither reaches `>= 1`.
3. Recognize Investigation is due (no numeric `Cadence`, always due) and eligible (no `Open` concept).
4. **Select Investigation** — the only due-and-eligible Track this pass, not by winning a ratio
   comparison but because it's the scheduler's own permanent fallback.
5. Hand the Investigation Track to `refactor-scan` as an explicit input; `refactor-scan` runs
   `investigation-track.md`'s own process and proposes `structural-scan` — already unblocked (every
   resolved-edge parent resolved), and, per this ticket's own scope, gated behind this Track's own
   selection rather than proposed unconditionally.
6. Neither `## Safety Net` nor `## Guardrails` is touched this pass (both still due-check-eligible for a
   future pass, just not this one) — no write to either section should happen.

## The bug this regression-tests

Before this ticket, `## Investigation` didn't exist as a bookkeeping section at all — Investigation
structurally couldn't enter Track-selection's ratio comparison (ticket 04's own PR report: "Housekeeping
and Investigation... have no bookkeeping section yet, so they structurally can't enter ratio comparison
today"), and `structural-scan` was proposed unconditionally, every pass, the moment its own resolved-edge
parents cleared, with no Track gate at all — a target could get a structural proposal on a pass Safety
Net/Guardrails staleness should arguably have taken priority instead (moot here, since neither is due,
but the absence of gating was real regardless). This fixture is the first regression test of Investigation
actually competing, and of `structural-scan`'s own proposal now depending on that competition's outcome.

## Verified

Confirmed live via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh scheduler
php-scheduler-investigation-fallback --opencode` — see the implementing pull request's own report for the
transcript summary.
