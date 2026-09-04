---
name: refactor-implement
description: Execute a designed refactor plan test-first, slice by slice, at the agreed seam — review the result, then open the merge request.
---

# Refactor Implement

Execute a **plan** (from `refactor-design`) as vertical slices, red → green, at the agreed **seam** — then review the diff (this step's own job, not a separate one) and open the merge request.

Use `/tdd` if installed for what a good test is and the red → green rules; otherwise `## Fallback` below governs.

Every slice follows the foundational refactoring rules: `skills/continuous-refactoring/references/foundational-refactoring-rules.md`.

## Process

### 1. Branch, then confirm the seams

Create the branch the plan names, or check it out if it already exists (a returning pass, e.g. after a review finding). No earlier skill creates it — this step's job.

Self-assign the candidate issue here too — work has actually started, the moment ownership should become visible (not at design time, where the issue might sit unpicked as a resumable `Pending candidates` entry for a while — assigning it there would misleadingly claim ownership before anyone starts). Whatever the target's tracker names in `docs/agents/issue-tracker.md` — a native tracker's own assignee mechanic (e.g. `gh issue edit <n> --add-assignee @me` on GitHub, or the GitLab equivalent) for a native-label tracker, or that tracker's own convention for marking ownership for Local Markdown or another named convention. No assignee mechanic exists for the tracker in use → skip silently, not a blocker.

A resume-candidate carrying an unaddressed `CHANGES_REQUESTED` review (from `refactor-scan` step 3) → read that review's comments/body first and treat them as this pass's findings to address, before re-examining the rest of the branch.

Structural candidate: list the seams the plan names and confirm them with the user. **No test is written at an unconfirmed seam** — testing at the wrong seam is how refactors produce tests that break under refactoring.

Tooling-tree node: no seam to confirm — its scope is a config/dependency change (see the tree doc's MR scope), not code. Skip straight to making that change; no red → green cycle, only its Fulfilment check (step 3).

Baseline-shrink candidate: no seam to confirm either — `refactor-design` already picked the group and files (`phpstan-baseline-shrink.md` step 3). No red → green cycle: this satisfies a static-analysis finding without introducing new behavior, so there's no new test to write at a seam — the full test suite (step 3) is what catches an unintended behavior change instead.

**`loop-config` exception — this node itself:** `refactor-design` couldn't write `Pending candidates` (the Refactoring Notes' `bookkeeping.md` didn't exist yet). Creating the file here, perform every write `skills/continuous-refactoring/references/loop-config-interview.md`'s `## Record` names (Create-mode, tracker file, the `Refactoring Notes:` line) — the interview already decided these, don't leave them unset or invent placeholders. Two things `## Record` doesn't cover, this step's own addition: set `Pending candidates` to this candidate's issue, and `Focus areas` only if the interview named one. Leave `Fulfilled nodes` unset — still `refactor-learn`'s field, filled in its own follow-up commit. All of it in the same MR as `bookkeeping.md` — this node's only one.

### 2. One slice at a time

Skipped for a tooling-tree node (step 1 already made its one change). Structural candidate: before the first test, ensure `tests/README.md` exists if the active language specialization defines a test-layout convention (PHP: `skills/refactor-scan/references/php-tooling-tree/phpunit.md`'s *Test layout*). Missing → create it with that default. Present → read it fresh (a human may have adapted it), follow it, create a documented-but-not-yet-existing folder only once a test needs it. No language convention → place tests by judgment.

Each slice: write the failing test first (red), then only enough code to pass it (green). One seam, one test, one minimal implementation per cycle. Don't anticipate future slices or add speculative features.

Baseline-shrink candidate: skip the red → green cycle (step 1) — make the planned fix file by file, **one commit per file fixed** (or per otherwise-distinct reduction), even within the same MR. A clean, reviewable trail of exactly which reduction landed where, since a group may take more than one MR to fully clear (step 5's multi-MR `Closes` handling already covers that case).

### 3. Verify the loop on completion

Structural candidate, slices done: run the full test suite (surviving plan tests plus new seam tests, all green) and the fulfilled tooling (PHPStan, Rector, style) over touched files — must not regress mechanical quality.

Tooling-tree node: no test suite to judge it — the node's own **Fulfilment check** from the tree doc is the acceptance check. Run or confirm exactly what it specifies.

Baseline-shrink candidate: regenerate `phpstan-baseline.neon` and confirm the touched files' entries for the chosen group are gone — full removal for what this MR actually touched; reducing the group overall is enough, it doesn't have to empty in one MR (`phpstan-baseline-shrink.md` step 3). Also run the full test suite over touched files, same as a structural candidate — real application code changed here too, even though no new test was written.

### 4. Review the diff

Delegate to the `mattpocock/skills` implement skill (`setup-matt-pocock-skills`) if installed — it already embeds review. Otherwise run two axes:

- **Standards** — does the diff conform to this repo's documented standards and the fulfilled tooling?
- **Spec** — does it faithfully implement the plan on the candidate issue: missing/partial requirements, scope creep, requirements that look implemented but wrong?

Findings on either axis send the work back to step 2 (structural) or step 1 (tooling-tree) — implement, don't hand off. Report the two axes separately, one line per finding (file, issue, fix); on the Spec axis, quote the plan line each finding is checked against.

### 5. Open the merge request

Review clean → push the branch and open the MR (create-mode per the Refactoring Notes' `bookkeeping.md`; full rules: `skills/continuous-refactoring/references/opening-a-merge-request.md`). No forge/remote to push to at all → don't attempt it; hand the branch to the human instead, per that same reference's "No forge/remote available" — this is expected, not a failure, and the completion criterion below adjusts for it. Include `Closes #<candidate-issue-number>` only when this MR is understood to satisfy the candidate issue's Fulfilment check on its own — the common case. A node needing more than one MR to fulfil — the common case for a baseline-shrink candidate, whose chosen group can span more MRs than fit this pass — don't add `Closes` to an intermediate one; `refactor-learn`'s own early-call behavior (closing the issue once it sees the candidate merged) is the designed fallback.

`docs/agents/issue-tracker.md` names a native-label tracker and `refactor-learn`'s native-tracker in-flight fold-in exception applies (its closing call will ride this same branch later this pass) → open the MR **as a draft** (`skills/continuous-refactoring/references/opening-a-merge-request.md`'s *Draft candidate MRs*) — the fold-in commit landing and marking it ready for review is `refactor-learn`'s job, not this step's. No native-label tracker, or the fold-in exception doesn't apply → open it normally, same as always.

Wait for CI if the target runs it — confirm via the forge's actual CI status (`gh pr checks` or equivalent), not a local rerun of step 3's checks. Red CI is a review finding like any other — back to step 2/1.

**Before writing anything in the closing report that claims work is done, fixed, or CI is green — re-check current state fresh.** A new `gh pr diff`/`gh pr checks`/`gh pr view` call (or forge equivalent) run in *this* pass, never memory of what an earlier step in this same pass intended or attempted. A diff byte-identical to a still-red prior round is still red — stating it's fixed because an earlier pass meant to fix it is exactly the failure this guards against.

**CI status unreadable via the API** (403, or nothing usable returned) — don't guess, and don't claim green. State plainly in the closing report that live CI status couldn't be confirmed via API and that verification instead ran locally in an environment equivalent to CI (name which checks). This is the documented fallback, not a silent workaround — see `docs/known-limitations.md`.

The candidate branch stays checked out after this. `refactor-learn`'s bookkeeping writes go out on their own separate branch/MR, never this one (the `loop-config`-in-flight case is the one exception, which `refactor-learn` handles).

## Output

The opened merge request → `refactor-learn`.

## Fallback

- **`/tdd`**: installed → use its discipline. Otherwise loop rules and test-quality criteria inlined at `skills/refactor-implement/references/review-fallback.md`.
- **`mattpocock/skills` implement skill**: installed → it already embeds step 4's review. Otherwise run step 4's two axes by the standards-axis rules (repo standards plus a fixed Fowler smell set) at the same `skills/refactor-implement/references/review-fallback.md`.

## Completion criterion

The branch exists with the work on it, review is clean on both axes, MR is open (CI green where the target runs it) — or, no forge/remote at all, the branch is handed to the human per `opening-a-merge-request.md` instead. Structural: every slice implemented red → green, full suite green, fulfilled tooling clean on touched files. Tooling-tree node: the MR-scope change is made and its Fulfilment check passes. Baseline-shrink candidate: the touched files' entries for the chosen group are confirmed gone from the regenerated baseline, one commit per file fixed, full suite green.
