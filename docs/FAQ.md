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
being handed to a subagent together with its instructions. What is left are the two things a human
calls: a run, and Housekeeping alone.

## Why does Housekeeping have a command of its own?

So it can be scheduled. `/continuous-housekeeping` needs no choice between Tracks: it works the due
ticket or reports that nothing is due. `/continuous-refactoring` still recommends Housekeeping when
its ticket is due.

## Why does the suite prefer my project's own skills for planning and implementing?

So that refactoring work is built the way all your other work is — same planning habits, same test
discipline, same review. The suite looks at what is available at that moment and recommends it; its
own procedures are the fallback for a project that has none. The choice is made on every run and
stored nowhere, so a skill you install tomorrow is recommended tomorrow.

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

## Why is Housekeeping a standing ticket instead of a tooling-tree node?

A node of the tree is a one-time adoption with a stable test for "done". Maintenance never is. It
also needs a home between cycles: a ticket that is always open is the place where an idea noticed
during feature work can be left. The ticket states its own due date, and its last task creates the
next one, so nothing has to remember when Housekeeping last ran.

## Why does an agent have to ask me before leaving an idea on the Housekeeping ticket?

A comment on a tracker is a write you did not ask for. The line the suite proposes for your
`AGENTS.md` tells every agent to ask first. For the same reason that line itself is only written
after you agreed — in an autonomous run too.

## Why does an autonomous run never decline a ticket that would change behaviour?

A refactoring keeps what the application does. When the design finds that a ticket cannot be done
that way, there are two honest answers — decline it as refactoring, or make it feature work — and
which one is a product decision. The suite leaves the finding on the ticket as an open question and
ends the run. Declining is an option you may choose.

## I answered an open question on a ticket — what happens now?

Any comment newer than the suite's `Open question` comment ends the wait. The next run reads your
answer: if it confirms the default the plan took, the plan stands; if it names another way, the suite
plans again with it; if the question is still open, you are asked once more. There is no label to
set or remove, so this works on a tracker without triage labels.

## Why "Safety Net" *and* "tooling tree"?

The tooling tree is the underlying model: a graph of adoption steps. "Safety Net" names the
part of it that must be settled before structural work starts — deterministic checks such as a test
runner and static analysis — and also names the Track that sets them up. Guardrails is the part that comes
after. One is the map, the other names regions of it.

## Do I need the matt-pocock skills?

No, but they help. `setup-matt-pocock-skills` (from [mattpocock/skills](https://github.com/mattpocock/skills))
writes the issue-tracker file the suite reads, and its skills for planning and implementing are the
kind a run recommends over its own procedures. Without them the first `/continuous-refactoring`
writes the issue-tracker file itself; running the setup later extends that file in place.

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

## What happens if there is no remote or forge?

The run still goes as far as it can: it prepares the branch and its commits, names the branch in a comment
on the ticket, and hands it to you — to merge yourself, or to push and open the merge request once a forge
exists. It never commits to the default branch. Later runs read the branch name from the ticket and treat the
ticket as in review until the branch is merged.

## Does the suite decide whether a tool is already adopted by matching dependency names?

No. Fulfilment is judged by an agent against each tool's purpose, so a tool you adopted by hand — or an
equivalent under another name — counts, and its ticket is closed with a note instead of being worked. The
parser only computes the tree's graph logic.
