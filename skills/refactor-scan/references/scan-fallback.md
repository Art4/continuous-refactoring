# Scan Fallback Reference

Git-only reconciliation and PHP-version reversal detection.

## Git-only reconciliation (no gh/glab available)

For each remembered merge request:

- **Merged:** `git fetch origin <branch>`, then `git merge-base --is-ancestor <branch> origin/<default-branch>` exits 0.
- **Still open:** branch present (`git ls-remote --exit-code --heads origin <branch>` exits 0) and not ancestor. Report "still open, no activity signal without API access".
- **Closed without merge:** branch gone (`git ls-remote --exit-code --heads origin <branch>` exits 2) and SHA not ancestor of default.

## PHP-version reversal

Check `docs/refactoring/out-of-scope/<node>.md` entries with `**Blocked by:** PHP >= X.Y`. If the target's current PHP version now satisfies it, hand as a finding to `refactor-learn` — that skill removes the file. A rejection without `Blocked by:` is never a finding here.
