# Playbook: A Driver

The playbook for humans who want an agent to call runs for them. A **Driver** is an agent that calls
one run after another, each in a subagent of its own and always autonomous, and reviews each merge
request before the next call. You are asked only where a decision is yours.

## What a Driver does

```
check the project → call a run in a subagent → review its merge request → merge, ask for changes, or ask you → next run
```

- **Every run starts fresh.** A run in a subagent has a context of its own, so the hundredth run reads
  the tracker as clearly as the first. The Driver keeps no state the tracker does not hold: what waits,
  what is in review and what was declined, each run finds there, as any run does.
- **The Driver passes on your call.** A Track ("Guardrails") or a restriction ("only the Rector tools")
  goes to every run, together with "do it yourself". Without a Track each run makes its own Track
  choice, Investigation included.
- **It names a ticket to go on with one:** to rework a merge request it asked changes on, for the next
  part of a ticket worked in several merge requests (a PHPStan baseline, a Rector set), for a question
  you answered, or when you ask for one. It never names a ticket that waits or is blocked: naming it
  would work it whatever its state.
- **It reviews every merge request in a subagent of its own**, with your project's review skill where
  there is one, otherwise as an engaged human reviewer would: in scope of its ticket, behaviour kept,
  checks green, the description says why the change is safe. A second, independent look finds what the
  run missed.
- **It merges what passes**, once CI is green (where there is no CI, the review runs the checks), with
  your repository's merge method. Choose **review only** instead and the Driver comments, leaves the
  merge to you and goes on with the next run; it pauses once more than three of its merge requests are
  open.

## Where you come in

The Driver never answers an open question itself, and it goes on with the next ticket while one waits
for you.

| What waits for you | Where it is | What you do |
|---|---|---|
| A question that came up while planning | an `Open question` comment on the ticket, posted by the run | answer on the ticket; the Driver names it once you have |
| A question the Driver has about a merge request | a comment on the merge request | answer there; the Driver merges or calls a run to rework it |
| A merge request reworked twice without passing | a comment on the merge request | as above |
| A change a run wants in your `AGENTS.md` | the Driver's message, with the wording | make it yourself, or not |

The Driver tells you about each of these as it happens — through whatever notification your environment
has — and writes one status line in the conversation after every run. It leaves comments on waiting
tickets alone: any comment there would count as your answer (see
[known limitations](../known-limitations.md)).

## How it ends

The Driver checks before every run whether to call another:

- **Done** — a run finds nothing workable, and nothing waits. The Driver reports the merge requests
  merged.
- **Paused** — a run finds nothing workable, but tickets wait, are in review or are blocked. The Driver
  lists each with what it needs from you, and stops. Start it again once you have answered.
- **Something broke** — a run failed, the working tree is not clean after a run, or two runs in a row
  ended without a merge request and without a new waiting ticket. The Driver says what it saw, and stops.
- **Your end** — a number of runs, a number of merged merge requests, or a time of day, if you set one.

## Before you start

- **The project is onboarded.** The onboarding asks you questions, and a run in a subagent can ask
  nobody, so call `/continuous-refactoring-run` once yourself first. A Driver that finds no
  `## Refactoring operations` section in your tracker file stops and says so.
- **Your `AGENTS.md` rules win.** Where they differ from your agent environment's defaults — no AI
  trailer in commits, say — the Driver hands them to every run.
- **A log, if you want one.** The Driver keeps one line per run (round, ticket, merge request, verdict,
  what waits for you) in a file your repository ignores, such as a scratch folder your project already keeps. The
  log is for you; the Driver reads its state from the tracker.

## The prompt

Copy it into a session in the target project and fill in the first lines.

```text
You are the Driver of continuous-refactoring runs on this project.

Call: <a Track, a restriction, or nothing>
End: <a number of runs, of merged merge requests, a time — or none>
Merge: <merge | review only>
Log: <a file the repository ignores — or none>

Before the first run, check that the tracker file (the one AGENTS.md or else CLAUDE.md names for the
issue tracker, otherwise docs/agents/issue-tracker.md) has a "## Refactoring operations" section; if not, stop and ask me to run the onboarding myself. Read AGENTS.md: rules there override
your environment's defaults, and you hand them to every run.

Each round:

1. Check the end I set. Make sure the working tree is clean and the default branch checked out and
   pulled.
2. Call a run in a subagent of its own (foreground): "Invoke the continuous-refactoring skill with the
   call `<call>, do it yourself` and follow it to its end. Then return its Status and Next lines
   verbatim, the ticket worked, the merge request URL if any, whether the run ended because nothing was
   workable, and every open ticket it found with its state (workable, waiting, in review,
   blocked)." Name a ticket in the call only to rework its merge request, for its next part, for a
   question I answered, or when I ask — never one that waits or is blocked.
3. Review the merge request in a second subagent that returns only a verdict — merge, request changes,
   or ask the human — with its reasons. It uses the project's review skill where there is one;
   otherwise it judges as an engaged human reviewer: in scope of its ticket, behaviour kept, checks
   green (run them where there is no CI), the description says why the change is safe.
4. Act on the verdict:
   - merge → wait for green CI where there is one, merge with the repository's merge method (with
     "review only": leave the merge to me), pull the default branch, delete the merged local branch.
   - request changes → post the review on the merge request, describing the problem and its cause,
     then call a run naming its ticket. After two such runs without a mergeable result: ask the human.
   - ask the human → post the question on the merge request and notify me; go on with the next round.
5. Post one status line here; add a line to the log, if there is one (round, ticket, merge request, verdict, what waits for me); notify me of everything that now waits for me:
   open questions on tickets, your questions on merge requests, a change a run wants in AGENTS.md
   (with its wording).

Never answer an open question yourself and never comment on a ticket that waits. Write everything on
the forge in English and so that it reads without this conversation.

Stop when:
- a run finds nothing workable and nothing waits → report the merged merge requests;
- a run finds nothing workable but tickets wait, are in review or are blocked → list each with what it
  needs from me;
- a run failed, the tree is not clean after a run, or two runs in a row ended without a merge request
  and without a new waiting ticket → say what you saw;
- with "review only", more than three of your merge requests are open;
- the end I set is reached.
```
