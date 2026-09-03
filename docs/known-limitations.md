# Known limitations

## GitHub App: CI/checks status may be unreadable even after granting "Actions" access

GitHub Apps scope **Actions** (workflow-run access) separately from **Checks** (the Checks API
that `gh pr checks`, PR merge-state, and check-runs rely on). Granting only "Actions: Read/Write"
in the App's repo-settings permissions does not grant Checks API read access — `refactor-implement`
step 5's CI-status check (`gh pr checks` or equivalent) will 403 or return nothing usable, even
though the human granted what looked like the right permission.

**Fix:** grant the GitHub App **Checks: Read** (repository permission), distinct from Actions.
One-time, per target repo, via the App's installation settings in GitHub's UI — no suite-side
automation for this; it's an admin-only action the bot can't perform on itself.

**If this isn't fixed:** `refactor-implement` still runs — see its step 5 fallback: it verifies
locally instead and says so plainly in the closing report, rather than claiming a CI status it
couldn't confirm.
