# Known limitations

## A ticket you wrote freely is only found when it is marked or named

The suite finds tickets by searching. Its own tickets name a tool or a module in plain words, so a
search for that subject finds them. A ticket you wrote in your own words has no such handle. On a
large tracker that also holds other work it is picked up in two cases only: your tracker section
says how refactoring tickets are marked (the **Candidate** operation) and the ticket carries that
mark, or you name the ticket in the call.

**What to do:** set a mark for refactoring tickets — the suite proposes one the first time it files a
structural ticket on such a tracker — or name the ticket: `/continuous-refactoring-run ticket 42`.

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

The suite notices this itself: before it picks new work, a run reads whether its open merge requests
can still merge, and brings a blocked one onto the default branch first, by rebase or merge as your
history does it. A conflict in a tool's output is resolved by running the tool again; any other is
resolved by hand and checked again. Only a merge request the forge blocks is touched: one that is
merely behind stays as it is, since every update starts CI again.

**What stays yours:**

- **A conflict that needs a decision** — both sides changed the same logic, or want opposite things.
  The suite pushes nothing and asks on the merge request what to keep.
- **No forge.** Without merge requests there is no merge state to read: a local branch is checked
  only when a run works on it anyway.
- **Another forge** than GitHub or GitLab: where its tool shows no merge state, only a conflict Git
  itself finds is noticed — not a forge rule such as "must be up to date".

## Drafts depend on the forge and its CI

The suite opens each merge request as a draft and marks it ready once it thinks it can merge. Where
the forge has no drafts, every merge request opens ready. Where your CI skips drafts, the run finds
no pipeline for its push and marks the merge request ready so CI runs; it says so in a comment.

Whose draft a draft is, the suite reads from its own steps, not from the account: it opened the
merge request as a draft and never marked it ready, or it commented why when it made it a draft.
Any other draft counts as yours, and the suite leaves it alone until you mark it ready or comment.

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

## A tool's moment to pay off is looked for in recent comments only, on some trackers

When a plan finds that a tool you can ask for would have paid off, it says so in a comment on its ticket, and the
next scan asks you whether to set that tool up. GitHub's issue search and the local ticket files reach comments;
other trackers' searches may not. There the suite finds the line through the plan's merge request, or else reads the
comments of the open tickets and of the ten closed last. A line older than that, with no merge request carrying it,
is not found, and the tool is not offered.

**What to do:** ask for the tool by name in the call when you want it.

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

## A session holds a short cadence only

The Driver waits between rounds in its session, with your environment's timer. A session ends, and a timer
reaches only so far: in Claude Code one wait reaches an hour. Where it cannot wait, the Driver ends and says when
the next round is due. It sets up no schedule.

**What to do:** for a longer cadence, one round a day say, point your own scheduler at
`/continuous-refactoring`. How is up to your repository, your agent and your system.

## The Driver does not know when it last ran

It reads no time of the last round. A call below the cadence starts a round at once, two Drivers side by side both
work, and each call counts its rounds from one: called once a day with an end of five rounds, each call ends after
the rounds it can hold.

**What to do:** how often it is called is yours to decide. Run one Driver per project.

## A gate your CI runs may not run locally

Before it opens a merge request, the suite runs every gate your CI runs over the whole project, such
as a coverage floor, in full. Some of them need something the local machine lacks, a coverage driver
for example. The merge request then opens anyway and names that gate as not run locally, and CI has
the last word on it.

**What to do:** look at that gate's result in CI before you merge, or install what it needs locally.

## Without a recorded BC promise, old APIs stay beside new ones

Whether your project promises stability to code outside it — your package's users, your application's
addons — decides whether an old API may be deleted. Until your tracker file records the promise, the suite
treats code outside the project could reach as covered: restructurings keep old APIs beside new ones where a
deletion would have been fine. The first time a plan does so only for that reason, the next scan files a
ticket that asks you to set the promise up, with a draft. An autonomous run never answers it for you.

**What to do:** answer that ticket, ask for the BC promise in the call ("set up the BC promise"), or add the
**BC promise** bullet to your tracker file yourself — a path, or `none`.

## Only the default branch's promise counts

The suite works on your default branch, so it reads the BC promise of the release line that branch is on. A
maintained older line with a promise of its own — security fixes for the previous major version, say — is not
its work, and nothing it does there follows that line's promise.

**What to do:** keep the suite on the default branch; changes to older lines stay yours.

## The strict coverage check needs PHPUnit 10, and does not work on Pest

The second coverage-metadata step makes a test fail when it runs code it neither covers nor names as used.
It needs PHPUnit 10 or newer, and Pest has no way for a test to name what it uses. On PHPUnit 9 or on Pest
the suite proposes only the first step, that every test says what it covers. PHPUnit also runs the check
only when it collects coverage, so a test run without coverage passes where the coverage job fails.

**What to do:** on PHPUnit 9, the step is proposed once you move to PHPUnit 10. Locally, run the tests the
way your coverage job does before you push.

## A frontend linter waits for the PHP Safety Net

Every Guardrails step waits until the Safety Net is in place, and the PHP Safety Net counts wherever the project has
PHP, even when that PHP only builds or deploys the site. So a project with a JavaScript frontend gets ESLint proposed
only after PHPUnit, PHPStan's first levels and Rector's first sets, though linting the frontend touches none of them.

**What to do:** name the Track to lint the frontend sooner: `/continuous-refactoring-run Guardrails, only the ESLint
Stages`. Where a PHP tool is not wanted for code that only builds the site, decline it when a run proposes it or picks
its ticket, and give the reason; the suite records the rejection and does not propose that tool again.

## Troubleshooting: why did the run end without a merge request?

The closing report's **Status** line always says why. The usual reasons:

| Status says | Cause | What to do |
|---|---|---|
| No Git repository | The suite's only hard requirement is missing | `git init` in the target, call again |
| The onboarding ran and ended | The tracker file had no section for the suite, or lacked a required operation; you stopped the interview, or a required answer was missing — in a run on its own also a **Search** or merge-request command that failed with no working variant found | Call again and answer; commit your tracker file once it is written, then call again to start a run |
| A run ends because of the tracker file | Your `AGENTS.md` or `CLAUDE.md` names a tracker file outside the repository, a URL or a path; the report names it | Name a file inside the repository, or remove the line to use the default path |
| A decision point is laid out and nothing was written | The run was interactive and nobody answered | Call again and answer, or say "do it yourself" in the call |
| Safety Net is unfinished | An autonomous run found nothing workable in Safety Net while it is unfinished; the report lists the Safety Net's tickets that hold it up | Merge, unblock or answer what the report lists, or name another Track |
| Nothing is workable | Every open ticket is in review, blocked or waiting | Merge, answer the open questions, or ask for a scan |
| Nothing is workable in what was asked for | The Track or ticket you named has nothing to work on; a run that was told where to work does not move on | Call without naming it, or name another |
| An open question is on the ticket | The design met a decision it does not make alone, or found that the work would change behaviour; or a ticket was filed with a question the scan could not settle | Reply as a comment on the ticket; the next run reads it |
| An open question says behaviour cannot be held in a test | The design found no way to pin down what a structural ticket must keep, at a reasonable cost | Reply on the ticket: name another seam, accept a coarser test, or decline the ticket |
| A run ended with no merge request after the review | The review found that no change made the code easier to follow, so the run took them all off | Read the ticket's comment; decline the ticket, or reword what it asks for |
| A run ended on a failing check or a review finding | The same check or finding came back after a fix and a second attempt; the branch stays local and the ticket carries the account as an open question | Reply on the ticket: how to go on, or take the branch over yourself |
| A branch was handed over | No forge, or you chose to push yourself | Merge it, or push and open the merge request |
| A merge request was brought onto the default branch | The forge reported it blocked: a conflict, a branch it refuses to merge while behind, or CI red from an outdated base | Nothing; where a conflict was resolved, its comment says how |
| A merge request stays a draft | The Driver's review did not pass it yet, asked for changes or asked you; its comment says which. Or you made it a draft yourself | Answer its comment, or mark it ready when the suite may go on |
| A conflict was handed to you | Both sides changed the same logic, or want opposite things; nothing was pushed | Say on the merge request what to keep, or resolve it yourself |
| Tools named as out of reach | They wait behind something no ticket can change: a PHP version your project does not allow yet, or a project that is not PHP | Raise the PHP version, or record the rejection the suite proposes |
| A run ends because of a Pack | The project's own Pack redefines a slug, a Role or a Pack name the suite has, or the file is not in the Pack format; the error names the file and the slug. A slug the suite added later does the same | Rename your slug or correct the file, then call again ([playbook](playbooks/own-tool.md)) |
| The ticket was not marked ready after its plan | The command of your **Ready after plan** operation failed; the plan stands on the ticket and the report names the command | Run the command yourself, or correct the bullet |
| Housekeeping: nothing due | The open ticket's date is not reached | Wait for the date the report names, or say "now" |
| Housekeeping: the setup waits for its merge request | The template is not on the default branch yet | Merge the first cycle's merge request |
| The line for `AGENTS.md` is missing | A setup left it out — in an autonomous run nobody agreed to it | Ask for it in a call of `/continuous-housekeeping` |
