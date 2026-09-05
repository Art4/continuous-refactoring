# 54 — A stated refactoring goal (e.g. "convert to OOP") should steer `structural-scan` candidates

**What to build:** A new, generic, hand-editable config field — sibling to `Focus areas` in the
Refactoring Notes' `bookkeeping.md` — that states the *shape* structural work should converge toward,
not *where* to look. Consumed by `refactor-design`'s `structural-candidate.md` (finding/grilling a
`structural-scan` candidate) and possibly `refactor-prioritize`'s ranking table, so a human-stated
goal like "convert this procedural PHP app to OOP" actually biases which candidates get proposed and
how they're designed, rather than sitting inert.

- Working name: `Refactoring goal` (bikeshed during grilling — could also be `Structural direction`,
  `Target architecture`, etc.).
- Stays **paradigm-neutral in every shared skill file** — never hardcode "OOP" anywhere in
  `skills/`. The field is arbitrary human-stated free text, exactly like `Focus areas` already holds
  target-repo-specific text (`order intake, billing`) in a generic field. A different target repo
  could set "hexagonal architecture" or "extract pure functions" instead.
- Same treatment as `Focus areas`: **not** asked during the `loop-config` interview
  (`skills/continuous-refactoring/references/loop-config-interview.md:145-148` already excludes
  `Focus areas` for the same reason — free-form, no filesystem signal to recommend from, a natural
  addition for a later, focused pass) — hand-editable any time instead.

**Why:** Raised by the user directly (2026-09-05): the continuous-refactoring skill suite should be
able to carry a general goal like "turn this legacy app into an OOP application," and there's
currently nowhere for that to live. Investigated live against the current design:

- Not a tooling-tree node — every existing node (`skills/refactor-scan/references/tooling-tree.md`,
  the PHP tree) has a clean binary Fulfilment check (tool installed, baseline empty, etc.). "The app
  is now OOP" has no such clean check and would never reliably resolve `fulfilled`, unlike e.g.
  PHPStan-level nodes (empty baseline is unambiguous).
- Not the existing `Focus areas` field either — that answers **where** a scan should look first
  (`skills/continuous-refactoring/references/refactoring-bookkeeping.md:41`), not **what shape** the
  result should take. Conflating the two would blur two currently very precisely-named concepts in a
  suite that's otherwise careful about its vocabulary (`/codebase-design`'s module/interface/depth/
  seam/leverage/locality terms, kept deliberately paradigm-neutral).
- The actual point of leverage is `structural-scan`'s own candidate-finding procedure
  (`skills/refactor-design/references/structural-candidate.md`). Step 2 already says *"Decide where
  to look before you look: the user named a direction (module, subsystem, hot spot) → take it."* —
  that's the existing hook for a *location* override; there's no equivalent hook today for a
  *direction/shape* override.

**Blocked by:** none.

**Priority:** medium — no live bug forcing urgency, but it's a real gap the user wants filled as a
general suite capability (not just for `Art4/legacy-todo`).

**Status:** done

- [x] Field name: `Refactoring goal`.
- [x] Free-text (not structured) — consistent with `Focus areas`, and confirmed during grilling that
  `bookkeeping.md`'s fields are never programmatically parsed by `tooling_tree.py`/`scripts/` today,
  so a structured field would be the first to need real parsing for no expressed need.
- [x] Global per target repo, not scoped per focus area.
- [x] Consulted at both `structural-candidate.md` step 2 (added friction-signal lens) and step 4 (new
  grill branch, "against the stated goal").
- [x] No new `refactor-prioritize` ranking factor — scope stays inside `structural-candidate.md`;
  `refactor-prioritize` never ranks between individual structural candidates in the first place.
- [x] Unset → today's behaviour, unchanged; stated explicitly in both consuming steps.
- [x] No progress reflection — purely manual, like `Focus areas`; `refactor-learn` never writes it.
- [x] No interaction with ticket 38 (`housekeeping`) or ticket 35 (`php-minimal-version`) — different
  mechanism (tooling-tree fulfilment vs. structural-candidate search), confirmed by inspection.
- [x] ADR written: `docs/adr/0036-refactoring-goal-field-steers-structural-candidates.md`.
- [x] Implemented on branch `tickets/54-refactoring-goal-field`: `refactoring-bookkeeping.md` (new
  field, table row, Structure example, Rules section), `loop-config-interview.md` (added to the
  "not asked here" note), `structural-candidate.md` (steps 2 and 4), new ADR-0036. No code/test
  changes — the field is pure prose, unparsed by `tooling_tree.py`, matching `Focus areas`.

## Comments

> **2026-09-05:** Filed at the user's request after they asked where a general "convert to OOP"
> refactoring goal should live in the skill suite. Investigated live (this session, read-only) against
> the current tooling-tree/structural-scan/structural-candidate design before filing — see *Why* above
> for the reasoning against a tooling-tree node or reusing `Focus areas` as-is. Same treatment as
> tickets 48–53: grill it (`/grill-me`), then implement on its own branch/PR once settled.

> **2026-09-05 (later):** Design settled via a `/grill-me` session (in German), two rounds (8
> questions total, every answer "as recommended" except two — the field name and the "both steps"
> consumption point, also both settled quickly). Implemented on branch
> `tickets/54-refactoring-goal-field`: `Refactoring goal` field added to `refactoring-bookkeeping.md`
> (Structure example, field table, Rules section) and `loop-config-interview.md`'s "not asked here"
> note; `structural-candidate.md` updated at steps 2 and 4; new ADR-0036. Pure documentation/skill-
> instruction change — no `tooling_tree.py` or test changes needed, since `bookkeeping.md`'s fields
> were confirmed never programmatically parsed. Validator and test suite run clean before opening the
> PR (see the PR itself for the exact numbers).
