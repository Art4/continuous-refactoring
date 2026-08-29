# 33 — Rector introduced ahead of its recommended `php-cs-fixer` parent

**What to build:** Change what a `recommended` edge means and enforces, tree-wide: a node with one or more `recommended` parents is proposed only once **every** one of those parents has reached a **decided** state — fulfilled, or rejected (directly, or transitively via a `required`-chain cascade: e.g. `phpstan-level-1` rejected closes `phpstan-level-2`/`-3` via their own `required` edges, which counts as `phpstan-level-3` decided for `rector-type-coverage`'s recommended edge too). Unlike a `required` edge, a rejected `recommended` parent still releases the child instead of closing it. A parent not yet reached at all (still blocked by its own required edges) counts as undecided too — the gate waits for an actual decision, not just a shared pass where both happen to be proposable. A node with multiple recommended parents (`rector-type-coverage`: `php-cs-fixer` and `phpstan-level-3`) waits on all of them independently.

This is a scan-level gate, not a `refactor-prioritize` ranking factor — a withheld node is excluded from the proposal set outright (`refactor-scan`'s `next`/`withheld` split), never merely ranked lower. Also lifts `refactor-scan`'s five-node proposal cap entirely (`next` is never capped) — already independently overdue, since more than five nodes can be genuinely unblocked at once without this change (e.g. `composer`'s required children plus `phpstan-level-1` already reach six on a fresh target).

**Why:** Observed on the same run as ticket 32 (`Art4/legacy-todo`): Rector's dead-code suite was introduced (`rector-dead-code`) while `php-cs-fixer` had never even been proposed yet. Not a `required`-edge violation — Rector's only required parent, `phpstan-level-0-baseline`, was fulfilled — but it undermines the documented purpose of the `php-cs-fixer → rector-dead-code` recommended edge: `skills/refactor-scan/references/php-tooling-tree.md`'s own `php-cs-fixer` node prose says its purpose is "automated code style so later Rector output lands styled." Rector's rewrites landed unstyled as a direct, foreseeable consequence.

**Blocked by:** 32 (done) — its Skip-streak fix reduces how often this specific instance occurs, since `php-cs-fixer` is itself a `required` child of `composer` and so already benefits from Skip-streak's anti-starvation pressure — but doesn't eliminate the underlying gap: a target that rejects `php-cs-fixer` outright as out-of-scope would still hit it, since Skip-streak has nothing left to boost once a node is rejected. Decided independently, per a `/grill-me` session — see Comments.

**Priority:** high

**Status:** done

- [x] `CONTEXT.md`: redefine **Recommended edge** to gate on decision (fulfilled or rejected) rather than never blocking.
- [x] `skills/refactor-scan/references/tooling_tree.py`: implement the decided-gate (`_is_effectively_rejected`, `_is_decided`, `_undecided_recommended_parents`) in `next_candidates()`; add `withheld_candidates()` for the surfaced "waiting on" set; lift `next_candidates()`'s five-node default cap (`limit: int | None = None`, unbounded unless a caller opts in); `detect_and_roadmap()` exposes the new `withheld` key. `roadmap()`'s own forward-simulated recommended-parent outlook is deliberately left as-is (a separate, already-documented speculative lookahead, not what `refactor-scan` reads).
- [x] `skills/refactor-scan/references/tree-walk-prompt.md`: mirror the same gate for the manual/LLM fallback (walk the recommended parent's own required chain looking for a decided-rejection, not just a fulfilment); `{N}=all` for the proposal step, replacing the old `{N}=5`.
- [x] `skills/refactor-scan/SKILL.md`: drop the `--steps 5` cap on the real `next_candidates()` call; Output step names every withheld node and which parent(s) it's waiting on, alongside the (now uncapped) proposal set.
- [x] `skills/refactor-prioritize/SKILL.md`: reworded step 1's "(not five fresh proposals)" phrasing, since the proposal count is no longer fixed.
- [x] `skills/refactor-scan/references/php-tooling-tree.md`: updated `rector-dead-code` and `rector-type-coverage` node prose — no longer "stated in the outlook when unfulfilled or rejected", now an actual proposability gate.
- [x] Swept every other live "up to five" description of `refactor-scan`'s proposal count and reworded it: `AGENTS.md`, `README.md`, `CONTEXT.md` (two places), `refactor-scan/SKILL.md`'s frontmatter `description`, `skills/continuous-refactoring/SKILL.md`. `docs/adr/0010-orchestrator-explicit-data-flow.md`'s own "up to five" is left untouched as a historical record, with a pointer from `docs/adr/0016` instead.
- [x] `docs/adr/0016-recommended-edges-gate-until-decided.md`: written, explicitly revising `docs/adr/0007-required-recommended-edges.md`.
- [x] `scripts/test_tooling_tree.py`: `RecommendedGateTests` (7 new tests) covering withhold/release/fulfilled/rejected/cascade/multi-parent/uncapped behavior. Full suite and `validate_skills.py` both pass clean.
- [x] **Correction (caught after the PR was opened):** `tooling_tree.py`'s own docstrings/comments cited `ADR-0016` eight times — a real violation of "no ADR citations in anything shipped under `skills/`", not just a documentation nicety, since the `.py` file ships and runs same as any `.md` reference. `scripts/validate_skills.py`'s `adr_issues()` check had never actually caught this: it only globbed `references/*.md` (top-level, `.md` only), missing every non-`.md` reference file and every nested reference subdirectory (e.g. `php-tooling-tree/composer.md`) tree-wide, not just in this diff. Fixed both: reworded all eight citations inline (no ADR number), and widened the validator's scan to `references/**/*` (recursive, any file type, skipping `__pycache__`/`.pyc`). Added `ReferencesDirTests` coverage for a non-`.md` reference file, a nested reference subdirectory, and a `__pycache__` file being correctly ignored (117 tests now, up from 114). `python3 -m unittest discover -s scripts -p 'test_*.py'` and `python3 scripts/validate_skills.py .` both pass clean.
- [x] **Second correction:** same category of gap, different target — `.scratch/` (the suite's own internal issue tracker) can be cited from skill prose the same way an ADR number could, and one pre-existing instance already was: `php-tooling-tree.md`'s `composer-audit` node pointed at `.scratch/php-tooling-tree/issues/10-dependency-vulnerability-scan.md` (unrelated to this ticket's own diff, a pre-existing violation the widened scan surfaced). Added `scratch_ref_issues()` to `validate_skills.py`, wired into both scan sites (`SKILL.md` body and every `references/**` file) alongside `adr_issues()`; reworded the one real violation to state the fact inline instead of citing the ticket path. New tests: `ScratchRefTests` (4 unit tests) plus one `ReferencesDirTests` integration case (122 tests now, up from 117). Full suite and `validate_skills.py` both pass clean.

## Comments

> **2026-08-29:** Filed from the legacy-todo reviewer-loop findings log
> (`.scratch/legacy-todo-loop-observation/findings.md`, same finding as ticket 32) after the user asked
> for it to be turned into a real ticket, kept separate from 32 since it's a distinct design question
> (recommended-edge ordering) even if 32's fix happens to resolve this instance of it.

> **2026-08-29 (later):** Design settled via a `/grill-me` session. Rejected both options originally
> posed in the checklist above (a `refactor-prioritize` ranking-weight nudge, and an outlook-note-only
> response) in favor of a harder mechanism: a `recommended` edge now gates proposability until every
> parent is *decided* (fulfilled or rejected), symmetric with a `required` edge except for what a
> rejection does to the child. Key corrections made during grilling: the trigger is "decided", not
> "simultaneously proposable this pass" (a recommended parent several required-edge hops away still
> withholds the child); a `required`-chain cascade rejection of a recommended parent counts as that
> parent being decided too; the five-node proposal cap is unrelated to and untouched by
> `refactor-scan`'s separate "five or more open `refactor:candidate` issues" backlog-stop precondition,
> which was spun out as its own ticket (36) rather than folded in here. Captured to-spec and implemented
> in the same session — see the checklist above and its closing note.

> **2026-08-29 (later still):** Implemented via `/implement`. Changed `CONTEXT.md`,
> `skills/refactor-scan/references/tooling_tree.py`, `skills/refactor-scan/references/tree-walk-prompt.md`,
> `skills/refactor-scan/SKILL.md`, `skills/refactor-prioritize/SKILL.md`,
> `skills/refactor-scan/references/php-tooling-tree.md`, `scripts/test_tooling_tree.py`, and added
> `docs/adr/0016-recommended-edges-gate-until-decided.md`. `python3 -m unittest discover -s scripts -p
> 'test_*.py'` (114 tests, 7 new) and `python3 scripts/validate_skills.py .` both pass clean.
