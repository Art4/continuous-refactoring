# 53 — Rejecting a required-parent node doesn't cascade-resolve a `resolved`-gate leaf beneath it

**What to build:** `php-structural-scan`'s (and any other `resolved`-gated node's) own gate check
treats each of its leaves individually as `fulfilled` or `rejected` — but a leaf that's unreachable
only because an *ancestor* in its own required-parent chain was rejected currently counts as neither:
it sits in `unresolved` forever, since `_rejected_nodes()` only recognizes a node with its own
out-of-scope entry. `next_candidates()`'s ordinary required-parent gating already treats "ancestor
rejected" as "permanently closed" for proposability purposes — the `resolved`-gate check needs the
same treatment, so a closed-by-ancestor leaf counts as resolved too, without needing its own separate
out-of-scope entry.

**Why:** Live reviewer-loop finding (`Art4/legacy-todo`, 2026-09-05 —
`.scratch/legacy-todo-loop-observation/findings.md`, Round 7): the maintainer rejected
`phpstan-level-6` specifically to reach `structural-scan` sooner. Confirmed via `detect_nodes()`
against real `main`: `php-structural-scan`'s own entry lists `phpstan-level-6` correctly under
`rejected`, but `phpstan-level-10` — the actual leaf that node's gate needs resolved — still sits
under `unresolved`, because it never got its own out-of-scope entry (and per the maintainer's
explicit instruction, never should: see below). Net effect: rejecting level 6 does not move
`structural-scan` any closer to unlocking, directly undercutting the reason for rejecting it at all.

**Blocked by:** none.

**Priority:** medium-high — directly blocks the stated goal of a live, ongoing run (reach
`structural-scan` sooner), and is a correctness gap in the tree's own documented "rejecting a required
parent closes everything beneath it" principle (`php-tooling-tree.md`'s *Nodes* preamble) — that
principle already holds for `next_candidates()`; this ticket is making the separate `resolved`-gate
check consistent with it, not inventing new behavior.

**Status:** done

- [x] Confirmed design decision (maintainer, 2026-09-05): only the actually-rejected node
  (`phpstan-level-6`) gets an out-of-scope entry — never write one for every node down the chain.
  The gate logic itself was fixed instead.
- [x] Fix reuses an existing function rather than a new helper: `_is_effectively_rejected()` already
  walked a node's `required_parents` chain recursively for `recommended`-edge gating — extended it
  with `required-any` handling (it previously only handled plain `required`) and wired it into
  `_resolved_gate_status()`, replacing the bare `leaf in rejected` check. Generic over
  `structural-scan`/`php-structural-scan`/any future resolved-gated node, no per-level special-casing.
- [x] `required-any` handling: only closes once *every* option in the group is rejected — mirrors
  `_is_permanently_gated()`'s identical pattern for its own, unrelated gate condition. Verified both
  directions with `rector-php-set`'s real `required-any(phpstan-level-0, psalm)` gate: rejecting just
  one option leaves it open, rejecting both closes it.
- [x] No distinction surfaced between "directly rejected" and "closed via ancestor" — both simply
  count as resolved, per the grilling decision.
- [x] No existing test asserted the buggy behavior — genuinely untested territory before this ticket;
  three new tests added (ancestor-cascade integration test via `php-structural-scan`, plus two unit
  tests directly against `_is_effectively_rejected` for the required-any nuance).

## Comments

> **2026-09-05:** Filed from the `Art4/legacy-todo` reviewer-loop findings log (Round 7's finding,
> Round 8 confirming the design decision) and the `rejected-required-parent-should-cascade-resolve-gate`
> memory. Same treatment as tickets 48–52: grill it, then implement on its own branch/PR.

> **2026-09-05 (later):** Design settled via a `/grill-me` session (in German), one round (2
> questions: required-any handling, whether to surface a distinction — both answered "as
> recommended"). Mid-fact-finding, discovered `_is_effectively_rejected()` already existed and did
> almost exactly what was needed (built for `recommended`-edge gating) — reused and extended it
> instead of writing a parallel implementation, smaller change than the ticket originally
> anticipated. Implemented on branch `tickets/53-cascade-resolve-rejected-ancestor`: extended
> `_is_effectively_rejected()` with required-any handling, wired into `_resolved_gate_status()`, new
> ADR-0035, 3 new tests (254/254 total). Validator clean (same 5 pre-existing warnings); all 8
> fixtures regenerated and confirmed unchanged (no fixture exercises a rejected-ancestor case).
