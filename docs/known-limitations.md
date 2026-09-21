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

## No remote or forge: nothing gets pushed

Without a reachable git remote the loop has nowhere to push or open a merge request, in any create-mode.
It prepares the branch and its commits locally and stops there.

**Fix:** either commit the branch yourself (skipping review — reasonable for a first, low-stakes change
such as the initial config) or push it and open the merge request yourself. The candidate stays in its
"merge request open" state; a later pass detects it delivered once your action lands it.

## Without `gh`/`glab`, merged and closed merge requests are detected from git only

With a remote but no forge CLI or API token, the loop falls back to what git alone shows: a merge request
counts as merged when its branch is an ancestor of the default branch, and as closed when the branch is
gone without having landed. Review activity, closing comments and CI status are invisible to it, so a
pass can't resume a candidate on reviewer feedback there, and the closing report says so rather than
assuming an outcome.

**Fix:** install and authenticate `gh` or `glab` for the target.

## Trackers without native labels use a ledger file

Where the tracker isn't GitHub or GitLab, remembered merge requests are kept in the committed
`merge-requests.md` ledger instead of being read from the tracker's own issue-to-pull-request linkage, and
an in-flight candidate is tracked in `Pending candidates`. The loop works the same way, but the ledger is
only as current as the last pass that wrote it.

## The implement step can hand back instead of finishing

The implement step runs in a subagent that can't ask you questions or reliably reach the forge. When the
plan's seams aren't confirmed yet, the create-mode asks you (`ask-each-time`, `human-opens`), or a push or
merge-request creation fails, it reports the branch and what's left, and the loop finishes that part
itself. If the subagent mechanism isn't available at all, the same steps simply run in the main
conversation.

**Fix:** none needed; answer the question the loop puts to you.

## Troubleshooting: why did the pass end without doing anything?

The closing report's **Status** line (or, for onboarding, its closing text) always says why. The usual reasons:

| Status says | Cause | What to do |
|---|---|---|
| No git repository | The loop's only hard requirement is missing | `git init` in the target, rerun |
| Needs a Track / was given none | A Track skill was invoked without going through the loop, or the dispatcher didn't select one | Start from `/continuous-refactoring` |
| Backlog full | Five or more open `refactor:candidate` issues (not counting `refactor:priority` ones) | Merge, close or finish existing candidates |
| Two merge requests already open | The suite-wide cap | Review and merge or close one |
| Candidate waiting on `ready-for-agent` | The design step left an open question (`needs-info`) | Answer it on the issue, then add `ready-for-agent` |
| Safety Net walk: nodes skipped | Blocked by an unfulfilled parent, `needs-info`, or an unverified PHP floor | Read each reason; adopt the parent, answer the question, or reject the node |
| Onboarding wrote setup files and stopped | The project had no `bookkeeping.md`, so this invocation only onboarded it | Commit the new files to the default branch, rerun `/continuous-refactoring` |
| Not onboarded yet | A Track skill or the Housekeeping skill was invoked directly on a project with no `bookkeeping.md` | Run `/continuous-refactoring` first |
| Housekeeping: nothing registered to check | No node has contributed a housekeeping check yet | Expected on a young target |

## Onboarding: GitHub backlog labels are not created for you

Onboarding records the two backlog labels (`refactor:candidate`, `refactor:priority`) in your `AGENTS.md`/`CLAUDE.md` but creates
nothing on the forge. On GitHub, filing an issue with a label that doesn't exist yet fails, so the closing
text lists ready-to-copy `gh label create` commands for both; run them once before the
first pass. GitLab creates a missing project label when an issue is filed with it, so nothing is needed there.
Local Markdown trackers need no labels.
