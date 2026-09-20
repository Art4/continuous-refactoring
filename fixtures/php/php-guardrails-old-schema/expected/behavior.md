# Expected behavior — Guardrails Track mid-migration pass-through

Confirms a target that's already worked through ticket 01's own migration (`## Safety Net` present and
closed) but never run a Guardrails Track pass — and whose `Fulfilled nodes` field still carries
pre-ADR-0055 residue for nodes the Safety Net Track has since taken over (`composer`, `php-cs-fixer`,
`phpunit`, `psr-4`, `phpstan-level-0`, the `rector-*` family — none of which the new schema ever writes
there again, per `skills/continuous-refactoring/references/refactoring-bookkeeping.md`'s "no Done
cache" `## Safety Net` design) — runs a normal Guardrails Track pass without erroring on, migrating, or
needing to understand that stale residue.

Deliberately **not** the same scenario as `fixtures/php/php-safety-net-old-schema` (a target still
fully on the pre-ADR-0055 shape, no Track section at all): a fully pre-ADR-0055 repo would never reach
the Guardrails Track in the same pass in the first place — the Safety Net Track is more overdue (no
section at all beats any `Cadence`-based staleness) and outranks Guardrails in the fixed priority order
(`CONTEXT.md`'s **Track** entry), so it would run first. The scenario this fixture actually tests —
Safety Net done, Guardrails never run, old-style fields never cleaned up in between — is the one a real
target reaches once ticket 01 has already landed and ticket 02 (this one) is new: an incremental,
per-Track migration, exactly what "no migration step" (ADR-0055) is supposed to make unremarkable.

Not deterministically checkable — pure skill process behavior (does the pass proceed normally, does it
choke on an unrecognized field or an old-style entry). Run via `fixtures/harness/run.sh
guardrails-track php-guardrails-old-schema --opencode`, same non-CI, local-only, advisory posture as
`safety-net-track`/`decision-gate-bypass`.

## Seeded state

`docs/refactoring/bookkeeping.md`: `## Safety Net` present and closed (`Open`/`Out-of-scope` both
empty — the Safety Net Track has already run to completion on this target), but `Fulfilled nodes` still
lists `composer`, `php-cs-fixer`, `phpunit`, `psr-4`, `phpstan-level-0`, and the `rector-*` family —
entries written before ticket 01 ever ran on this target, never cleared since (the new schema simply
stops reading or writing them for a Safety-Net-Track-scoped node; nothing goes back and removes the old
ones). **No `## Guardrails` heading anywhere in the file.** The project itself matches: the Safety Net
is genuinely fully resolved (same shape as `php-guardrails-open-blocks-rescan`'s own seeded state), but
`composer-audit`, `phpmd`, `coverage-floor`, `php-minimal-version`, `phpstan-level-6`,
`phpstan-deprecation-rules`, and `semgrep` are all still genuinely missing — real, still-open
Guardrails Track work exists here, this isn't a "nothing to do" fixture.

## Expected: `refactor-scan` pass

Run `/refactor-scan`. It should:

1. Read `bookkeeping.md` without erroring on `Fulfilled nodes` still carrying old-style entries for
   Safety-Net-Track-scoped nodes — nothing about reading them is invalid, they're simply never
   consulted for those nodes any more (the deterministic parser re-derives their live state directly
   from the repo either way).
2. Find no `## Guardrails` section, treat the Track as due (never run), and confirm `php-safety-net`
   is resolved (it is — the Safety Net closed already), so every Guardrails node is reachable.
3. Treat `composer-audit`, `phpmd`, `coverage-floor`, `php-minimal-version`, `phpstan-level-6` and
   above, `phpstan-deprecation-rules`, and `semgrep` as the Track's unresolved scope — all genuinely
   still missing — and record them as `Open` (below) rather than filing any of them.

## Expected: `refactor-learn`

Whichever candidate this pass actually carries through to completion (or, at minimum, the Track's own
scan completing) creates the `## Guardrails` section fresh — `Cadence: 60`, `Last scan: <today>`,
`Open` holding the complete Guardrails backlog in the script's order, blocked nodes included, no
issue numbers: `phpmd`, `coverage-floor`, `composer-audit`, `phpstan-level-6`, `phpstan-level-7`,
`phpstan-level-8`, `phpstan-level-9`, `phpstan-level-10`, `phpstan-deprecation-rules`,
`php-minimal-version`, `semgrep` (computed with `tooling_tree.py` and a seed marking every other
node fulfilled — see `php-guardrails-scan-fills-open`). The pre-existing `Fulfilled nodes`/`Pending
candidates` content, and `## Safety Net` itself, are left exactly as they were — this write never
touches, migrates, or removes any of it.

## The behavior this regression-tests

Without this rule, a target partway through adopting the Track-based schema — one Track migrated,
another not yet — would either error out on the coexistence, or need a one-time manual reconciliation
step before its next pass could run at all, both of which ADR-0055 explicitly rejects ("No migration
step").

## Verified

Confirmed live via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh guardrails-track
php-guardrails-old-schema --opencode` (`opencode/muse-spark-1.2-contributor-free`): the model
explicitly confirmed "no error, no migration," read `refactoring-bookkeeping.md`'s own "Old-schema
repos need no migration" rule, and treated the mid-migration state (`## Safety Net` present, `##
Guardrails` absent, `Fulfilled nodes` residue) as the ordinary, documented case. See the implementing
pull request's own report for the full transcript summary.
