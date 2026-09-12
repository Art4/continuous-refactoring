# 01 — Abolish suite MR stacking; always branch parallel off the default branch

**What to build:** Fully reverse ADR-0015 ("suite merge requests always stack"). Every suite branch — bookkeeping, tooling-tree candidate, structural candidate, `loop-config`, anything this suite opens — always branches directly off the default branch, never off another still-open suite branch. No exceptions by case (sequential same-candidate stacking and parallel different-candidate stacking are both abolished alike).

**Why now, not before:** ADR-0015 traded a real problem (two parallel branches independently writing `docs/refactoring/bookkeeping.md`, causing repeated merge conflicts) for a different, recurring cost: a stacked PR gets silently auto-closed by the forge whenever its base branch is deleted after merging — GitHub gives no warning, just closes it. Observed twice, live, in the same target (`Art4/legacy-todo`), by the human reviewer, not the watched agent (which stacks correctly per the current rule):

- PR #244 (stacked on #243) — auto-closed when #243 merged with its branch deleted. Re-opened as #245.
- PR #264 (stacked on #261) — the identical failure, weeks later, despite the first incident being known. Re-opened as #265.

Investigated (this same conversation, no code changes) before this ticket: the two incidents have different root causes — #243→#244 was the same candidate (#240) in two sequential steps (a bookkeeping early-call branch, then the candidate's own implementation branch), no real concurrency risk at all; #261→#264 was two genuinely independent candidates (#259 and #262), the second correctly stacking on the first per ADR-0015's own rule — exactly the scenario the rule was designed to protect. In both cases the actual damage came from the auto-close mechanism, never from a real bookkeeping merge conflict, which never materialized either time. The theoretical protection ADR-0015 provides has never once been needed in practice; the cost it introduces has now hit twice.

## Decisions (grilled, `/grill-with-docs`)

1. **Abolish uniformly**, not case-by-case — a rule that stacks only in some cases needs the agent (or the human reviewer) to correctly identify which case applies every time, itself a new failure surface. Every suite branch always branches off the default branch from now on.
2. **No replacement mechanism for the original conflict risk.** Two suite branches independently changing `bookkeeping.md` at once is rare in practice (the existing, independent "fewer than two suite MRs open" cap already limits how much is ever concurrently in flight) and, if it happens, is an ordinary git merge conflict — visible, resolvable by rebase, no data loss. Not worth a structural mechanism (e.g. per-field files) to prevent something this cheap to resolve when it occurs.
3. **The "fewer than two suite MRs open at once" cap is unrelated and stays exactly as it is** — a capacity/focus limit, not a branching-topology decision.
4. **New, independent safety net in the reviewer-loop playbook** (`docs/playbooks/reviewer-loop.md`, not part of the continuous-refactoring suite's own skills — this is the human/AI reviewer's own procedure): before deleting any merged branch, explicitly check whether an open PR bases on it; if one does, retarget it (or leave the branch undeleted) before deleting. Applies regardless of this ticket's own outcome — a manually-stacked branch, or any future re-introduction of stacking, still needs this guard.
5. **Unaffected by this change:**
   - ADR-0028 (native-tracker in-flight bookkeeping rides the candidate's own branch) — not a stacking case at all; it's an extra commit on the *same*, already-checked-out candidate branch, never a second branch basing on a first.
   - ADR-0023 (never delete a branch as the only record a candidate was closed) — its general rule (land the abandonment record before deleting a branch with an unmerged bookkeeping write) stays sound for the simpler, still-possible case (a single candidate branch, rejected, with its own unmerged fold-in commit); only its own motivating example (a bookkeeping branch stacked *on* a candidate branch) can no longer occur.

## Affected files (expected, confirm during implementation)

- `skills/continuous-refactoring/references/opening-a-merge-request.md` — the "Basing/stacking" rule (line ~9) inverts: always branch parallel off the default branch, stacking removed entirely (not "stack only when X").
- A new ADR under `docs/adr/`, **superseding** ADR-0015 outright (not merely amending it) — references the two real incidents above as the trigger, and ADR-0006's own older conditional rule (superseded by ADR-0015, now superseded again) for full lineage.
- `docs/adr/0015-suite-merge-requests-always-stack.md` — mark its `## Status` superseded, pointing at the new ADR (matching this repo's own convention for a fully-reversed decision, e.g. how `psr-4`-adjacent ADRs record supersession elsewhere in this suite).
- `docs/adr/0023-never-delete-a-branch-as-a-candidates-only-close.md` and `docs/adr/0028-native-tracker-in-flight-bookkeeping-rides-the-candidate-branch.md` — check whether either's own prose needs a light word-level correction now that "stacked" branches are rarer/nonexistent (likely minimal — both already describe mechanics that don't strictly require stacking to exist, per decision 5 above), but confirm during implementation rather than assume.
- `docs/playbooks/reviewer-loop.md` — new rule: check for a PR based on a branch before deleting it.
- `CONTEXT.md` — check whether any glossary entry describing "stacking" as current suite behavior needs correction (a quick check, not expected to be substantial).

**Status:** ready-for-agent

- [ ] `opening-a-merge-request.md`'s stacking rule inverted: always parallel off the default branch
- [ ] New ADR supersedes ADR-0015 outright, references both real incidents
- [ ] ADR-0015 marked superseded, pointing at the new ADR
- [ ] ADR-0023/ADR-0028 checked for wording that assumed stacking still exists; corrected if found
- [ ] `docs/playbooks/reviewer-loop.md` gains the pre-delete stacked-PR check
- [ ] `CONTEXT.md` checked for stale "stacking" claims

## Comments

> **2026-09-12:** Grilled (`/grill-with-docs`) after a second real auto-close incident (PR #264 on
> Art4/legacy-todo, identical to the earlier #244) proved the reviewer-side mitigation recommended
> after the first incident doesn't hold up in practice. Root-cause analysis distinguishing the two
> incidents' actual structural causes (sequential same-candidate vs. genuine parallel-candidate
> stacking) was done before grilling, confirmed with the maintainer, and found not to matter for the
> final decision — abolish uniformly either way. All decisions above confirmed by the maintainer.
