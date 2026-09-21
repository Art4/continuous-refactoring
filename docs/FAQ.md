# FAQ

## Why does the suite install so much tooling instead of just starting the refactor?

Because an LLM can't be trusted to make sweeping code changes safely on its own. The tooling tree
introduces deterministic checks and safeguards — static analysis, coding standards, a working test
runner — *before* an agent is allowed to touch the code, so a wrong or overconfident change gets
caught mechanically rather than relying on the agent to notice its own mistake.

Nearly all of it can be skipped, but at the cost of code quality and backward compatibility: fewer
gates means fewer things stopping a bad change before it merges. The tooling also gives you a
lever — reviews of the suite's own merge requests can steer, speed up, or focus what the loop
decides to work on next, the same way any other proposal-and-review cycle would.

## Why is Housekeeping a separate Track instead of a recurring tooling-tree node?

Because the tooling tree is a purely fact-based, filesystem-driven model — its deterministic parser
has no forge access and so has no way to derive a cadence from tracker history. A time-driven
"unfulfilled again after N days" flag would also violate `structural-scan`'s own assumption that a
once-resolved leaf stays resolved.

It doesn't fit the ordinary candidate pipeline shape either: `scan → prioritise → design → implement →
learn` ranks and delivers one candidate at a time, but a housekeeping sweep works down a standing
checklist instead — there's nothing to rank. That's why it's its own Track, run directly by the
`continuous-housekeeping` skill when the shared Track scheduler selects it (default cadence:
weekly), rather than a step inside the ordinary candidate pipeline or a node inside the tree — the same
shared scheduler that runs Safety Net, Guardrails, and Investigation, but with its own self-contained
due-check/reconcile/checklist/deliver process once selected, architecturally independent of the
propose-then-hand-off shape the other three Tracks use.

## Why four Tracks instead of one long pipeline?

Because the work has different rhythms. Adopting tooling is bounded and mostly one-time; a structural
refactoring is open-ended; a maintenance sweep is calendar-driven. One pipeline ranking all of it
together would let the endless kind of work crowd out the finite kind, or vice versa. Each Track has its
own cadence, and a pass runs whichever is most overdue. The order stays sensible on its own: the Safety
Net must be in place before structural work opens, and Investigation, which is always due, only runs
when nothing else needs the pass.

## Why is `continuous-refactoring` only a dispatcher?

So the part that decides *what* to run is small enough to read in one sitting, separate from the part that
runs it. `continuous-refactoring` only selects a Track; a per-Track skill runs it, and the three
tooling-and-structure Tracks share one track-agnostic loop. Adding a Track means adding a skill and a
bookkeeping section, not reworking the pass.

## Why are at most two merge requests open at once?

Reviewing is the bottleneck, not writing. Without a cap the loop would keep opening merge requests faster
than you can review them, and each one would go stale. With two open, a pass tells you which are waiting and
ends without new work. Each merge request also branches off the default branch, never off another
one, so merging them in any order is safe.

## Why does the loop write everything through `refactor-learn`?

So "what changed the loop's state?" has one answer. The other skills detect, decide, plan or implement;
only `refactor-learn` records outcomes — the ledger, each Track's bookkeeping section, issue status,
decision records in the target. A skill that wrongly assumes state can't quietly corrupt it.

## Why "Safety Net" *and* "tooling tree"?

The tooling tree is the underlying model: a graph of adoption steps, walked forever. "Safety Net" names the
part of it that must be settled before structural work starts — deterministic checks such as a test
runner and static analysis — and also names the Track that adopts them. Guardrails is the part that comes
after. One is the map, the other names regions of it.

## Do I need the matt-pocock skills?

No, but they help. `setup-matt-pocock-skills` (from [mattpocock/skills](https://github.com/mattpocock/skills))
writes the issue-tracker file and the triage-label table the suite reads. The suite decides whether that
setup is in place from the repo itself: both `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md`
must exist. If either is missing, the first `/continuous-refactoring` asks once whether to stop so you can
run the setup first (nothing is written) or to continue, in which case it writes a minimal issue-tracker
file and label table itself. Running the setup later updates those files in place. Labels are only ever
recorded in files — the suite never creates a label on GitHub or GitLab during onboarding.

## Why do I have to run `/continuous-refactoring` twice on a new project?

Because setting up a project is a different job from refactoring it. The first invocation on a project with
no `bookkeeping.md` only onboards: it asks a few questions, writes the setup files, tells you what it did
and stops. That keeps one-time setup out of the scan-prioritise-design-implement pipeline — no issue, no
merge request, no branch — and it means the very first thing you see is that onboarding is happening, not a
scan starting in the background. Commit the new files to the default branch (candidate branches are based on
it), then run `/continuous-refactoring` again: that invocation selects a Track and starts the first scan.
Naming a Track on a project that was never onboarded still onboards first.

## How do I make the loop work on a specific Track?

Name it when you invoke `/continuous-refactoring` ("run the Housekeeping Track"), or invoke the Track's
skill directly. That bypasses the scheduler for one pass. Details: [Track playbook](playbooks/tracks.md).

## What happens if there is no remote or forge?

The loop still runs as far as it can: it prepares the branch and its commits and hands it to you, either
to commit yourself or to push and open the merge request once forge access exists. It never invents a
local-only merge request and never commits to the default branch. The closing report says plainly what it
couldn't confirm.

## Does the loop decide whether a tool is already adopted by matching dependency names?

No. Fulfilment is judged by an agent against each node's purpose, so a tool you adopted by hand — or an
equivalent under another name — counts, and the node leaves the open list without a merge request. The
parser only computes the tree's graph logic.
