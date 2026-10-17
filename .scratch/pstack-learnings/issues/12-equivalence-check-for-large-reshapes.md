# 12 — Equivalence check for large reshapes

Type: task
Status: done

Split out of ticket 01. pstack asks, for larger reshapes, for a script that runs old and new code on the
real artifact and diffs the outputs (back-to-back / differential testing), on top of the pin. Decide what
"large" means (files touched? seams crossed? a plan flag?), where the plan names the check, and how the
merge request reports it. Builds on the `Pin` item of the plan.

See `../spec.md`.

## Comments

### 2026-10-17 — grilled; decisions

- Not a new plan item: the pin's description in the design point now says when its kind is an equivalence script (comparable output at the seam, reshape over several slices behind it); the plan gives one sentence why or why not. No threshold; the agent judges.
- Old side from the base commit in a throwaway worktree outside the tree, new side from the branch, same inputs; runs again with every pass of the checks; a difference is a red check (fix code, not script); script thrown away unless it meets *Tests worth keeping*.
- Inputs: only what the target has (fixtures, example files, test inputs), never production data; none usable → another pin kind, and the MR says so.
- MR: no new item; the pin sentence gains how many inputs agreed.
- Taxonomy: Pin is the umbrella; kinds by oracle — characterization test (hand-written expectation), snapshot (recorded output), equivalence script (the old version live; known as back-to-back testing, a narrower case of differential testing). Fuzzing is an input source, deliberately not adopted. No second late proof step as in pstack.
- Built: `design-point.md`, `implement-point.md` step 3, `opening-a-merge-request.md`, `CONTEXT.md` (Pinning Test), FAQ, changelog fragment.
