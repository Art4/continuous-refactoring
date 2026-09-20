# Expected behavior — Guardrails Track: a scan fills `Open` with the complete backlog

Confirms that when the Guardrails Track is selected with an **empty** `Open`, its scan records the
**complete** backlog — every unresolved node of the Track's scope, blocked nodes included, in the
script's deterministic order — plus `Last scan`, instead of only the currently-proposable nodes
(`skills/refactor-scan/references/guardrails-track.md`'s *Filling `Open`*,
`skills/refactor-learn/references/guardrails-write.md`). Spec case 4 of
`agent-judged-fulfilment`.

Not deterministically checkable end to end — the fulfilment judgement and the bookkeeping write are
agent behavior. The ordered list below *is* deterministic given the seed and was computed with
`tooling_tree.py` (see *Seeded state*). Run via `fixtures/harness/run.sh guardrails-track
php-guardrails-scan-fills-open --opencode`, same non-CI, local-only, advisory posture as
`safety-net-track`/`guardrails-track`.

## Seeded state

The Safety Net is fully closed (same shape as `php-guardrails-open-blocks-rescan`'s own seeded state —
`psr-4`/`ci-runner`/`php-cs-fixer`/`phpunit`/`phpstan-level-5`/the `rector-*` family resolved,
`psalm-taint-analysis` rejected under `out-of-scope/`), so every Guardrails node is reachable in the
tree. All eleven Guardrails scope nodes are genuinely still missing.

`docs/refactoring/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-01` (`overdue_ratio ≈ 0.2`), `Open` list `- none`.
- `## Guardrails` — `Cadence: 60`, `Last scan: 2026-07-01` (80 days before this fixture's reference date
  of 2026-09-19 → `overdue_ratio ≈ 1.33`), **`Open` list `- none`**, `Out-of-scope` list `- none`. **Due and eligible.**
- `## Housekeeping` — `Cadence: 7`, `Last scan: 2026-09-15` (`overdue_ratio ≈ 0.57`). Not due.
- `## Investigation` — `Cadence: continuous`, `Last scan: 2026-09-10`. All four sections present, so the
  one-time bootstrap exception is done.
- Top-level `Pending candidates: none`.

Seed the scan is expected to hand the script (every node fulfilled except the eleven Guardrails scope
nodes, `structural-scan` (Investigation) and the rejected `psalm-taint-analysis`), and the script's
output for it (`python3 skills/refactor-scan/references/tooling_tree.py --seed <seed> <fixture-project>`):

- `next` (workable now): `phpmd`, `coverage-floor`, `composer-audit`, `phpstan-level-6`,
  `phpstan-deprecation-rules`, `php-minimal-version`, `semgrep`.
- `withheld_with_reasons` (blocked): `phpstan-level-7` (blocked by required parent `phpstan-level-6`),
  `phpstan-level-8` (by `phpstan-level-7`), `phpstan-level-9` (by `phpstan-level-8`),
  `phpstan-level-10` (by `phpstan-level-9`).
- `backlog`, filtered to the Guardrails scope (the raw list also carries the Investigation node
  `structural-scan`, which is not this Track's): `phpmd`, `coverage-floor`, `composer-audit`,
  `phpstan-level-6`, `phpstan-level-7`, `phpstan-level-8`, `phpstan-level-9`, `phpstan-level-10`,
  `phpstan-deprecation-rules`, `php-minimal-version`, `semgrep`.

## Expected: `continuous-refactoring` pass

1. Track selection picks **Guardrails**: it is due (~1.33) and eligible (`Open` empty); Safety Net and
   Housekeeping are not due, and Investigation carries no ratio to compete with.
2. `refactor-scan` runs a genuine Guardrails scan (`Open` is empty, so no walk): it judges every scope
   node's Fulfilment check against its Purpose, hands that fulfilled set to the script as a seed, and
   takes the resulting `backlog` in the script's order.
3. `refactor-learn`'s closing call writes `## Guardrails`:
   - `Open`, as a bullet list under `**Open:**`, in exactly this order, one bullet per node, **no
     issue numbers** (none is being worked) — the four blocked `phpstan-level-7..10` entries are
     present, not omitted:
     - `phpmd`
     - `coverage-floor`
     - `composer-audit`
     - `phpstan-level-6`
     - `phpstan-level-7`
     - `phpstan-level-8`
     - `phpstan-level-9`
     - `phpstan-level-10`
     - `phpstan-deprecation-rules`
     - `php-minimal-version`
     - `semgrep`
   - `Last scan` set to today's date.
   - `Out-of-scope` left as it was (`- none`); `## Safety Net`, `## Housekeeping`, `## Investigation`
     and `Pending candidates` untouched.
4. No candidate issue is filed for any of the recorded nodes (Track nodes are no longer pre-filed).

## The behavior this regression-tests

Under the earlier semantics `Open` held only nodes that had been proposed and filed, so a blocked node
was invisible until its parent landed. The complete-backlog rule makes `Open` the whole remaining
scope: a maintainer can see what is left and reorder it, and `Open` empty genuinely means the Track is
done.

## Verified

Not yet confirmed live against an opencode model run. The ordered list was computed from the seed with
`tooling_tree.py` on 2026-09-20.
