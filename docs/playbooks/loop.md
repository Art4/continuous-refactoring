# Playbook: The Continuous Refactoring Loop

The playbook for humans. The skills do the work; this document explains how you steer the loop — cadence, triggers, and what you decide each pass.

## What the loop is

Continuous refactoring is **stateful and repeatable**: each pass does only the work due since the last one, and writes learned decisions back. So a weekly turnus and a spontaneous invocation both work — they run the same loop.

```
scan (propose nodes, detect closed MRs) → prioritise → design (grill, file the issue) → implement (tdd + review)
   └────────────────────────────────── learn (ledger / ADR / CONTEXT.md / issue status) ←──────┘
```

The orchestrator passes each skill's output to the next as its input (ADR-0010) — nobody re-derives context from shared state except `refactor-scan`'s own detection and whatever local state doc a skill reads directly.

## Triggers

The loop never triggers itself — it has no stored schedule (`docs/playbooks/refactoring-config.md`). You kick it off, however often that is: by hand, or via whatever recurring trigger you set up outside the suite.

- **On-demand:** `/continuous-refactoring` any time — after a feature, before a release, when an area hurts.
- **Recurring:** point your own scheduler (a cron job, `/schedule`, `/loop`) at `/continuous-refactoring` on whatever interval fits — the loop does the same one pass regardless of how often it's invoked.
- **Triggers that make an early scan worthwhile:** many commits in the same module (a hot spot), a bug that's been fixed three times, an area the fulfilled tooling keeps flagging.

## What you decide each pass

The loop stops exactly where human judgement is needed:

| Step | Skill | Your decision |
|---|---|---|
| Propose nodes | `refactor-scan` | focus area, if you name one |
| Prioritise | `refactor-prioritize` | which node is next |
| Design | `refactor-design` | sign off the interface / seam |
| Implement (review included) | `refactor-implement` | the seams that get tested; accept or reject review findings |
| Learn | `refactor-learn` | none — bookkeeping only |

## After the pass

The loop closes with the **learn step**:

- **ADR**, when a decision should stop future scans from re-litigating it (e.g. "we deliberately don't do this").
- **`CONTEXT.md`**, when new domain terms have crystallised.
- **Issue status**, so the backlog reflects the true state.

## Common mistakes

- **Ignoring tooling-tree pressure.** When fulfilled tooling flags a candidate, the loop prioritises it — unfulfilled tooling is a missing tree node, not a baseline delay.
- **Scanning everything at once.** Scope to hot spots or named areas; a scan that wants everything finds nothing well.
- **Merging reviews into one score.** Standards and spec stay two separate axes — that's the only way you see a violation of one when the other is green.