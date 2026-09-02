# Git-only reconciliation

Fallback for `refactor-scan` step 3 when no `gh`/`glab` (or other forge API/token) is available — common on a target with no CLI or credentials configured. Real MRs still exist (pushed directly rather than through the API); this only changes how to check their status.

- **Merged:** `git fetch origin <candidate-branch>` (if still present), then `git merge-base --is-ancestor <candidate-branch-or-its-last-known-sha> origin/<default-branch>` exits `0`.
- **Still open, unmerged:** the branch is still present (`git ls-remote --exit-code --heads origin <candidate-branch>` exits `0`) and the merge-base check above is not an ancestor. No reviewer-comment/review-state signal is available this way — report it as "still open, no activity signal available without API access" rather than guessing at review state. Never invent a resume-candidate from git state alone.
- **Closed without merge:** the branch is gone (`git ls-remote --exit-code --heads origin <candidate-branch>` exits `2`) and its last known SHA (from the ledger/issue) is not an ancestor of the default branch. No maintainer comment text is available this way — hand it to `refactor-learn` as a finding with no closing-comment signal; its early-call rule ("otherwise ask the human") already covers a finding with no structural reason attached.
