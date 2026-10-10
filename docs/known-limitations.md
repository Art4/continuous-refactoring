# Known limitations

## A ticket you wrote freely is only found when it is marked or named

The suite finds tickets by searching. Its own tickets name a tool or a module in plain words, so a
search for that subject finds them. A ticket you wrote in your own words has no such handle. On a
large tracker that also holds other work it is picked up in two cases only: your tracker section
says how refactoring tickets are marked (the **Candidate** operation) and the ticket carries that
mark, or you name the ticket in the call.

**What to do:** set a mark for refactoring tickets — the suite proposes one the first time it files a
structural ticket on such a tracker — or name the ticket: `/continuous-refactoring ticket 42`.

## Parallel merge requests may conflict

Nothing limits how many merge requests of the suite are open at once, and each one starts from the
default branch. Two of them may touch the same lines — two tools rewriting the same files, say.
Each merges cleanly on its own; after the first is merged the second may conflict.

**What to do:** resolving that is yours, as with any two branches. Merge in the order the tickets
block each other, or let fewer run side by side by reviewing before calling again.

## A target that is not a PHP project never gets a fulfilled Safety Net out of a scan

Beyond `.editorconfig` and a CI pipeline, every tool of the Safety Net is a PHP tool. On a project in
another language a scan finds those out of reach, files no ticket for them, and Safety Net does not
come out of it as fulfilled. An autonomous run that scanned stops there with "Safety Net is waiting
for merges".

Where both language-neutral tools are already in place, the scan has nothing to file, the tracker
never shows that the Track was scanned, and every run scans and stops again. Where the scan did file
tickets, later runs read the tracker instead of scanning: once those tickets are closed they count
Safety Net as fulfilled and move on — until a scan you ask for, or Housekeeping's re-check within
its own run, judges the tools again.

**What to do:** name the Track in the call, or run interactively and choose it. Investigation and
Housekeeping work on any project.

## On a tracker strangers can write to, their comments on the Housekeeping ticket are weighed like anyone's

A Housekeeping run reads the comments on its ticket as refactoring ideas, whoever wrote them. On a
public tracker an autonomous run therefore takes up a stranger's comment as a proposal. What limits
this is the kind of change, not the author: an idea is carried out only as a behaviour-keeping
change of structure in code that tests or a tool cover. A comment asking for anything else — a
command to run, a dependency, CI, credentials — is left alone. And what is carried out arrives in
a merge request a human reviews, one commit or a few per idea.

**What to do:** review the idea commits of a Housekeeping merge request as you would a stranger's
contribution — on a public tracker that is what they may be.

## With a daily rhythm, the tooling re-check runs daily

The template the suite proposes holds the task that re-checks Safety Net and Guardrails — a full
scan of both, the most expensive thing the suite does. It runs as often as the template's rhythm
says.

**What to do:** on a daily rhythm, move that task by hand into a second template with a rarer
rhythm ("a monthly one beside the daily").

## A proposal you did not file is not remembered

What a scan or an exploration offers and you neither file nor decline is stored nowhere. A tool
left that way counts as done from then on, until a scan you ask for or Housekeeping's re-check
offers it again; a structural finding may or may not come up in a later exploration.

**What to do:** file what you want kept, decline what you never want, and ask for a scan when you
want to see the rest again.

## GitHub App: CI/checks status may be unreadable even after granting "Actions" access

GitHub Apps scope **Actions** (workflow-run access) separately from **Checks** (the Checks API
that `gh pr checks`, PR merge-state, and check-runs rely on). Granting only "Actions: Read/Write"
in the App's repo-settings permissions does not grant Checks API read access — reading the CI
result of a merge request will 403 or return nothing usable, even though the human granted what
looked like the right permission.

**Fix:** grant the GitHub App **Checks: Read** (repository permission), distinct from Actions.
One-time, per target repo, via the App's installation settings in GitHub's UI — no suite-side
automation for this; it's an admin-only action the bot can't perform on itself.

**If this isn't fixed:** the run still ends with an open merge request; its closing report says that
the CI result could not be read and names the checks that ran locally, rather than claiming a status
it couldn't confirm.

## No remote or forge: nothing gets pushed

Without a reachable Git remote there is nowhere to push or to open a merge request. The run prepares
the branch and its commits locally, names the branch in a comment on the ticket, and stops there.

**What to do:** merge the branch into the default branch yourself, or push it and open the merge
request once a forge exists. Until the branch is merged, later runs treat the ticket as in review.

## Merge requests are read through the tool your tracker file names

Reconciling merged and closed merge requests, and telling which tickets are in review, goes through
the tool named under **Merge requests** (`gh`, `glab`). Onboarding checks once that it answers.

**Fix:** keep that tool installed and authenticated for the target.

## The suite follows your tracker's conventions, it doesn't set them

Which status a ticket gets when work starts, how a merge request refers to its ticket, and the language and
markup of ticket texts are your project's conventions. The suite follows what `docs/agents/issue-tracker.md` and
your contribution guide say and asks for little of it during onboarding. A convention those files don't state is
one a run won't follow.

## Troubleshooting: why did the run end without a merge request?

The closing report's **Status** line always says why. The usual reasons:

| Status says | Cause | What to do |
|---|---|---|
| No Git repository | The suite's only hard requirement is missing | `git init` in the target, call again |
| The onboarding ran and ended | The tracker file had no section for the suite, or lacked a required operation; you stopped the interview, or a required answer was missing | Call again and answer; commit `docs/agents/issue-tracker.md` once it is written |
| A decision point is laid out and nothing was written | The run was interactive and nobody answered | Call again and answer, or say "do it yourself" in the call |
| Safety Net is waiting for merges | An autonomous run found nothing workable in Safety Net while it is unfinished | Review and merge what the report lists, or name another Track |
| Nothing is workable | Every open ticket is in review, blocked or waiting | Merge, answer the open questions, or ask for a scan |
| Nothing is workable in what was asked for | The Track or ticket you named has nothing to work on; a run that was told where to work does not move on | Call without naming it, or name another |
| An open question is on the ticket | The design met a decision it does not make alone, or found that the work would change behaviour | Reply as a comment on the ticket; the next run reads it |
| A branch was handed over | No forge, or you chose to push yourself | Merge it, or push and open the merge request |
| Tools named as out of reach | They wait behind something no ticket can change: a PHP version your project does not allow yet, or a project that is not PHP | Raise the PHP version, or record the rejection the suite proposes |
| Housekeeping: nothing due | The open ticket's date is not reached | Wait for the date the report names, or say "now" |
| Housekeeping: the setup waits for its merge request | The template is not on the default branch yet | Merge the first cycle's merge request |
| The line for `AGENTS.md` is missing | A setup left it out — in an autonomous run nobody agreed to it | Ask for it in a call of `/continuous-housekeeping` |
