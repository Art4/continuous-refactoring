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

Without a reachable git remote the loop has nowhere to push or open a merge request, in any MR-create-mode.
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

Where the tracker isn't GitHub or GitLab, remembered merge requests are kept in the
`merge-requests.md` ledger instead of being read from the tracker's own issue-to-pull-request linkage, and
an in-flight candidate is tracked in `Pending candidates`. The loop works the same way, but the ledger is
only as current as the last pass that wrote it.

## Where the state lives decides what carries over

With local files, the config file and the bookkeeping document under `.scratch/refactor/` are never committed by
the suite: nothing carries them to another machine or teammate for you, and two people running the loop each
keep their own cadence and open items — so each runs Housekeeping on their own schedule, too. Copy or commit the
files yourself when you switch machines. With a bookkeeping issue, any machine that has `gh` / `glab` access to it
picks the state up, but the last write wins (an edit you make during a pass can be overwritten) and an issue that
can't be read — deleted, no access, no CLI — stops the pass rather than creating a new one; a closed issue is
still used, and the report says so. The Housekeeping checklist (`docs/refactoring/housekeeping-template.md`) is
the exception in both cases: it is shared, committed like code.

## Create-modes default to the safe values

A config file that doesn't state `Ticket-create-mode`, or doesn't exist, reads as `ask-each-time`;
`MR-create-mode` reads as `human-opens`. The pass says so in its closing report. Onboarding writes both
explicitly, so this only shows on a machine that skipped it.

## The implement step can hand back instead of finishing

The implement step runs in a subagent that can't ask you questions or reliably reach the forge. When the
plan's seams aren't confirmed yet, the MR-create-mode asks you (`ask-each-time`, `human-opens`), or a push or
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
| Waiting for a confirmation to create a ticket | `Ticket-create-mode` is `ask-each-time` and nobody was there to answer — or you declined the ticket for the candidate the pass chose | Rerun and answer; or set `Ticket-create-mode` to `autonomous` in your config file if nobody will be there. Declined for good? Say so when offered and the node stops being proposed |
| Onboarding wrote setup files and stopped | The project had no bookkeeping document, so this invocation only onboarded it | Commit what belongs in Git (the instruction-file section, `docs/agents/*`), rerun `/continuous-refactoring` |
| Bookkeeping issue can't be read | The pointer names an issue that was deleted, is out of reach (no access, no `gh`/`glab`), or the forge is down | Restore access or point the config file at another issue; the loop never creates a replacement. Onboarding again only after removing the pointer |
| Not onboarded yet | A Track skill or the Housekeeping skill was invoked directly on a project with no bookkeeping document | Run `/continuous-refactoring` first |
| Housekeeping: nothing registered to check | No node has contributed a housekeeping check yet | Expected on a young target |

## Cadence: hours are day-accurate, a month is 30 days

A Track's `Last scan` is a date, not a timestamp. A `Cadence` in hours (`12 hours`) therefore behaves as "due again from the next calendar day on" — a Track scanned this morning is not due again this afternoon, however short the interval. `1 month` counts as 30 days, not a calendar month. The calendar form only anchors monthly (`monthly on the 1st` to `monthly on the 28th`); weekly or weekday anchors aren't supported.

**Fix:** none needed for day-or-longer cadences. For a fixed day of the month, use `monthly on the <N>th`; if the loop has to run more often than daily, trigger `/continuous-refactoring` from your own scheduler, and let each pass pick whichever Track is due.

## Onboarding: GitHub backlog labels are not created for you

Onboarding records the two backlog labels (`refactor:candidate`, `refactor:priority`) in your `AGENTS.md`/`CLAUDE.md` but creates
nothing on the forge. On GitHub, filing an issue with a label that doesn't exist yet fails, so the closing
text lists ready-to-copy `gh label create` commands for both; run them once before the
first pass. GitLab creates a missing project label when an issue is filed with it, so nothing is needed there.
Local Markdown trackers need no labels.
