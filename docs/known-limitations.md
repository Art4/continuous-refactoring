# Known limitations

## A ticket you wrote freely is only found when it is marked or named

The suite finds tickets by searching. Its own tickets name a tool or a module in plain words, so a
search for that subject finds them. A ticket you wrote in your own words has no such handle. On a
large tracker that also holds other work it is picked up in two cases only: your tracker section
says how refactoring tickets are marked (the **Candidate** operation) and the ticket carries that
mark, or you name the ticket in the call.

**What to do:** set a mark for refactoring tickets — the suite proposes one the first time it files a
structural ticket on such a tracker — or name the ticket: `/continuous-refactoring ticket 42`.

## The suite cannot run a skill that only you can call

A skill marked for the human's use alone does not appear among the skills an agent sees, so a run can
neither recommend nor start it. To plan or implement a ticket with such a skill, take that step into a
session of your own: a run offers this at the design point and again when the plan is laid out, ends
there, and a later run continues from the plan, the branch or the merge request it finds. An autonomous
run always uses the suite's own procedures.

## A run needs a clean working tree

Before the implementation checks out its branch the suite looks at `git status`. Changes it wrote itself it offers to deliver in a merge request of their own;
changes it did not write it leaves alone and asks you to tidy up — an autonomous run ends there. Files
your project ignores do not count.

## Parallel merge requests may conflict

Nothing limits how many merge requests of the suite are open at once, and each one starts from the
default branch. Two of them may touch the same lines — two tools rewriting the same files, say.
Each merges cleanly on its own; after the first is merged the second may conflict.

**What to do:** resolving that is yours, as with any two branches. Merge in the order the tickets
block each other, or let fewer run side by side by reviewing before calling again.

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
the tool named under **Merge requests** (`gh`, `glab`). Onboarding checks once that it answers, before
it shows you the summary to confirm.

**Fix:** keep that tool installed and authenticated for the target.

## The suite follows your tracker's conventions, it doesn't set them

Which status a ticket gets when work starts, how a merge request refers to its ticket, and the language and
markup of ticket texts are your project's conventions. The suite follows what your tracker file and
your contribution guide say and asks for little of it during onboarding. A convention those files don't state is
one a run won't follow.

## An agent's comment on a waiting ticket counts as your answer

A ticket with an open question waits until a comment follows that is neither the suite's plan nor
another of its questions. Who wrote it does not count, because agents often post with your own
account: the suite cannot tell your reply from an agent's comment, and reads either as the answer.

**What to do:** an agent that drives runs for you ([Driver](playbooks/driver.md)) — or reviews them — leaves waiting tickets alone and
asks you somewhere else.

## A run inside a subagent does every step in its own context

A run hands some steps that only read and judge — the review of its change, judging a scan — to
subagents of its own. A run started in a subagent cannot start further ones in Claude Code, so it does
those steps in its own context, which fills up faster. Runs driven this way have shortened steps: a
review replaced by a quick read, a plan not posted.

**What to do:** the agent driving the runs ([Driver](playbooks/driver.md)) reviews each merge request in a subagent of its own before
merging, and checks that the ticket carries the plan.

## A gate your CI runs may not run locally

Before it opens a merge request, the suite runs every gate your CI runs over the whole project, such
as a coverage floor, in full. Some of them need something the local machine lacks, a coverage driver
for example. The merge request then opens anyway and names that gate as not run locally, and CI has
the last word on it.

**What to do:** look at that gate's result in CI before you merge, or install what it needs locally.

## An autonomous run does not settle the BC promise on a guess

Whether your project promises stability to code outside it — your package's users, your application's
addons — decides whether an old API may be deleted. An autonomous run takes a promise it found in exactly
one document, but never decides that there is none: with no document found, or several, it leaves the
question open, and until you answer it treats code outside the project could reach as covered. Restructurings
then keep old APIs beside new ones where a deletion would have been fine.

**What to do:** answer the question in an interactive run, or add the **BC promise** bullet to
your tracker file yourself — a path, or `none`.

## The strict coverage check needs PHPUnit 10, and does not work on Pest

The second coverage-metadata step makes a test fail when it runs code it neither covers nor names as used.
It needs PHPUnit 10 or newer, and Pest has no way for a test to name what it uses. On PHPUnit 9 or on Pest
the suite proposes only the first step, that every test says what it covers. PHPUnit also runs the check
only when it collects coverage, so a test run without coverage passes where the coverage job fails.

**What to do:** on PHPUnit 9, the step is proposed once you move to PHPUnit 10. Locally, run the tests the
way your coverage job does before you push.

## Troubleshooting: why did the run end without a merge request?

The closing report's **Status** line always says why. The usual reasons:

| Status says | Cause | What to do |
|---|---|---|
| No Git repository | The suite's only hard requirement is missing | `git init` in the target, call again |
| The onboarding ran and ended | The tracker file had no section for the suite, or lacked a required operation; you stopped the interview, or a required answer was missing — in a run on its own also a **Search** or merge-request command that failed with no working variant found | Call again and answer; commit your tracker file once it is written, then call again to start a run |
| A run ends because of the tracker file | Your `AGENTS.md` or `CLAUDE.md` names a tracker file outside the repository, a URL or a path; the report names it | Name a file inside the repository, or remove the line to use the default path |
| A decision point is laid out and nothing was written | The run was interactive and nobody answered | Call again and answer, or say "do it yourself" in the call |
| Safety Net is waiting for merges | An autonomous run found nothing workable in Safety Net while it is unfinished | Review and merge what the report lists, or name another Track |
| Nothing is workable | Every open ticket is in review, blocked or waiting | Merge, answer the open questions, or ask for a scan |
| Nothing is workable in what was asked for | The Track or ticket you named has nothing to work on; a run that was told where to work does not move on | Call without naming it, or name another |
| An open question is on the ticket | The design met a decision it does not make alone, or found that the work would change behaviour; or a ticket was filed with a question the scan could not settle | Reply as a comment on the ticket; the next run reads it |
| An open question says behaviour cannot be held in a test | The design found no way to pin down what a structural ticket must keep, at a reasonable cost | Reply on the ticket: name another seam, accept a coarser test, or decline the ticket |
| A run ended with no merge request after the review | The review found that no change made the code easier to follow, so the run took them all off | Read the ticket's comment; decline the ticket, or reword what it asks for |
| A run ended on a failing check or a review finding | The same check or finding came back after a fix and a second attempt; the branch stays local and the ticket carries the account as an open question | Reply on the ticket: how to go on, or take the branch over yourself |
| A branch was handed over | No forge, or you chose to push yourself | Merge it, or push and open the merge request |
| Tools named as out of reach | They wait behind something no ticket can change: a PHP version your project does not allow yet, or a project that is not PHP | Raise the PHP version, or record the rejection the suite proposes |
| A run ends because of a Pack | The project's own Pack redefines a slug, a Role or a Pack name the suite has, or the file is not in the Pack format; the error names the file and the slug. A slug the suite added later does the same | Rename your slug or correct the file, then call again ([playbook](playbooks/own-tool.md)) |
| The ticket was not marked ready after its plan | The command of your **Ready after plan** operation failed; the plan stands on the ticket and the report names the command | Run the command yourself, or correct the bullet |
| Housekeeping: nothing due | The open ticket's date is not reached | Wait for the date the report names, or say "now" |
| Housekeeping: the setup waits for its merge request | The template is not on the default branch yet | Merge the first cycle's merge request |
| The line for `AGENTS.md` is missing | A setup left it out — in an autonomous run nobody agreed to it | Ask for it in a call of `/continuous-housekeeping` |
