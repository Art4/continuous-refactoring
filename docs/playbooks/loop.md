# Playbook: The Continuous Refactoring Loop

The playbook for humans. The skills do the work; this document explains how you steer the loop — cadence, triggers, and what you decide each pass.

## What the loop is

Continuous refactoring is **stateful and repeatable**: each pass does only the work due since the last one, and writes learned decisions back. So a weekly turnus and a spontaneous invocation both work — they run the same loop.

```
scan → prioritise → design (grill) → implement (tdd) → review (2 axes)
   └────────────────────────────── learn (ADR / CONTEXT.md / issue status) ←──────┘
```

## Cadence and triggers

- **Cadence:** configured in `docs/refactoring/config.md` (default: weekly). You kick the loop off whenever it's due.
- **On-demand:** `/continuous-refactoring` any time — after a feature, before a release, when an area hurts.
- **Triggers that make an early scan worthwhile:** many commits in the same module (a hot spot), a bug that's been fixed three times, an area the fulfilled tooling keeps flagging.

## What you decide each pass

The loop stops exactly where human judgement is needed:

| Step | Skill | Your decision |
|---|---|---|
| Find candidates | `refactor-scan` | focus area, if you name one |
| Prioritise | `refactor-prioritize` | which candidate is next |
| Design | `refactor-design` | sign off the interface / seam |
| Implement | `refactor-implement` | the seams that get tested |
| Review | `refactor-review` | accept or reject findings |

## After the pass

The loop closes with the **learn step**:

- **ADR**, when a decision should stop future scans from re-litigating it (e.g. "we deliberately don't do this").
- **`CONTEXT.md`**, when new domain terms have crystallised.
- **Issue status**, so the backlog reflects the true state.

## Common mistakes

- **Ignoring tooling-tree pressure.** When fulfilled tooling flags a candidate, the loop prioritises it — unfulfilled tooling is a missing tree node, not a baseline delay.
- **Scanning everything at once.** Scope to hot spots or named areas; a scan that wants everything finds nothing well.
- **Merging reviews into one score.** Standards and spec stay two separate axes — that's the only way you see a violation of one when the other is green.