# 55 — `_composer_audit_extra_gate` doesn't cascade through a rejected required ancestor either

**What to build:** `_composer_audit_extra_gate()` (`tooling_tree.py`) checks whether every *other*
leaf feeding `php-structural-scan` is resolved via `leaf in rejected` — the raw `_rejected_nodes()`
set — instead of `_is_effectively_rejected(leaf, tree, rejected)`, the cascading check ticket
53/ADR-0035 introduced so a `resolved`-gate leaf behind a rejected *required ancestor* (not itself
directly rejected) still counts as resolved. Fix it the same way ticket 53 fixed
`_resolved_gate_status()`: swap the raw membership check for `_is_effectively_rejected()`.

**Why:** Live reviewer-loop finding (`Art4/legacy-todo`, 2026-09-06 — this run's
`.scratch/legacy-todo-loop-observation/findings.md`, Round 1): the watched OpenCode agent's own scan
step noticed `next_candidates()`/`withheld_candidates()` both came back empty despite
`composer-audit` showing `fulfilled: false` with no blocking required-parent, investigated the
parser's own source, and correctly diagnosed the cause. Verified directly against `tooling_tree.py`
in this repo:

- `_composer_audit_extra_gate()` (line ~1094): `unresolved = [leaf for leaf in other_leaves if not
  (resolved_check.get(leaf, False) or leaf in rejected)]`.
- `_resolved_gate_status()` (line ~758, ticket 53's own fix): `... or _is_effectively_rejected(leaf,
  tree, rejected)`.
- On `Art4/legacy-todo`: `phpstan-level-6` is rejected (has an out-of-scope entry, per ticket 53's
  explicit design decision that *only* the directly-rejected node gets one). `phpstan-level-10` — a
  `php-structural-scan` leaf, closed beneath `phpstan-level-6` — has no out-of-scope entry of its own
  and isn't fulfilled, so it shows up in `_composer_audit_extra_gate`'s `unresolved` list, and
  `composer-audit` never satisfies its extra condition. Net effect: `composer-audit` never gets
  proposed, `php-structural-scan` never resolves, `structural-scan` never opens — the exact same
  "rejecting the level-6 node doesn't move structural-scan any closer to unlocking" gap ticket 53
  already fixed once, just via a second, separate gate function ticket 53's own patch never touched
  (that fix only wired `_is_effectively_rejected()` into `_resolved_gate_status()` and its two
  existing `recommended`-edge call sites — `_composer_audit_extra_gate()` wasn't a call site yet).

**Blocked by:** none.

**Priority:** high — directly re-blocks the same live goal ticket 53 was filed to unblock (reaching
`structural-scan`), on the same target repo, confirmed live.

**Status:** done

- [x] Fix confirmed mechanical: swapped `leaf in rejected` for `_is_effectively_rejected(leaf, tree,
  rejected)` in `_composer_audit_extra_gate()`'s `unresolved` computation — no other difference from
  `_resolved_gate_status()`'s own treatment needed; `composer-audit` is already excluded from
  `other_leaves` before this check runs, so no self-reference risk.
- [x] `roadmap()`'s simulation call site (passing `sim_fulfilled` instead of real `detected`) needed
  no separate change — it calls the same `_composer_audit_extra_gate()` function, so the fix applies
  there automatically.
- [x] New test added: `ComposerAuditGateTests.test_eligible_via_fallback_when_leaf_effectively_rejected_through_ancestor`
  — rejects `phpstan-level-6` only (no entry for `phpstan-level-10`), confirms `phpstan-level-10`
  stays unfulfilled but `composer-audit` still becomes proposable via the fallback. 255/255 tests
  pass (was 254; ticket 54 landed one more since ticket 53).
- [x] Extended ADR-0035's own Consequences section rather than writing a new ADR — this is the same
  decision applied to a call site that existed all along but wasn't wired up yet, not a new design
  question.

## Comments

> **2026-09-06:** Filed from the `Art4/legacy-todo` reviewer-loop findings log (this run's Round 1) —
> the watched OpenCode agent's own pass diagnosed this correctly and reported it as a "Next" note
> rather than attempting to fix an external skill install itself (correct: it doesn't own this repo).
> Verified against `tooling_tree.py` source directly before filing. Same treatment as tickets 48–53:
> quick grill (likely short, given how closely this mirrors ticket 53's own already-decided pattern),
> then implement on its own branch/PR.

> **2026-09-06 (later):** Human opted to skip a full `/grill-me` session — fix was mechanical enough
> to implement directly (confirmed by reading the source first, not assumed). Implemented on branch
> `tickets/55-composer-audit-gate-cascade`: one-line fix in `_composer_audit_extra_gate()`, one new
> test, ADR-0035 extended (not a new ADR). 255/255 tests pass, validator clean (same 5 pre-existing
> warnings — had to fix one self-inflicted validator error first: the fix's own docstring initially
> mentioned "ticket 53"/"ticket 55"/"ADR-0035" directly, which `validate_skills.py` correctly flagged
> as internal maintainer references leaking into shipped skill prose; reworded to state the rule
> inline instead).
