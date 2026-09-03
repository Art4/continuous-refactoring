# Git-only reconciliation

Fallback for `refactor-scan` step 3 when no `gh`/`glab` (or other forge API/token) is available — common on a target with no CLI or credentials configured. Real MRs still exist (pushed directly rather than through the API); this only changes how to check their status.

- **Merged:** `git fetch origin <candidate-branch>` (if still present), then `git merge-base --is-ancestor <candidate-branch-or-its-last-known-sha> origin/<default-branch>` exits `0`.
- **Still open, unmerged:** the branch is still present (`git ls-remote --exit-code --heads origin <candidate-branch>` exits `0`) and the merge-base check above is not an ancestor. No reviewer-comment/review-state signal is available this way — report it as "still open, no activity signal available without API access" rather than guessing at review state. Never invent a resume-candidate from git state alone.
- **Closed without merge:** the branch is gone (`git ls-remote --exit-code --heads origin <candidate-branch>` exits `2`) and its last known SHA (from the ledger/issue) is not an ancestor of the default branch. No maintainer comment text is available this way — hand it to `refactor-learn` as a finding with no closing-comment signal; its early-call rule ("otherwise ask the human") already covers a finding with no structural reason attached.

## No remote at all

A step further than the above: `git remote -v` is empty, not just `gh`/`glab` missing — the case `opening-a-merge-request.md`'s "No forge/remote available" hands off to the human for. There's no `origin` to fetch or list against; check the candidate branch locally instead.

- **Merged:** the local candidate branch (still present, or its last known SHA from the ledger/issue) is an ancestor of the local default branch — `git merge-base --is-ancestor <candidate-branch-or-its-last-known-sha> <default-branch>` exits `0`. Covers both ways a human might have landed it (merge commit, or a fast-forward that deleted the branch).
- **Still open, unmerged:** the local branch still exists and isn't an ancestor yet. Same caveat as above — no review-state signal, report only that.

Closed-without-merge has no local signal at all here (no remote to have hosted a real close) — don't report one; a human rejecting a locally-prepared candidate says so directly instead of leaving evidence in git.
