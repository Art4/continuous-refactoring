# Playbook: The Continuous Refactoring Loop

The playbook for humans. The skills do the work; this document explains how you steer the loop — cadence, triggers, and what you decide each pass.

## What the loop is

Continuous refactoring is **stateful and repeatable**: each pass does only the work due since the last one, and writes learned decisions back. So a weekly turnus and a spontaneous invocation both work — they run the same loop.

The first invocation on a project that has never run the loop is different: it only **onboards** — a short interview, a few setup files written, then it stops (no scan, no issue, no merge request). Commit those files and run `/continuous-refactoring` again; every invocation after that is a pass as described next.

Each pass has two stages. First `/continuous-refactoring` selects one **Track** — Safety Net, Guardrails, Housekeeping or Investigation ([Track playbook](tracks.md)). Then that Track's skill runs the pass:

```
select Track
   └─ scan (propose nodes, detect closed MRs) → prioritise → design (grill, plan onto the ticket) → implement (tdd + review)
         └────────────────────────────────── learn (ledger / ADR / CONTEXT.md / issue status) ←──────┘
```

(Housekeeping runs its own sweep instead of this pipeline — see the [Housekeeping playbook](housekeeping.md).) A thin data pipe carries each skill's output to the next as its input — nobody re-derives context from shared state except `refactor-scan`'s own detection and whatever local state doc a skill reads directly. The scan and implement steps run in subagents, so their reasoning stays out of the main conversation.

Structural work (Investigation) only opens once the tooling adoption chain is in place — this playbook calls that chain the **Safety Net**: deterministic checks (static analysis, a test suite) that catch a regression before an agent's own structural judgement has to. It's the same mechanism `CONTEXT.md` and the skills themselves still call the tooling tree — "Safety Net" is a reading aid for this playbook, not a renamed concept.

### What you see while it runs

The loop narrates the pass in your conversation: one sentence before each step says what starts, one after says what came back (what scan found, which node won and why, what design planned). Every change to your repository is reported on its own line when it happens — an issue created, a branch pushed, a merge request opened, a bookkeeping merge request. Housekeeping does the same. The steps that run in subagents can't talk to you directly, so the loop reports for them after they return; the closing report stays two lines and doesn't repeat any of it.

## Triggers

The loop never triggers itself — it has no stored schedule (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`). You kick it off, however often that is: by hand, or via whatever recurring trigger you set up outside the suite.

- **On-demand:** `/continuous-refactoring` any time — after a feature, before a release, when an area hurts.
- **Recurring:** point your own scheduler (a cron job, `/schedule`, `/loop`) at `/continuous-refactoring` on whatever interval fits — every invocation runs exactly one pass, and the Track scheduler decides what that pass works on from each Track's own cadence.
- **A specific Track:** name it ("run the Guardrails Track") or invoke its skill directly to bypass selection for one pass.
- **Triggers that make an early scan worthwhile:** many commits in the same module (a hot spot), a bug that's been fixed three times, an area the fulfilled tooling keeps flagging.

## What you decide each pass

The loop stops exactly where human judgement is needed:

| Step | Skill | Your decision |
|---|---|---|
| Onboarding (first invocation only) | `continuous-refactoring` | tracker, whether tickets get created automatically or after asking (`Ticket-create-mode`), the same for merge requests (`MR-create-mode`), where the suite keeps its state (local files, a new bookkeeping issue, or an existing one), whether to move state from an earlier version — and, if the engineering-skills setup is missing, whether to stop and run it first |
| Select Track | `continuous-refactoring` | optionally, which Track to force |
| Propose nodes | `refactor-scan` | focus area, if you name one |
| Prioritise | `refactor-prioritize` | which node is next; a `refactor:priority` label you set narrows the ranking |
| Ticket | `refactor-loop` | with `Ticket-create-mode` `ask-each-time`, whether the tickets it proposes get created — one question for the batch of proposed nodes, then one for the candidate it chose. Say no to the chosen one and the pass ends; you're offered to reject that node for good so it isn't asked again |
| Design | `refactor-design` | sign off the interface / seam; answer a flagged open question (the issue carries `needs-info` until you do, and `ready-for-agent` once it may proceed) |
| Implement (review included) | `refactor-implement` | the seams that get tested; accept or reject review findings |
| Merge request | `refactor-implement` | with MR-create-mode `ask-each-time` or `human-opens`, whether the merge request gets opened — and by whom |
| Learn | `refactor-learn` | none — writes the bookkeeping in place |

Two merge requests at most are open at once. With two waiting, a pass tells you which ones and ends without new work — merging or closing one is what unblocks the loop.

## After the pass

The loop closes with the **learn step**:

- **ADR**, when a decision should stop future scans from re-litigating it (e.g. "we deliberately don't do this").
- **`CONTEXT.md`**, when new domain terms have crystallised.
- **Issue status**, so the backlog reflects the true state.

## Common mistakes

- **Ignoring tooling-tree (Safety Net) pressure.** When fulfilled tooling flags a candidate, the loop prioritises it — unfulfilled tooling is a missing tree node, not a baseline delay.
- **Scanning everything at once.** Scope to hot spots or named areas; a scan that wants everything finds nothing well.
- **Waiting on a Track that's blocked.** While Safety Net still has open items, nothing else runs; the closing report names what is waiting (a parent node, a `needs-info` answer). Answer or adopt it by hand — don't force another Track.
- **Merging reviews into one score.** Standards and spec stay two separate axes — that's the only way you see a violation of one when the other is green.