# Expected behavior — hand-adopted Guardrails tool gets Housekeeping line

Confirms a Guardrails tool adopted by hand (no delivering merge request in the tracker's history)
gets its `Housekeeping` checklist line via agent judgement in the reconciliation step, without
reading `Fulfilled nodes`.

Not deterministically checkable — pure skill process behavior. Run via
`fixtures/harness/run.sh housekeeping-track php-housekeeping-hand-adopted-guardrails --opencode`,
same non-CI, local-only, advisory posture as `decision-gate-bypass`.

## Seeded state

The project has `composer-audit` fulfilled by hand (the `composer audit` command exists and is
invoked in CI via a workflow step), but no merge request in the tracker's history that delivered
it. The Guardrails section in `bookkeeping.md` shows `Open` list `- none` — the Guardrails Track has
already closed. There is no `housekeeping-template.md` yet (first Housekeeping cycle for this
target). The `## Housekeeping` section exists with `Cadence: 7`, `Last scan: 2026-09-01`.

## Expected: Housekeeping Track reconciliation

When the Housekeeping Track runs its reconciliation:

1. It walks the tooling tree and checks only nodes that carry a `Housekeeping` field.
2. For each node, it judges the Fulfilment check against the node's Purpose statement (agent
   judgement), NOT by reading `Fulfilled nodes`.
3. `composer-audit` is judged fulfilled (CI runs `composer audit` via the workflow), so its
   `Housekeeping` line ("Review `composer audit`'s report; attempt a fix for anything with an
   available patched version.") is appended to `housekeeping-template.md`.
4. `phpstan-level-0` is judged fulfilled (phpstan.neon with level 0, empty baseline exists), so
   its `Housekeeping` line is appended.
5. `php-minimal-version` is judged fulfilled (PHP 8.1 declared in composer.json), so its line is
   appended.
6. `semgrep` is NOT fulfilled (no semgrep config/workflow), so its line is NOT added yet.
7. The `Fulfilled nodes` field (which doesn't even exist in this fixture's bookkeeping.md) is
   never read — the reconciliation uses agent judgement exclusively.

## Expected: housekeeping-template.md

After reconciliation, `housekeeping-template.md` should contain the lines contributed by the
fulfilled nodes (composer, phpstan-level-0, php-minimal-version, and php-cs-fixer via its
delivering MR, if any). The file should NOT require `Fulfilled nodes` to exist in
`bookkeeping.md` for the reconciliation to succeed.

## The behavior this regression-tests

Before this ticket, the Housekeeping reconciliation read `Fulfilled nodes` to discover which
nodes contributed housekeeping lines. A hand-adopted Guardrails tool with no delivering MR
would never appear in `Fulfilled nodes` (which only tracked ordinary tooling-tree adoptions),
so its housekeeping line would be permanently missing. Agent judgement closes this gap.

## Verified

Not yet manually confirmed live against an opencode model run — see the implementing pull request's
own report for what was attempted and observed.
