# 51 — PHPStan level-chain gets permanently stuck: baseline-shrink work is never proposed

**What to build:** `phpstan.md`'s own Stop-conditions prose for `phpstan-level-1`–`10` already states
the intended behavior: *"Baseline is non-empty → do not propose the next level; the loop proposes
shrinking work (candidates flagged by the fulfilled tooling, or Rector steps that reduce baseline
entries) until the baseline becomes empty."* That mechanism does not exist anywhere in the suite —
confirmed by grep: zero mentions of "baseline" in any of `refactor-scan`/`refactor-prioritize`/
`refactor-design`/`refactor-implement`'s `SKILL.md` files, and `tooling_tree.py`'s
`next_candidates()`/`roadmap()` never turn a non-empty baseline into a candidate; they only ever
produce the boolean tree nodes. A level that's fulfilled with a non-empty baseline therefore never
gets any follow-up work proposed for it — the chain is stuck forever unless a human intervenes by
hand.

Build the actual mechanism: some way for a non-empty baseline on an already-fulfilled
`phpstan-level-N` node to surface as real, proposable candidate work (not just a silent stop
condition), sized/shaped consistently with how every other node's MR scope stays small and bounded.

**Why:** Live reviewer-loop finding (`Art4/legacy-todo`, 2026-09-04 —
`.scratch/legacy-todo-loop-observation/findings.md`, post-stop cleanup section): PHPStan Level 1 is
fulfilled with a 34-finding baseline across 9 files (all `variable.undefined`, from legacy
include-based global sharing — `$db`, `$site_name`, `$cfg`, `$dbFile`, `$version`). Every scan pass
since correctly refuses to propose Level 2 (blocked by the non-empty baseline, per spec) but also
never proposes anything to shrink Level 1's own baseline — the watched agent's most recent pass (PR
#122) could only do bookkeeping housekeeping, nothing else. This also transitively blocks
`php-structural-scan` (requires `phpstan-level-10` resolved) — so on any repo that adopts PHPStan at
all, "real" structural work through `structural-scan` can never start unless every baseline along
the way happens to empty itself by accident.

**Blocked by:** none.

**Priority:** medium — not a correctness bug (nothing incorrect lands), but a real stagnation trap:
without this, PHPStan adoption on a legacy codebase permanently caps out at whatever level it started
at, and the entire rest of the tooling tree downstream of `php-structural-scan` becomes unreachable.

**Status:** done

- [x] Representation: no new `tooling_tree.py` candidate shape — `detect_nodes()` already exposes
  `details.baseline_empty` for every `phpstan-level-N`. `refactor-scan` step 4b reads that directly
  and proposes "PHPStan Level N — baseline shrink" generically, the same shape `structural-scan`
  itself is proposed in; `refactor-design`'s new `phpstan-baseline-shrink.md` does the actual
  baseline read and picks a concrete group once chosen.
- [x] Grouping: by **root cause** (message pattern + identifier, not by file — a root cause commonly
  spans several files, one fix approach usually covers the whole group).
- [x] Fix-design guidance: ordinary judgment, same as any other candidate — no PHPStan-identifier-
  specific fix recipes.
- [x] PHPStan-only for now; Psalm's own suppression mechanism is a separate future ticket.
- [x] Verification bar: reduction suffices per MR; the chosen group stays the active target across
  passes until it's fully empty (continuity via the ordinary open-issue-resume mechanics, no new
  tracking field). One commit per file fixed (or otherwise-distinct reduction), even within one MR.
- [x] No `next_candidates()`/`roadmap()` shape change needed. `roadmap()`'s existing half-finished
  phpstan-level simulation comment code cleaned up for clarity (it was never live-authoritative).

## Comments

> **2026-09-04:** Filed from the `Art4/legacy-todo` reviewer-loop findings log, after the human
> noticed the watched agent opening a bookkeeping-only PR (#122) instead of any PHPStan Level 1
> baseline work and asked what could be done about it. Root cause investigated directly (read-only)
> before filing: confirmed `phpstan.md`'s own documented intent for this exact situation was simply
> never implemented, not a bug in #122 or in the watched agent's behavior — PR #122 itself is correct
> and was merged separately. Same treatment as tickets 48/49/50: grill it, then implement on its own
> branch/PR.

> **2026-09-04 (later):** Design settled via a `/grill-me` session (in German), two rounds. Key
> redirect from the round-1 proposal (a mechanical, `tooling_tree.py`-generated per-file candidate):
> the human wanted this to be a single skill's judgment call — analysis, grouping, and (partial)
> fixing together — not a Python-mechanical enumeration. Landed on `refactor-design` owning the
> grouping (by root cause, not file — matches how `refactor-design` already owns MR-scope decisions
> everywhere else), mirroring the existing `structural-scan`/`php-structural-scan` pattern
> (`refactor-scan` names the open gate generically, `refactor-design` walks the specifics for the
> candidate actually chosen). Also settled: reduction suffices per MR but the group stays active
> until empty, and one commit per file fixed even within a single MR. Implemented on branch
> `tickets/51-phpstan-baseline-shrink-work`: new `refactor-scan` step 4b, new
> `skills/refactor-design/references/phpstan-baseline-shrink.md`, `refactor-design`/
> `refactor-implement` `SKILL.md` updates (steps 1/2/3/5 plus Completion criterion), `phpstan.md`'s
> Stop-conditions bullet now points at the real mechanism instead of an unfulfilled promise,
> `roadmap()`'s dead comment code cleaned up, one new regression test confirming the
> `details.baseline_empty` contract `refactor-scan` step 4b depends on. `python3 -m unittest
> discover -s scripts -p 'test_*.py'` (251/251) and `scripts/validate_skills.py` (same 5
> pre-existing advisory warnings) both green; all 8 fixtures regenerated and confirmed unchanged
> (no behavior change, comment-only cleanup in `tooling_tree.py`). New ADR-0033. Not yet tested live
> against `Art4/legacy-todo` — both watched-agent loops are currently stopped.
