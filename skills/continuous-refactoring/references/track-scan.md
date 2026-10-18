# Reference: scanning a tooling Track

The scan of Safety Net or Guardrails: judge the Track's Stages against the target, let the parser order
them, and turn every Stage that is neither fulfilled nor closed by a rejection into a **proposal** for a
ticket. It runs when a Stage of the Track is not known yet (`worklist.md`, *A Track's trace*), when the
call asked for it, or as the Housekeeping task that re-checks the tooling Tracks. The scan reads; its
proposals reach the tracker through the filing step.

## 1. Scope

From the parser's seedless call (`tooling-parser.md`): the Track's `nodes`, the Packs, and the first Stage
of every Tool, recognized ones included — they say which Tool fills a Role. A restriction in the call
narrows what step 4 proposes; of the Stages outside it, only those a covered Stage requires are judged.

## 2. Judging

- **Rejected** — the recorded rejections (`rejection.md`, *Finding rejections*), of Roles, Tools and
  Stages, with their blockers.
- **The Packs.** Each Pack's *Applies when*, judged once per run against the target; the Packs it holds
  for go into the seed's `packs`. The generic Pack always applies.
- **The runtime.** For each runtime a Tool of an applying Pack names in `min_runtime`, the lowest version
  the target's manifest allows, as the seed's `runtime` (`tooling-parser.md`). Where it is unclear, none is
  handed in and nothing is blocked.
- **Every other Stage in scope** whose Pack applies — judged, below. A Stage whose own *Applies when* does
  not hold goes into `not_applicable`.
- **The other tooling Track's Stages.** In a Safety Net scan they stay undecided. In a Guardrails scan the
  Safety Net decides what blocks a Guardrails Stage: one with an open ticket stays undecided, every other
  is judged unless this run already judged it.

Judging may run in a subagent handed this section and the Packs; it returns the seed and, per Stage
judged fulfilled under another name than its Tool, the evidence in one line.

### Judging a Stage

Read the Purpose of the Tool's Role (`roles.json`) and the Stage's Fulfilment check in its Tool's `details`
file, then the target. **Judge by Purpose:** a Stage is fulfilled when a real, working tool serves the
Purpose in the target, under any name.

- **The evidence the Fulfilment check names is there** — the dependency, the config file, the CI
  invocation → fulfilled.
- **It is absent, and another tool serves the Purpose** → fulfilled. A CI job running
  `composer run security-check`, a script that calls `composer audit`, fulfils `composer-audit`. Where the
  Pack knows the other tool as a recognized Tool, its own Stage is the one fulfilled, never the
  recommended Tool's: a target running Psalm fulfils the Stage `psalm`, one running Laravel Pint the Stage
  `pint` (Easy Coding Standard: `ecs`), and no PHPStan Stage and not `php-cs-fixer` is judged fulfilled for
  it. The Role is then filled by the recognized Tool, and the recommended one is not proposed.
- **Two tools compete for the Purpose, or it is unclear whether one serves it** → undecided, and the
  proposal carries the question, so the human answers it at filing.
- **Nothing serves it** → undecided. A human who says the Purpose is met without a tool declines the
  Stage at filing; that is a rejection, never a fulfilment.

Step 2 is done when every Stage in scope is in one of the seed's lists or deliberately in neither.

## 3. Order

Write the seed and run the parser with it. Take the Track's `backlog`, `workable` and `withheld`, plus
`runtime_blocked`, `closed_by_rejection`, `roles`, `tools` and `tree.stages`.

## 4. Proposals

Go through the backlog in its order. Each Stage becomes one proposal — its Name, its Purpose in one line,
and what blocks it — unless one of these applies first:

| The Stage | Instead |
| --- | --- |
| already has an open ticket (a scan the call asked for) | no proposal; the ticket stands |
| is in `runtime_blocked` and not rejected | the proposal is to record a rejection with that runtime version as its blocker (`rejection.md`, *Below the runtime floor*) |
| is in `withheld` as closed by a rejection | out of reach: no ticket could unblock it. Named in one line with what it hangs on, no proposal |

**What blocks a proposal** is read from `tree.stages`: every `requires` Stage that is not fulfilled; every
required Role that is not filled, where the Tool recommended for it stands for it; and every `after`
Stage that is undecided. Where a `requires` item is a group of alternatives, its members block together,
and the ticket says that one of them is enough.

**A PHPStan baseline with entries.** A level the target has set up whose baseline still holds findings is
not fulfilled, since the Fulfilment check asks for an empty baseline, and the next level requires it. Its
proposal is titled "PHPStan Level N: shrink the baseline" instead of "Raise to PHPStan Level N"; the check of
a baseline ticket is whether the baseline still has entries.

**Which Tool fills a Role.** The report says, per Role the Track's Stages need, which Tool fills it, and
which Tool is not proposed because another took its place (`tools` marks it `out`).

**A scan the call asked for** also re-judged Stages that have an open ticket: one found fulfilled is laid
out at filing for closing with a note, as selection does at pick-up (`selection.md`).

## 5. Hand on

- **Proposals** → the filing step, in backlog order.
- **None** → say what the scan found — every Stage fulfilled or rejected, or which are out of reach and
  why — and return to Track choice with the Track marked as tried.

The scan is done when every Stage in scope is fulfilled, rejected, proposed, or named as out of reach.
