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

## Why does only the loop create tickets — and why would it ask?

A ticket is visible to everyone watching the tracker, and it can be closed but not un-created. The steps that come up with candidates run in subagents, and a subagent can't ask you anything, so they hand back drafts and the loop — the one place that can ask — creates them. `Ticket-create-mode` decides how: `autonomous` creates them as the pass needs them; `ask-each-time` asks once for the whole batch of tickets proposed up front and once more for the candidate the pass chose. It's separate from `MR-create-mode`, which is only about opening merge requests; you can be asked about one and not the other. If you decline the chosen candidate's ticket the pass ends without touching anything else, and you're offered to reject the node for good. With nobody there to answer, nothing is created and the pass says it is waiting — switching the field to `autonomous` in your config file is the way to run unattended. A config file that doesn't state the field reads as `ask-each-time`, so a fresh machine never creates tickets on its own.

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

## Why doesn't the suite commit its own state?

Because the state — each Track's last scan and open items, your create-modes — is bookkeeping about *your*
runs, not part of the project. Committing it meant bookkeeping branches, extra merge requests and a
review nobody wanted to give. The suite now keeps it in one of two places and leaves Git alone. **Local files**
under `.scratch/refactor/` are the default: whether they are committed, ignored or copied to another machine is
your decision, and this is meant for one person on one working tree. Or **one tracker issue** (GitHub or GitLab),
created during onboarding: the suite loads it before a pass and saves after each write, so you can run the loop
from another machine without carrying files around. Your config (`Ticket-create-mode`, `MR-create-mode`, the
pointer to the bookkeeping) is a separate file either way, because it can differ per person and machine.

## What happens if two people edit the bookkeeping issue at once?

The last write wins. The suite doesn't reload and merge before saving, so an edit you make in the issue while a
pass is running can be overwritten by that pass. The loop is meant to run on one machine at a time; edit the
issue between passes.

## Why do I have to run `/continuous-refactoring` twice on a new project?

Because setting up a project is a different job from refactoring it. The first invocation on a project with
no bookkeeping document only onboards: it asks a few questions, writes the setup files, tells you what it did
and stops. That keeps one-time setup out of the scan-prioritise-design-implement pipeline — no issue, no
merge request, no branch — and it means the very first thing you see is that onboarding is happening, not a
scan starting in the background. Commit what belongs in Git (the instruction-file section, `docs/agents/*`; the
files under `.scratch/refactor/` are yours to keep or not), then run `/continuous-refactoring` again: that invocation selects a Track and starts the first scan.
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
