# Playbook: The Driver

The playbook for humans who want the suite to keep going by itself. `/continuous-refactoring` is the **Driver**: it works one **round** after another, with a **cadence** between them, until an end. You are asked only where a decision is yours.

A round is one run, the review of its merge request, and any rework:

```
check the project → a run in a subagent → review its merge request → settled, or rework → wait the cadence → next round
```

## The call

It starts without asking, and says back in one sentence what it took. Everything has a default; say otherwise in your own words.

| Setting | Default | You can say |
|---|---|---|
| Merge | `review only`: it comments, and you merge | `merge` |
| End | five rounds | a number of rounds, of merged merge requests, a time, "until nothing is workable" |
| Cadence | 30 minutes between rounds | another duration, "no pause" |
| Call | none: each run makes its own Track choice, Investigation included | a Track ("Guardrails"), a restriction ("only the Rector tools") |
| Log | none | a file your repository ignores, one line per round. The log is for you; the Driver reads its state from the tracker |

For one run alone, a named ticket or [a Pack of your own](own-tool.md), call [`/continuous-refactoring-run`](run.md). Given one of those, the Driver passes it on.

## What a round does

- **Every run starts fresh.** A run in a subagent has a context of its own, so the hundredth run reads the tracker as clearly as the first. It is always autonomous, and your `AGENTS.md` rules go with it.
- **It names a ticket to go on with one:** to rework a merge request it asked changes on, for the next part of a ticket worked in several merge requests, for a question you answered, or when you ask. It never names a ticket that waits or is blocked: naming it would work it whatever its state.
- **It reviews every merge request in a subagent of its own**, with your project's review skill where there is one, otherwise as an engaged human reviewer would: in scope of its ticket, behaviour kept, checks green, the description says why the change is safe.
- **Rework stays in the round.** A request for changes is posted on the merge request, and a run answers it at once, with no cadence between. After two reworks without a mergeable result the merge request goes to you. A round holds up to three runs, and counts as one.
- **With `merge`**, it waits for green CI and uses your repository's merge method. It checks for a merge request stacked on the branch before deleting it, and that the merge really landed the branch's content. If not, it stops: the correction is a normal merge request, never a rewrite of history.

## The cadence

It is counted from the end of the round before. The Driver waits in its session where your environment has a timer. Otherwise it ends and says when the next round is due, and the next call works the next round. A short cadence is all a session holds; a longer one, once a day say, is yours to set up with your own scheduler. See [known limitations](../known-limitations.md).

## Where you come in

The Driver never answers an open question itself, and it goes on with the next ticket while one waits for you.

| What waits for you | Where it is | What you do |
|---|---|---|
| A question that came up while planning | an `Open question` comment on the ticket, posted by the run | answer on the ticket; the Driver names it once you have |
| A question the Driver has about a merge request | a comment on the merge request | answer there, and call again |
| A merge request reworked twice without passing | a comment on the merge request | as above |
| A mergeable merge request, with `review only` | a comment on the merge request | merge it |
| A change a run wants in your `AGENTS.md` | the Driver's message, with the wording | make it yourself, or not |

It tells you about each as it happens, through whatever notification your environment has, and writes one status line after every round. It leaves comments on waiting tickets alone: any comment there would count as your answer.

## How it ends

- **Done:** a run finds nothing workable, and nothing waits.
- **Paused:** a run finds nothing workable but tickets wait, are in review or are blocked; or, with `review only`, more than three merge requests are open. It lists what each needs. Call again once you have dealt with them.
- **Something broke:** a run failed, the working tree is not clean after a run, a merge did not land, or two runs in a row ended without a merge request and without a new waiting ticket.
- **Your end:** by default the fifth round.

## The first call

On a project without a `## Refactoring operations` section the onboarding asks you questions, and a run in a subagent can ask nobody. So the first call runs the onboarding right in your session, and stops: commit what it wrote, then call again.
