# safety-net-gate

An autonomous run ended with "Safety Net is waiting for merges" on a target whose Safety Net was met: a later
Safety Net scan with a judged seed reported it fulfilled with an empty backlog (GitHub issue #234). Grilled on
2026-11-06 (`/grill-me`). One new ADR (0096), amending ADR-0079.

## Why

The rule is already right: `tooling-parser.md`, *Is Safety Net fulfilled?*, reads the answer from this run's scan or
from a call with the seed from the trace, never from the seedless call. Three gaps make the wrong answer easy:

1. **The seedless call answers anyway.** `worklist.md` step 1 runs the parser without a seed in every run, before
   Track choice. With every Stage undecided its output still carries `safety_net_fulfilled: false`, a Safety Net
   `backlog` of every Stage, and Guardrails `withheld` reasons ("waiting on the Safety Net"). That verdict sits in
   the agent's context when Track choice asks the question.
2. **The trace seed needs judging no step asks for.** *The seed from the trace* takes `packs`, `not_applicable` and
   `runtime` "judged this run (`track-scan.md`, *Judging*)", and the trace check in `worklist.md` needs the same
   *Applies when* judging — but outside a scan no step says when to judge them. Skipped, every Pack applies, and a
   Stage out of scope (`roave-bc-check` on an application) stays undecided: `safety_net_fulfilled: false`.
3. **The stop does not check itself.** With a correct trace, the trace seed's answer is false only because Stages
   of the backlog have an open ticket: a Stage in the backlog without one is not known, so there is no trace and the
   scan is due. And the stop message lists "the tickets in review with their merge requests" of any Track, so
   Guardrails merge requests read as what blocks the Safety Net.

## Decided

| # | Decision |
|---|---|
| Q1 | A design PR (this spec, ADR-0096), then three tickets with a PR each |
| Q2 | Gap 1 is fixed in the parser, not in prose: without a seed it gives no verdict |
| Q3 | Gap 2: a step of its own in `worklist.md`, once per run, before the trace check |
| Q4 | Gap 3: the stop "not fulfilled → end the run" holds only when every Stage of the Safety Net backlog has an open ticket; otherwise the Track counts as having no trace and its scan is due |
| Q5 | The stop says "Safety Net is unfinished" and lists the Safety Net's tickets alone, grouped: in review with the merge request, blocked with the reason, waiting with the reason |
| Q6 | Besides the parser's unit test, a scenario walk-through of the issue's shape |
| Q7 | `compute()` gives no verdict where `seed is None`, so the CLI without `--seed` too: no `safety_net_fulfilled`; per Track no `backlog`, `workable`, `withheld`, `fulfilled`. The structure stays: `nodes`, `tree`, `tools`, `roles`, `packs`, `prerequisites`, `runtime_blocked`, `reversals`, `closed_by_rejection` where the parser computes them from the Packs alone — ticket 01 settles which keys stay by what an empty seed can honestly say |
| Q8 | `selection.md` step 1 orders by the Stage's position in the Track's `nodes`, not its `backlog` (both follow `stage_order`; `nodes` also lists on-request Stages) |
| Q9 | One ADR for all three: the gate question is answered only from a judged state |
| Q10 | The worklist's judging step judges each Pack's *Applies when*, the own *Applies when* of the Stages in both tooling Tracks' `nodes`, and the runtime. It may run in a subagent. A later scan, the pick-up check and the trace seed take its result instead of judging again; where no worklist judged (a `continuous-housekeeping` run), they judge as before. It is skipped where the call names a ticket: no Track choice, no trace |
| Q11 | The check of Q4 applies only to the answer from the trace seed. From this run's scan every Stage is judged; a declined proposal is a rejection, so not in the backlog |
| Q12 | The new wording goes into `CONTEXT.md`, `docs/FAQ.md`, `docs/playbooks/run.md`, `docs/playbooks/tracks.md`, and the troubleshooting row of `docs/known-limitations.md` |
| Q13 | This folder; tickets 01 (parser), 02 (judging in the worklist), 03 (Track choice); 02 and 03 build on 01; each PR has a changelog fragment; the PR of 03 closes #234 |
| Q14 | Scenario `docs/agents/evals/r7-safety-net-met-guardrails-open.md`, a walk-through with two variants, in the evals README's table |

## Facts

- The seedless call is read by `worklist.md` (step 1, the Stages of `tracks`), `selection.md` (the `backlog`
  order), `track-scan.md` (step 1, scope) and `own-pack.md` (what the suite knows). None of them needs a verdict
  from it except `selection.md`'s order, which `nodes` gives as well.
- The unit tests call `compute()` almost always through a helper that hands in a full seed; real seedless calls
  are rare in `scripts/test_tooling_tree.py`.
- In the PHP Pack `roave-bc-check` is a Safety Net Stage that applies to libraries only.
- A Stage fulfilled at its first scan gets no ticket and so never becomes known (ADR-0079): on a target that had
  its Safety Net from the start, the Safety Net scan is due in every run. That is the design and stays.
- The Driver does not read the stop message.

## Tickets

- `issues/01-parser-gives-no-verdict-without-a-seed.md`
- `issues/02-judging-in-the-worklist.md` (blocked by 01)
- `issues/03-track-choice-checks-its-stop.md` (blocked by 01)
