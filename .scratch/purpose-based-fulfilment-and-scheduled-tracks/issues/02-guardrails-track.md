# 02: Guardrails Track

**What to build:** The same mechanism ticket 01 built for the Safety Net Track, applied to the
Guardrails node subset (the nodes gated on the Safety Net closing) — its own `Guardrails` section in
`bookkeeping.md` (`Cadence` default 60 days, `Last scan`, `Open`, `Out-of-scope`), scanned and written
back through the same agent-judged-Purpose and `refactor-learn` mechanics ticket 01 already established,
proving the approach generalizes to a second node set without new plumbing.

**Blocked by:** 01

**Status:** done

- [x] Guardrails nodes are recognized via agent judgement against their own Purpose statement, the same
      way Safety Net nodes are.
- [x] `bookkeeping.md` gains a `Guardrails` section (`Cadence`, `Last scan`, `Open`, `Out-of-scope`),
      independent of the `Safety Net` section.
- [x] Guardrails nodes are only ever proposed once the Safety Net has closed (existing gating semantics
      unchanged).
- [x] Merge/rejection write-back for Guardrails behaves identically to the Safety Net Track's own —
      reusing ticket 01's mechanism, not a reimplementation.

## Comments

Implemented on branch `tickets/02-guardrails-track`, stacked on `tickets/01-safety-net-track`.

- New `skills/refactor-scan/references/guardrails-track.md` and
  `skills/refactor-learn/references/guardrails-write.md` mirror `safety-net-track.md`/
  `safety-net-write.md` structurally, scoped to the seven nodes required on
  `structural-scan`/`php-safety-net` themselves (`composer-audit`, `phpmd`, `coverage-floor`,
  `php-minimal-version`, `phpstan-level-6` and above, `phpstan-deprecation-rules`, `semgrep`) — the
  scope boundary ticket 01's own Safety Net Scope section already resolved, confirmed against
  `php-tooling-tree.md`'s current edges, not re-litigated.
- `refactoring-bookkeeping.md` gains a `## Guardrails` section (`Cadence: 60`) documented in parallel
  to `## Safety Net`; `refactor-scan`/`refactor-learn`'s `SKILL.md`s gained minimal pointer bullets at
  the same steps ticket 01 wired, not a restructuring.
- Five new fixtures (`fixtures/php/php-guardrails-*`) and a `guardrails-track` harness tier, adapted
  from the five Safety Net fixture types (purpose-recognition, open-blocks-rescan, first-run,
  rejection-symmetry, old-schema) — `old-schema` deliberately adapted rather than mirrored 1:1: a
  target still fully on the pre-ADR-0055 shape would never reach the Guardrails Track in the same pass
  (Safety Net outranks it and is always at least as overdue), so this fixture instead seeds a
  mid-migration target (`## Safety Net` already closed, `## Guardrails` never run, old-style
  `Fulfilled nodes` residue left untouched) — the scenario a real target actually reaches once ticket
  01 has shipped and this ticket is new.
- `purpose-recognition`'s judgement case: a target whose CI gates on `composer audit` only indirectly,
  via a `composer.json` script (`composer run security-check`), so `tooling_tree.py`'s literal
  CI-text match misses it even though the check is genuinely real — chosen because none of the seven
  Guardrails nodes has as direct a named-tool equivalent as Pint/PHP-CS-Fixer did for Safety Net's own
  fixture; this is the same class of purpose-judgement gap, just surfacing through an indirection
  instead of a rebrand.
- All 339 `python3 -m unittest discover -s scripts -p 'test_*.py'` pass;
  `python3 scripts/validate_skills.py .` is clean (pre-existing advisory warnings only — one new
  `VOCAB_ALLOW` entry added for `("continuous-refactoring", "floor")`, a false positive from the
  `coverage-floor` node slug appearing in the new `## Guardrails` doc section).
- All five fixtures verified live via `fixtures/harness/run.sh guardrails-track <fixture> --opencode`
  (`opencode/muse-spark-1.2-contributor-free`, `OPENCODE_TIMEOUT=280`) — exceeding the two-fixture
  minimum. One real bug surfaced and fixed along the way: `refactor-learn/SKILL.md`'s own closing-call
  precondition (pre-existing, shared with the Safety Net Track) didn't list "a Track's scan ran with
  nothing to propose" as a precondition-satisfying event, so a literal reading stopped the closing call
  before it ever reached `guardrails-write.md`'s "write `Last scan` regardless" rule — fixed with a
  narrowly-scoped third precondition clause authorizing only that one write. Two harness-check
  robustness fixes also landed: a bare `grep -qi "RESCANNED"` false-failed on the word appearing in the
  model's own correct reasoning prose (fixed to a line-anchored match), and the `first-run` check now
  also looks across local git branches, since a correct run in a no-remote sandbox leaves its
  bookkeeping write on a dedicated branch rather than the working tree.
- PR: (link recorded below once opened).
