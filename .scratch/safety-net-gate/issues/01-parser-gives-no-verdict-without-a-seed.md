# 01 — The parser gives no verdict without a seed

Type: task
Status: done

**What to build** (spec Q2, Q7, Q8; ADR-0096)

- **`tooling_tree.py`.** `compute()` with `seed is None` returns no `safety_net_fulfilled`, and per Track no
  `backlog`, `workable`, `withheld` and `fulfilled`. It keeps what the Packs alone say: `nodes`, `tree`, `tools`,
  `roles`, `packs`, `prerequisites`. Decide per remaining key (`runtime_blocked`, `reversals`,
  `closed_by_rejection`) whether an empty seed says something true; drop it where not. The CLI follows.
- **Unit tests** in `scripts/test_tooling_tree.py`: a seedless call carries no verdict key; a call with an empty
  seed file still does (an empty seed is a judgement: nothing fulfilled).
- **`tooling-parser.md`.** *Calling it* and *What it returns*: the seedless call is the structure — Stages,
  order, Tools, Roles — and answers nothing about fulfilment; the verdict keys come only with `--seed`.
- **`selection.md`** step 1: order by the Stage's position in the Track's `nodes`.
- Check `worklist.md`, `track-scan.md` and `own-pack.md` still read only keys the seedless call has.
- A changelog fragment.

**Done when** tests and validator are green, and no reference reads a verdict from the seedless call.

## Comments

> **2026-11-06:** Done. Without a seed `compute()` drops `safety_net_fulfilled`, `runtime_blocked`, `reversals`,
> `closed_by_rejection`, every Track key but `nodes`, a Role's `filled_by` and a Tool's `out`: each depends on what
> was judged. `prerequisites` stays, the parser reads it from the file itself. Found on the way: the pick-up check in
> `selection.md` read `runtime_blocked` from the seedless call, where it was always empty; it now reads it from the
> call with the seed from the trace.
