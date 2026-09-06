# 56 — Psalm-equivalence for `phpstan-level-0` ignores the documented Co-presence rule

**What to build:** `detect_nodes()`'s `psalm_fulfils_p0` computation (`tooling_tree.py`) treated
Psalm's own fulfilment as sufficient to mark `phpstan-level-0` fulfilled *and* every
`phpstan-level-1..10` as `"not applicable: psalm fulfils p0"`, unconditionally — regardless of
whether PHPStan is *also* genuinely adopted. `phpstan.md`/`psalm.md` both document a **Co-presence**
rule: "if both analysers are present, PHPStan is the authoritative check for this tree; Psalm
fulfilment is considered superseded." The code never implemented that half of the rule.

**Why:** Live reviewer-loop finding (`Art4/legacy-todo`, 2026-09-06 —
`.scratch/legacy-todo-loop-observation/findings.md`, Round 5), already anticipated but never fixed:
PR #151's own delivery comment on that repo flagged this exact gap back on 2026-09-05 ("scanner
detection gap... should be fixed in the skill install"), and Round 4's own reviewer pass reasoned
around it by hand rather than trusting the parser's output. This round's pass didn't apply that same
care during its bookkeeping fold-in: `docs/refactoring/bookkeeping.md`'s `Fulfilled nodes` field lost
five genuinely-fulfilled entries (`phpstan-level-1` through `-5`) the moment a pass with parser access
ran `refactor-learn`'s cache-overwrite against a repo that has both PHPStan (configured, levelled,
baseline-backed) and Psalm (adopted for `psalm-taint-analysis`) — exactly the co-presence scenario
the docs already named as needing PHPStan to stay authoritative.

**Blocked by:** none.

**Priority:** medium-high — silently corrupts `Fulfilled nodes` on any target that layers
`psalm-taint-analysis` onto an existing PHPStan setup (a documented, expected adoption path, not an
edge case), and a future pass reading the cache at face value could wrongly re-propose already-earned
PHPStan levels.

**Status:** done

- [x] Root cause confirmed: `psalm_fulfils_p0 = psalm_fulfilled` (unconditional) at the single call
  site inside `detect_nodes()` — not a duplicated-gate-function situation like ticket 55; one place
  to fix.
- [x] Fix: added a `phpstan_genuinely_adopted` check (`has_phpstan_dep_or_ephemeral and phpstan_level
  is not None` — the same "real dependency, actually configured" bar `phpstan-level-0`'s own
  non-Psalm branches already use) and required it to be *false* for the Psalm-equivalence path to
  apply: `psalm_fulfils_p0 = psalm_fulfilled and not phpstan_genuinely_adopted`. Reordered the
  `ephemeral_ci_dep`/`has_phpstan_dep_or_ephemeral` computation earlier in the function since this
  check now needs it before it previously did.
- [x] `psalm` node's own `fulfilled` flag is untouched by this fix — per `psalm.md`'s own text it
  correctly "still shows fulfilled, harmlessly" regardless of co-presence; only the *equivalence*
  reading (whether Psalm's fulfilment substitutes for PHPStan's) changed.
- [x] `roadmap()`/`directly_unblocked_children()` needed no separate fix — both read `detect_nodes()`'s
  output directly rather than re-deriving the equivalence themselves (unlike ticket 55's
  `_composer_audit_extra_gate`, which had a genuinely separate, duplicated gate condition).
- [x] Two new tests: co-presence (both genuinely adopted → PHPStan authoritative, level-5 fulfilled
  from real config, not from equivalence) and a negative case (PHPStan dep present but no level
  configured → still not "genuinely adopted," Psalm-equivalence still applies, matching every
  Psalm-only fixture already in the suite). 257/257 total. Validator clean (same 5 pre-existing
  warnings).

## Comments

> **2026-09-06:** Filed from the `Art4/legacy-todo` reviewer-loop findings log (Round 5) — a
> previously-known, previously-unfixed gap (flagged on that repo's own PR #151 the day before)
> finally causing a real bookkeeping corruption once a pass's fold-in didn't manually correct for it.
> Fixed directly (small, well-understood, single-call-site fix), same treatment as ticket 55.
