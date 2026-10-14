# Suite rebuild: one run of decision points, state in the tracker

**Status:** ready-for-agent

Target release: 0.7.0. Everything lands on the integration branch `suite-rebuild`; `main` stays at 0.6.0
until the whole rebuild is accepted.

## Problem Statement

A developer who calls `/continuous-refactoring` gets a whole pass: the suite picks a Track, files a ticket,
designs, implements and opens a merge request. How much of that happens without asking is fixed in a
per-machine config file, set once in an onboarding interview. The developer cannot say "show me what you
would do next" on one call and "do it yourself" on the next.

The suite also keeps its own state — which nodes are open, when a Track last ran, what was rejected, which
merge request belongs to which ticket — in a bookkeeping document, with a pointer to it, a config file, a
local and a remote variant, and a single skill allowed to write it. That state duplicates what the issue
tracker and the forge already show, goes stale when a human works outside the suite, and is the largest
source of rules in the skill texts.

Tickets are recognised by a fixed marker (a label, a category, a title). A ticket a human wrote without
the marker is invisible to the suite.

The suite brakes on its own: at two open merge requests and at five open candidates it stops proposing
work, whatever the developer wants.

Finally, the suite is ten skills, eight of them internal, each symlinked into a target and listed among
the developer's skills.

## Solution

One run is a chain of **decision points**: reconcile, choose a Track, scan, file tickets, select a ticket,
design, implement, open the merge request. At each one the suite lays out what it found and recommends one
option.

- **Interactive** (the default): the human decides at every point.
- **Autonomous** (said in the call, in free words): the suite takes its own recommendation at every point.
  The human may switch from interactive to autonomous mid-run.

The call takes free text the suite interprets: a Track, a restriction ("only the Rector nodes"), a ticket,
the autonomous mode.

The suite keeps no state of its own. Open tickets are the worklist; merge requests, rejections and the
standing Housekeeping ticket are found by searching the tracker and the forge. The config file, the
bookkeeping document, the pointer, local and remote bookkeeping and the cadence fields all go.

The suite is two skills a human calls — `continuous-refactoring` and `continuous-housekeeping` — and
everything else is a reference one of them loads when a run reaches it.

## User Stories

### Running

1. As a developer, I want `/continuous-refactoring` without further words to walk me through one run and
   ask me at every decision point, so that nothing is written to my tracker or forge that I did not approve.
2. As a developer, I want every decision point to come with a recommendation, so that I can answer "yes"
   and move on.
3. As a developer, I want to say in the call that the suite should do the run itself, so that one call
   takes a ticket from selection to an opened merge request.
4. As a developer, I want to say "carry on yourself from here" in the middle of an interactive run, so that
   I only attend the decisions I care about.
5. As a developer, I want to name a Track in the call, so that I can work on Guardrails although the suite
   would recommend something else.
6. As a developer, I want to restrict a run in free words ("only the Rector nodes"), so that scan, ticket
   filing and selection stay within what I asked for.
7. As a developer, I want to name a ticket in the call, so that the suite works on exactly that one.
8. As a developer, I want a run to end once the merge request is open, so that I get more work done by
   calling again, not by one run growing.
9. As a developer, I want an autonomous run to end with a clear message when the design cannot proceed
   without a human answer, so that it never guesses.
10. As a developer who started the suite without the autonomous hint and is not there to answer, I want
    the run to end at the first decision point with a report of what it found and what it recommends, so
    that an unattended call writes nothing.
11. As a developer, I want no limit on open merge requests or open candidates, so that how much runs in
    parallel is my decision.
12. As a developer, I want repeated calls on Safety Net to end, eventually, at "every workable node has a
    ticket and an open merge request", so that I know the next step is mine: review and merge.

### Track choice and worklist

13. As a developer, I want the suite to search the open tickets, sort them into Tracks and recommend a
    Track from that, so that an unspecific call is cheap.
14. As a developer, I want the recommendation to follow a fixed order — Safety Net, Guardrails,
    Housekeeping, Investigation — so that I can predict it.
15. As a developer, I want an autonomous run to stop at Safety Net while Safety Net is unfinished, and to
    be able to override that myself, so that the foundations come first unless I say otherwise.
16. As a developer, I want a Track with nothing workable to be skipped within the same run once Safety Net
    is fulfilled, so that a call does not end empty when another Track has work.
17. As a developer, I want a scan only when a Track has no trace yet in my tracker — no ticket of its
    nodes, open or closed, and no recorded rejection —, as a recurring Housekeeping task, or when I
    ask for one, so that a run does not repeat work the tickets already record.
18. As a developer, I want the scan to offer a ticket for every node that is neither fulfilled nor
    rejected, blocked ones included and marked as blocked, so that the whole way ahead is visible in my
    tracker.
19. As a developer, I want a node's fulfilment check to run again right before its ticket is worked, so
    that a tool I set up by hand is noticed and its ticket closed instead of redone.
20. As a developer, I want the order within Safety Net and Guardrails to follow the tooling tree and
    within Investigation to follow the signals, with a ticket I marked as priority first, so that the
    recommendation is explainable.
21. As a developer, I want an Investigation run with no open tickets to explore the code, show me
    everything it found in order of signal, and recommend filing the three strongest, so that neither I
    nor an autonomous run flood the tracker.

### Finding things again

22. As a developer, I want the suite to search for an existing ticket about a subject before it files one,
    open or closed, so that it continues on mine instead of filing a duplicate.
23. As a developer, I want a ticket I wrote myself to be picked up when my repository describes how
    refactoring candidates are marked, or when I name it in the call, so that I can hand work to the suite
    without a suite-specific label.
24. As a developer, I want the suite to find the merge request of a ticket by searching, so that nothing
    depends on a list it kept.
25. As a developer, I want a run to begin by telling me which of its merge requests were merged or closed
    and recommending what follows — close the ticket, record a rejection, ask me — so that tracker and
    forge agree.
26. As a developer, I want a rejection recorded as a closed ticket or as a file, in the place my repository
    names, so that the suite and my own triage share one memory of what was declined.
27. As a developer, I want the suite to ask what happens to the tickets that depend on a node I just
    rejected, with a recommendation that follows the kind of edge, so that no ticket is orphaned silently.
28. As a developer, I want a rejection whose stated reason no longer holds (a minimum PHP version now met)
    to be offered for reversal, so that a node comes back when its blocker is gone.

### Design, implementation, decisions

29. As a developer whose repository has its own skills for planning and implementing, I want the suite to
    recommend those and use its own only as a fallback, so that refactoring work is built the way all my
    other work is.
30. As a developer, I want that choice to be a decision point and never stored, so that installing a skill
    tomorrow changes the recommendation tomorrow.
31. As a developer, I want the suite to open the merge request itself when the implementing skill did not,
    so that a run always ends the same way.
32. As a developer, I want an ADR and a glossary change to travel in the candidate's merge request, so that
    I review a decision together with its code.
33. As a developer whose repository keeps no ADRs, I want none written, so that the suite follows my
    conventions.

### Housekeeping

34. As a developer, I want one standing, open Housekeeping ticket created from a template in my
    repository, so that recurring maintenance has a visible home.
35. As a developer, I want the template to state the recurring tasks, the rhythm, and as its last item
    "create the next Housekeeping ticket", so that the cycle carries itself.
36. As a developer, I want to choose the rhythm when Housekeeping is first set up, with a recommendation
    drawn from my repository, so that a busy project can run it daily and a quiet one monthly.
37. As a developer, I want to keep several templates with different rhythms, so that daily and monthly
    chores stay apart.
38. As a developer, I want a line in my `AGENTS.md` telling every agent to propose refactoring ideas as a
    comment on the open Housekeeping ticket, after asking me, so that ideas noticed during feature work
    are not lost.
39. As a developer, I want the Housekeeping run to carry out those comments along with the recurring
    tasks, each in a commit of its own, so that I can review and revert them one by one.
40. As a developer, I want the run to propose moving a comment that is too big for Housekeeping into a
    ticket of its own, so that it gets a plan and its own review.
41. As a developer, I want the secret scan over the Git history to be a Housekeeping task — the whole
    history the first time, afterwards the commits since the last Housekeeping ticket — so that it recurs
    without a remembered flag.
42. As a developer, I want Housekeeping to offer to set its mechanism up when it is missing, so that after
    one setup `/continuous-housekeeping` works without further explanation.
43. As a developer, I want `/continuous-housekeeping` as an entry point of its own, so that I can schedule
    it.
44. As an agent about to comment on the Housekeeping ticket who finds two open ones, I want the human to
    choose, with the younger one recommended, so that the comment lands where work has not started.

### Setting up and moving over

45. As a developer installing the suite, I want onboarding to ask only where my tickets live and how the
    operations work there, so that setup is short.
46. As a developer, I want the suite installed with two symlinks, so that my skill list shows two entries
    for it.
47. As a developer with a target onboarded on 0.6.0, I want a changelog entry that names the breaking
    change and the three steps — run onboarding again, delete the old files under the suite's scratch
    folder, remove the symlinks of the removed skills — so that I can move over in minutes.
48. As a developer who wants to keep old rejections where they are, I want to name that place in my
    repository's operations, so that nothing has to move.
49. As a developer, I want questions and reports to speak of the "skill suite" and of a "run", so that I am
    not addressed in the suite's internal words.

## Implementation Decisions

### How this is built

- **Rewrite the flow texts from this spec, do not transform the old ones.** The entry skill, the Track
  choice, the per-Track references, the Housekeeping process, the fallback design and implement references
  and the onboarding interview are written new. Carried over as content: the tooling-tree node definitions
  and edges, the parser, the signals catalogue, the structural candidate search, the refactoring-operations
  reference, the forge-facing writing rules.
- **Every text an agent reads is written with the `writing-for-agents` skill**: steps end on a checkable
  completion criterion, reference only some branches need sits behind a pointer, one meaning lives in one
  place, the target behaviour is stated positively.
- **No tests are written and none are repaired during the rebuild**, with one exception: the parser
  (Testing Decisions). Red checks on `suite-rebuild` are accepted until the final decision about tests.
- **A changelog fragment** names the rebuild as breaking for 0.7.0.

### Shape of the suite

- Two user-invocable skills: `continuous-refactoring` (the run) and `continuous-housekeeping` (the
  Housekeeping Track alone, no Track choice). Both read the same Housekeeping reference.
- Removed as skills: `refactor-loop`, `refactor-scan`, `refactor-prioritize`, `refactor-design`,
  `refactor-implement`, `refactor-learn`, `continuous-safety-net`, `continuous-guardrails`,
  `continuous-investigation`. What each knew that still applies becomes a reference of
  `continuous-refactoring`.
- A step that deserves a context of its own is handed to a subagent together with its reference.
- The rule "only one skill writes" goes with the bookkeeping it protected. The scan may act on what it
  finds, through a decision point.

### The run

- The chain: reconcile → Track choice → scan (only when the Track needs one) → file tickets → select →
  design → implement → merge request. Each link is a decision point: findings, options, one recommendation.
- Autonomous is the same chain with the recommendation taken. There is one path to maintain.
- Without the autonomous hint and without anyone answering, the run ends at the first decision point with
  a report and has written nothing.
- A run ends when the merge request is open, when the design cannot proceed without a human, or when
  nothing is workable.
- The limits on open merge requests and open candidates are removed.
- **Writes that need a human even in an autonomous run:** changing the target's `AGENTS.md`.

### Track choice

- At the start the suite searches the open tickets and assigns each to a Track: a ticket matching a node
  belongs to that node's Track; the open Housekeeping ticket to Housekeeping; everything else —
  structural candidates, tickets a human wrote — to Investigation.
- Recommendation in fixed order: Safety Net, Guardrails, Housekeeping, Investigation; the first with
  something workable.
- While Safety Net is not fulfilled, an autonomous run that finds nothing workable there ends with
  "Safety Net is waiting for merges". A human may choose another Track. Moving on to the next Track within
  one run applies once Safety Net is fulfilled.
- Housekeeping is recommended when its open ticket's due date is reached, or when the mechanism is missing.
- Investigation with no open tickets explores; the three strongest findings are the recommendation for
  filing; the rest is not stored.

### Tickets as the worklist

- "Workable" means: an open ticket whose blockers are all done.
- A Track scan runs when the Track has no trace yet (no ticket of its nodes, open or closed, and no
  recorded rejection) or on request. With a trace, a node without an open ticket counts as done, the gate
  is computed on that, and re-checking the tooling Tracks is a task of the Housekeeping template. A scan
  runs the fulfilment
  checks, and offers a ticket for every node neither fulfilled nor rejected, blocked ones included.
- Before a ticket is worked, its node's fulfilment check runs again; a fulfilled node's ticket is closed
  with a note.
- A ticket names its subject in plain words in title and text (the tool's name), so that a later search
  finds it. No hidden marker, no fixed title.
- Several hits are all shown, one recommended.
- Limit, stated in the docs: on a large tracker a freely written ticket is found only through a
  **Candidate** hint in the target's operations or by being named in the call.

### The parser

- Reads no file of the suite. The state of the nodes (fulfilled, rejected) is handed in.
- Emits, per Track, the list of nodes with name and tool from the node sections. Track membership stays
  derived from the edges; it is not maintained as a column.
- Still emits the ordered backlog, blocked nodes included, and the reasons a node is withheld.
- The `onboarding-setup` node's fulfilment is: the target's tracker file has a `## Refactoring operations`
  section.

### Refactoring operations

- Required: **Search** (new — how tickets are searched, open and closed), **Done**, **Merge requests**.
- Optional: **Candidate** and **Priority** (now hints for search and order), **Linked merge request**,
  **Comment author and time**, **Claim**, **Rejected** (new — how a rejection is recorded and found again:
  closed ticket or file, and where), **Blocked by** (new — how a ticket states what blocks it),
  **Housekeeping** (new — where the template lives and how the next ticket is made from it).
- Removed: **Bookkeeping**, **Filed date**.
- Missing **Blocked by** → the suite writes the dependency as a sentence in the ticket and reads it there.
- Missing **Rejected** → the suite proposes a place when the first rejection is recorded.
- The templates for GitHub, GitLab and Local Markdown are updated to this cut.

### Rejections

- Recorded as a closed ticket with the reason, or as a file, wherever the target says. The engineering
  skills' `.out-of-scope/` folder is a natural place when the target uses it.
- A rejection with a machine-readable blocker (minimum PHP version) is offered for reversal when the
  blocker is met.
- Rejecting a node others depend on is a decision point: close the dependents as rejected (required edge)
  or remove the blocker (recommended edge).

### Design and implementation

- At the design and the implement point the suite looks at the skills available in the target and at what
  its `AGENTS.md` says, recommends the target's own, and falls back to its own references.
- Expected from a design skill: a ticket carrying an implementable plan. From an implement skill: a branch
  with green checks. The suite opens the merge request per **Merge requests** unless it already exists.
- ADR and glossary changes are part of the candidate's merge request, and only where the target's domain
  docs say ADRs are kept.

### Housekeeping

- Always one open Housekeeping ticket per template. The template is a file in the target; its location
  and the way the next ticket is made from it are the target's (**Housekeeping** operation).
- The template holds the recurring tasks, the rhythm, and the last item "create the next Housekeeping
  ticket". The new ticket states from when it is due.
- Tooling-tree nodes keep contributing their Housekeeping line to the template through their own merge
  request.
- A run works the recurring tasks and the comments on the ticket, each comment in one or more commits of
  its own; one too big for Housekeeping is proposed for a ticket of its own.
- Secret scan over history: a task in the template; whole history the first time, then since the last
  Housekeeping ticket's date.
- Mechanism missing → the Track proposes: create the template (rhythm chosen by the human, recommended
  from the target), create the first ticket, add the `AGENTS.md` line.
- The `AGENTS.md` line says: propose refactoring ideas as a comment on the open Housekeeping ticket, after
  the human allowed it; with two open tickets the human chooses, the younger recommended.

### Onboarding and existing targets

- The interview keeps the tracker question and the operations. The questions on ticket mode, merge-request
  mode and bookkeeping are gone.
- The dispatcher check stays: no `## Refactoring operations` section → onboarding. A section without
  **Search** → onboarding adds it.
- No migration. Files under the suite's old scratch folder are no longer read.
- The project lines `Focus areas` and `Refactoring goal` stay human-written and feed the recommendations.

### Vocabulary

- Leaves `CONTEXT.md`: Loop pass, Ticket-create-mode, MR-create-mode, Refactoring Notes, Bookkeeping
  document, Bookkeeping pointer, Local/Remote bookkeeping, Config file, cadence.
- Enters: **Run**, **Decision point**, **Interactive / Autonomous**, **Worklist**, **Housekeeping ticket**,
  **Housekeeping template**.
- Text addressed to the human says "skill suite" and "run".
- ADRs record: the run as decision points with two modes; state in the tracker instead of bookkeeping;
  one skill with references and the target's own skills first; the standing Housekeeping ticket. They
  supersede the ADRs on the single writer, the bookkeeping, the scheduler's cadence and the caps.

## Testing Decisions

- A good test here checks what a caller of the parser sees: given a tree, a repository and a node state
  handed in, which nodes come back per Track, in which order, withheld for which reason. It does not check
  how the parser reads its files.
- **Only the parser gets tests during the rebuild**, at its existing seam: the command-line and function
  interface the scan uses. Prior art: the existing parser unit tests. Tests of the bookkeeping derivation
  are removed with that code; tests for the per-Track node list and the handed-in state are added.
- **Skill texts get no tests.** The validator, the trigger-control tests and the fixture harness are left
  red where the rebuild breaks them. What is deleted, adapted or rewritten is decided once, with the
  finished suite in view, before the pull request to `main`.
- **Acceptance is a run in a real target**, from the `suite-rebuild` checkout: onboarding again, one
  interactive run, one autonomous run, one Housekeeping run. The target is the one whose tracker and forge
  are different systems and whose tracker is large.

## Out of Scope

- A migration of existing bookkeeping into tickets.
- New tooling-tree nodes, new language specialisations.
- Distributing the suite without its development files.
- Reducing the verification a fallback implement run does per slice.
- A hand review of every text the suite posts to a forge.
- Scheduling: the suite offers an entry point that can be scheduled, it schedules nothing.

## Further Notes

- The work is cut into tickets under this feature's `issues/` folder, merged on `suite-rebuild`, and goes
  to `main` as one pull request.
- The decision about tests and the acceptance run need the human and sit outside the automated build.
- The operations contract from 0.6.0 stays the base; this spec changes its cut, not its idea.
