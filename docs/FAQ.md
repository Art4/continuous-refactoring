# FAQ

## Why does the suite install so much tooling instead of just starting the refactor?

Because an LLM can't be trusted to make sweeping code changes safely on its own. The tooling tree
introduces deterministic checks and safeguards — static analysis, coding standards, a working test
runner — *before* an agent is allowed to touch the code, so a wrong or overconfident change gets
caught mechanically rather than relying on the agent to notice its own mistake.

Nearly all of it can be declined, but at the cost of code quality and backward compatibility: fewer
gates means fewer things stopping a bad change before it merges. And nothing forces the order on
you: name the Track you want in the call.

## Why does the suite ask me at every step?

Because everything it does ends up somewhere other people see it: a ticket on your tracker, a branch,
a merge request. By default nothing is written that you did not approve, and each question comes with
a recommendation, so "yes" moves on.

When you would rather not be asked, say so in the call ("do it yourself") or in the middle of a run
("carry on yourself from here"). The suite then takes its own recommendation at every point. It is
the same chain of decisions either way, so an autonomous run does nothing an interactive run would
not have recommended.

## Why isn't "autonomous" a setting I make once?

A setting made once is the one you forget. Earlier versions kept two such settings per machine, and a
developer could not say "show me what you would do" on one call and "do it" on the next. Now the call
says it. For a scheduled job that is one more phrase in the command.

## What happens when I start a run and walk away?

Without the autonomous hint, the run ends at its first decision point. What you find afterwards is
that decision point as a report — what it found, the options, what it recommends — and nothing was
written. That is deliberate: a call nobody attends should not surprise you.

## Why doesn't the suite keep any state of its own?

It used to: a document recording which tools were open, when each Track last ran, what was declined
and which merge request belonged to which ticket. That record duplicated what your tracker and your
forge already show, went stale whenever you worked outside the suite, and needed more rules than
everything else together.

Now your open tickets are the worklist, and the rest is found by searching each time. If you close a
ticket by hand, merge something yourself or set a tool up on your own, the next run finds it that way.
There is nothing to synchronise, nothing to carry to another machine, and two people can use the
suite on one project without sharing a file.

## Why are tickets found by their subject and not by a label?

A marker the suite requires is a marker you forget on the ticket you wrote yourself. So a ticket the
suite files names its subject in plain words — "Introduce PHPStan Level 0" — and is found again by
searching for it. Before filing, the suite searches for an existing ticket on the subject, open or
closed, and continues on yours instead of creating a duplicate.

A label still helps: if your tracker section says how refactoring tickets are marked, the suite uses
that as a hint to narrow its search, and it is how a freely written ticket of yours is picked up on a
tracker full of other work.

## Why only two skills?

Earlier versions were eleven skills, all but one internal, each linked into your project and listed
among your skills. The split existed to give each step a context of its own and to keep one skill as
the only writer of the suite's state. The state is gone, and a step gets a context of its own by
being handed to a subagent together with its instructions. What is left are the two things you
call: a run, and Housekeeping alone.

## Why does Housekeeping have a command of its own?

So it can be scheduled. `/continuous-housekeeping` needs no choice between Tracks: it works the due
ticket or reports that nothing is due. `/continuous-refactoring` still recommends Housekeeping when
its ticket is due.

## Can an agent start a run?

Yes, both commands. An agent you put in charge can hand each run to a subagent of its own, so every run
starts with a fresh context, and call the next one after it has dealt with the merge request. Such a
run asks nobody, so say "do it yourself" in the call: without it the run ends at its first decision
point and writes nothing. The one thing it still leaves to you is a change to your `AGENTS.md`. The
[Driver playbook](playbooks/driver.md) describes such an agent and gives a prompt for it.

## Why does the suite prefer my project's own skills for planning and implementing?

So that refactoring work is built the way all your other work is — same planning habits, same test
discipline, same review. The suite looks at what is available at that moment and recommends it; its
own procedures are the fallback for a project that has none. The choice is made on every run and
stored nowhere, so a skill you install tomorrow is recommended tomorrow.

Two limits. A run you asked to do everything itself uses the suite's own procedures. And a skill
marked so that only you can call it is invisible to an agent: when you want to use one, choose "I plan
this myself" at the design point, or "I implement this myself" when the plan is laid out. The run
ends there and tells you which ticket to hand to your skill; a later run finds the plan, the branch or
the merge request and continues from it.

Whoever builds the change, the suite expects the same two results — a plan on the ticket, a branch
with green checks — and opens the merge request itself, so a run always ends the same way.

## Why is there no limit on open merge requests?

Earlier versions stopped proposing work at two open merge requests and at five open candidates,
whatever you wanted. How much runs in parallel is your decision: a team that reviews fast wants more
in flight than a single maintainer. The one number left is a recommendation, not a limit — an
exploration recommends filing its three strongest findings, and you may file any number.

The price: merge requests opened side by side may conflict. Each starts from the default branch, so
any one of them merges cleanly on its own; resolving a conflict between two is yours.

## Why four Tracks, in a fixed order?

Because the work has different rhythms. Setting up tooling is bounded and mostly one-time; a
structural refactoring is open-ended; maintenance recurs. A fixed order — Safety Net, Guardrails,
Housekeeping, Investigation — over what is workable right now is something you can predict from your
tracker alone, without knowing when anything last ran.

## Why does an autonomous run stop at an unfinished Safety Net?

The Safety Net is what catches a regression before an agent's judgement has to. While it is
unfinished and all of its tickets wait for review, the useful next step is yours — review and merge —
not more work stacked on foundations that are not there yet. So an autonomous run says "Safety Net
is waiting for merges" and ends. You can always decide otherwise: name another Track in the call.

## Why is a Track scanned only once?

A scan judges every tool against your project, which is the most expensive thing a run does, and its
result is already in your tracker afterwards: one ticket per tool still to set up. Repeating it on
every run would repeat work the tickets record. So a tool without an open ticket counts as done, a
recurring Housekeeping task re-checks the tooling, and you can ask for a scan in the call any time.

## Why are some tools only set up when I ask for them?

Because their worth depends on the project, and the suite cannot tell it reliably. A security scanner such
as Semgrep finds a lot in code that grew for years without guardrails and almost nothing in a young project
that had them from the start; there, its ticket is only noise. Such a tool is never offered unasked, and
never blocks a Track. Every scan report names what is available on request; name one in the call and it is
proposed and worked like any other tool.

## Why is the dependency audit a Housekeeping task and not a tool to set up?

Because its value is in repeating it. A pipeline check fails only on advisories known at the moment the
code changes; an advisory published next month against the same lockfile is never seen, and Composer
already audits on every update. The Housekeeping ticket audits your dependencies on every cycle and updates
what has a patched version. A pipeline job that already runs the audit stays as it is.

## Why is Housekeeping a standing ticket instead of a Stage of the tooling tree?

A Stage of the tree is a one-time adoption with a stable test for "done". Maintenance never is. It
also needs a home between cycles: a ticket that is always open is the place where an idea noticed
during feature work can be left. The ticket states its own due date, and its last task creates the
next one, so nothing has to remember when Housekeeping last ran.

## Why does the suite mark a ticket ready after the plan, but never set a status when work starts?

Which status a ticket gets when work starts is your workflow, and the suite neither sets nor asks for it. The moment
its own plan lands on a ticket is different: it is the same for every project, and a project whose planning skill
cannot run unattended would otherwise never see the ticket marked. If your tracker section has a **Ready after
plan** bullet, the suite runs it after it posts a plan, and not when your own skill wrote the plan or while an open
question waits. Without the bullet nothing is written.

## Why does an agent have to ask me before leaving an idea on the Housekeeping ticket?

A comment on a tracker is a write you did not ask for. The line the suite proposes for your
`AGENTS.md` tells every agent to ask first. For the same reason that line itself is only written
after you agreed — in an autonomous run too.

## Why does an autonomous run never decline a ticket that would change behaviour?

A refactoring keeps what the application does. When the design finds that a ticket cannot be done
that way, there are two honest answers — decline it as refactoring, or make it feature work — and
which one is a product decision. The suite leaves the finding on the ticket as an open question and
ends the run. Declining is an option you may choose.

## Why does a plan cut a ticket into several merge requests?

A merge request is only as good as the review it gets. A tool that rewrites two hundred files in one go is
reviewable when every file changes the same way and unreviewable when the changes differ. So the plan
estimates the size first and, where one merge request would be too much, cuts at the seam of kind or risk:
rewrites that only restate the code on one side, rules that change what the code does on the other. Each
part stands on its own, and the plan says in a sentence where it cuts and why. There is no file count,
because the same count can be easy or hard. What the ticket's goal does not need is proposed as a ticket
of its own instead of riding along.

## Why does a structural ticket start with a test, and a tooling ticket does not?

A refactoring promises that behaviour does not change, and that can only be checked against behaviour
written down beforehand. So the first commit of a structural ticket is a test that holds what the code
does today and passes before anything moves; written afterwards it would describe the new code and prove
nothing. A type check or a linter is no substitute. A tooling or baseline ticket lets a tool change the
code, and your existing test suite is what notices a difference, so it adds none. Where a test cannot be
written at a reasonable cost, the suite asks you instead of restructuring unchecked.

That first test only covers the old whole, so it stays green when code moves into a new class without
any test of that class. Each new type the restructuring creates therefore gets a test of its own,
written before the type exists. And because a coverage floor or a similar gate measures the whole
project, not the files a branch touched, the suite runs every such gate your CI has in full before it
opens the merge request.

## Why does PHPMD have no baseline?

A baseline would let the existing findings stay in view only as a list of rule, file and method. It holds no value and no reason, so a method that gets worse after it was baselined stays quiet, and nobody can tell why an entry is there. The suite sets each limit of PHPMD's metrics to the worst value the code has now and lowers it whenever the work removes that value, so the limits themselves are the record of the debt. An exception that is deliberate sits at the code, with its reason beside it. A rule with too many findings to fix in one reviewable merge request waits, marked in the config, and is taken in one rule at a time; you are not asked to give it up. The cost is that PHPMD reports nothing on a project whose limits are ratcheted, so the search for candidates runs it with PHPMD's default limits instead.

## Why does PHP CS Fixer take two Stages?

On a project of a thousand files, one formatting pass is a merge request nobody can review, and narrowing
the config's paths to cut it would also drop every rule already in place on the paths left out. So the
adoption carries the preset and the rules that fit one merge request, and switches the others off with a
marker. A second config file then takes in one rule at a time, path by path. Splitting it into two Stages
keeps the long tail from holding up Rector, which waits only for the adoption, and moves the tail to
Guardrails, where it does not hold up structural work either. The price is that Rector and structural
changes run on code that is only partly styled for a while; a conflict there is resolved by running the
fixer again.

## Why do PHPStan Levels 4 and 5 wait for Rector?

Because Rector clears part of their baseline mechanically, and every finding it clears is one nobody fixes
by hand. Level 4 reports dead code — unreachable statements, conditions and type checks that are always
true or false — and Rector's Dead Code set removes exactly that, so Level 4 waits until that set is decided.
Level 5 checks the types of the arguments passed to methods and functions; once Rector's Type Coverage has
declared the types it can infer, Level 5 is measured once against them, not fixed against docblocks the
rewrites later replace, so Level 5 waits for Type Coverage. The two tools are meant to be used side by side.
Declining the Rector set releases the level; it is then taken in without the rewrites. Rector's PHPUnit Set
does not touch what the levels check and is a Guardrails Stage: it rewrites only test code, and a conflict
with structural work is resolved by running Rector again.

## Why does Rector stop at the PHP version my project declares?

Because rewriting the code for a newer PHP is the same promise as raising the minimum in `composer.json`:
afterwards the code no longer runs on the older PHP. Whoever installs your package or runs your application
on that PHP breaks, even though `composer.json` still says it is supported. Raising the minimum is a product
decision, so the suite never makes it, neither in `composer.json` nor through Rector. Rector's PHP set goes
up to the version you declare; when you raise it yourself, the next re-check of the tooling offers the next
level. Code that already needed a newer PHP before the suite came is proposed as an ordinary ticket, for you
to decide whether the minimum goes up or the code comes down.

## Why does the suite sometimes compare the old and the new code on real inputs?

A test only covers the cases someone thought of. When a restructuring reaches over several steps behind
one edge and the result is something comparable — text, a file, data — the first commit can be a script
instead: it runs the code as it was and the code as it is now on the project's own sample inputs and
compares what comes out. A difference is a mistake in the change, because a refactoring allows none.
It uses only what the project already has — fixtures, example files, inputs of its tests — and never
production data; without a usable input, an ordinary test holds the behaviour. The script is thrown away
afterwards unless it would still be a good test.

## Why are some things rules and others only principles?

A rule is what a run must hold to without exception, and can be checked: a refactoring keeps behaviour, a
tool does what a tool can do, work happens on its own branch, a test pins behaviour first. A principle
helps with a call that depends on the code — whether a migration needs the old and new side by side,
whether a change makes the code easier to follow. An agent weighs it and says in the plan or the review
which one changed a decision. Treating such calls as rules produces changes that are correct and make
nothing better, which is why a change that makes the code no easier to follow is taken off.

## Why are not all of the review's findings fixed?

The suite's own review sorts what it finds. A finding that the plan's slices can fix goes back to be
fixed. One that is right but needs more than the plan is named in the merge request and left, so the
change stays the size you agreed to. One that turns out to be none, because your project's documented
standard endorses the pattern, is dismissed with its reason in the closing report. What the plan did not
ask for, or a change in what the application does, is never dismissed. The suite does not stop to ask
about the grey cases, because an autonomous run could not answer; the closing report lists every
dismissal, so you or the agent that started the run can overrule one.

## Why does a run give up after the same failure comes back, not after a number of tries?

A fixed number of rounds is arbitrary: two might be too few for a hard bug and too many for a dead end.
What shows that a run is stuck is that the same check stays red, or the same review finding returns, after
a fix and then after a second attempt. At that point the suite stops, keeps the branch to itself without
pushing it, leaves a plain-words account on the ticket and waits for your answer. It never turns a check
green by deleting or loosening it.

## Why is the old API sometimes kept beside the new one and sometimes deleted at once?

It depends on your project's promise to the code outside it — the users of your package, the addons of
your application. Where your BC promise covers the old interface, the suite replaces it piece by piece,
keeps old and new side by side, and marks the old one deprecated the way your promise says; it never
deletes it, because that would break someone the promise protects. The removal comes later as an ordinary
ticket for you, when your promise allows it. Where every caller is in the project and the promise does not
cover it, the suite moves all callers and deletes the old API in the same step, so no compatibility layer is
left behind. The plan says which case it found.

## What is the BC promise, and why does the suite ask about it?

It is your project's own document saying which parts of the code stay stable for code outside the project
and how a breaking change is allowed: a new major version under SemVer, or a deprecation period counted in
releases and months, as Friendica's addon promise does. The suite does not model either; it reads your
document. It asks once, at onboarding or at the start of the next run, because several decisions depend on
the answer and a wrong guess cannot be undone by declining a ticket: deleting an API your addons use is a
break, keeping an API nobody outside uses is clutter. It proposes the document it found, or "none". Until
you answer, it treats code reachable from outside as covered.

## Why doesn't the suite just do what a review bot asks?

A bot finds real defects and also files comments that are wrong or only noise, and acting on all of them
makes changes that nobody wanted. So the suite checks each bot comment first, running the test or command it
cites where that is cheap, and sorts it: fix it, dismiss it with a concrete reason, or ask you. Anything
about security, data, permissions, migrations or concurrency is asked, never dismissed. A comment from a
person is a different matter: it is fixed or answered, and the suite never dismisses it by itself. Under
each comment it handles it leaves a short reply, and it does not mark threads as resolved — that is the
reviewer's.

## Why does a merge request say why a change is safe?

The test that pins behaviour covers what a user of the code sees. A rename, a move or a deletion can still
break something the test never reaches: a name in a string, a configuration file, a container entry, stored
data. So where a change touches such a name, the description states the one fact it is safe because of and
how far that was proved — read in the source, shown that the bad case cannot occur, run, or reproduced in
the application. What could not be proved is said to be unproved, so the reviewer knows where to look.
Other changes get no such paragraph.

## I answered an open question on a ticket — what happens now?

Any comment newer than the suite's `Open question` comment ends the wait, unless it is another
`Plan` or `Open question` of the suite. Who wrote it does not count: agents often post with your own
account, so the suite goes by what a comment says. The next run reads your answer: if it confirms the default the plan took, the plan stands; if it names another way, the suite
plans again with it; if it declines the ticket, the decline is recorded; if the question is still
open, you are asked once more. There is no label to
set or remove, so this works on a tracker without triage labels.

## Why "Safety Net" *and* "tooling tree"?

The tooling tree is the underlying model: the tools a project can adopt, each in steps. "Safety Net" names the
part of it that must be settled before structural work starts — deterministic checks such as a test
runner and static analysis — and also names the Track that sets them up. Guardrails is the part that comes
after. One is the map, the other names regions of it.

## Why does the suite think in roles and tools, not just a list of steps?

Because tools compete and projects differ. Two tools can do the same job — PHPStan and Psalm, PHP CS Fixer
and Pint — and a project that already uses one should not be offered the other. So the suite names the job
(a *role*, such as static analysis), the tools that can do it, and the steps of each tool. A project on
Psalm has the role filled and is never offered PHPStan; declining one tool leaves the role open for
another; declining a role closes every tool for it. The same shape lets a project of another language, or a
tool the suite does not know, be added as data instead of a change to the suite.

## How do I add a tool the suite does not know?

Keep a Pack of your own: a `pack.json` with the tool and its steps, a Markdown file saying what makes a step
fulfilled, and a **Tooling Pack** bullet in your tracker file that names the directory. The suite proposes your
steps like its own, and a tool of yours that does the job of one of its tools stands beside it (decline the
suite's if you prefer yours). It adds, it never redefines, and it names the language it works on so a tool for
Twig does not take the place of one for PHP. The [playbook](playbooks/own-tool.md) has a worked example.

## Is it compatible with other engineering skills?

Yes, and it is better with them. A run recommends a project's own skills for planning and implementing,
such as those of [mattpocock/skills](https://github.com/mattpocock/skills), over its own procedures, and
reads an issue-tracker file they wrote. Use the skills you already trust. None is needed: without any,
the first `/continuous-refactoring` writes that file itself and the run plans and implements its own way.

## Which issue trackers work?

Any tracker an agent can reach, as long as `docs/agents/issue-tracker.md` describes it. GitHub, GitLab and local
Markdown files come with a template, so onboarding asks nothing about their operations. For another tracker
onboarding offers three ways: use it as that file already describes it, describe it right there in the
interview, or keep refactoring tickets as local Markdown files while everything else stays where it is.

The suite asks for a handful of operations instead of knowing each tracker by name, because that is all it
needs: how tickets are searched, how a finished one is recognised, where merge requests live. Tickets and
merge requests may also live in two systems; the suite then finds a ticket's merge request by searching the
forge for it.

## Can I run the onboarding again?

It runs again by itself whenever the tracker section lacks an operation the suite requires — that is how a
project set up with an earlier version gets what it is missing. What is already recorded stays and isn't
asked again; only what is missing gets written. On a section that is complete the interview has nothing
to ask: change a bullet there by editing `docs/agents/issue-tracker.md` yourself.

## How do I move a project over from 0.6.0?

Three steps: run the onboarding again; delete the suite's old state files in its scratch folder, which
are no longer read; remove the symlinks of the skills that no longer exist. Nothing is migrated — the
first scan of each Track rebuilds the worklist as tickets. To keep old rejections where they are, name
that folder as the place for rejections in your tracker section. The [README](../README.md#moving-over-from-060)
lists the files.

## How do I make a run work on a specific Track or ticket?

Name it in the call: "work on Guardrails", "ticket 42". The run then stays with it, and ends when it
has nothing to work on. Details: [Track playbook](playbooks/tracks.md).

A named ticket also narrows what the run looks at before it starts: it searches for no other ticket and
reconciles only that ticket's merge request. A run you started for one ticket writes nothing to the
others and does not search the whole tracker first. Merge requests of other tickets that were merged or
closed meanwhile, and declined work whose blocker is met, wait for the next run that names no ticket.

## What happens if there is no remote or forge?

The run still goes as far as it can: it prepares the branch and its commits, names the branch in a comment
on the ticket, and hands it to you — to merge yourself, or to push and open the merge request once a forge
exists. It never commits to the default branch. Later runs read the branch name from the ticket and treat the
ticket as in review until the branch is merged.

## Does the suite decide whether a tool is already adopted by matching dependency names?

No. Fulfilment is judged by an agent against each tool's purpose, so a tool you adopted by hand — or an
equivalent under another name — counts, and its ticket is closed with a note instead of being worked. The
parser only computes the tree's graph logic.
