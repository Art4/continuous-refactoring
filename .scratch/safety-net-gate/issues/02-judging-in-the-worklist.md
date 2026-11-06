# 02 — The worklist judges what applies, once per run

Type: task
Status: open
Blocked by: 01

**What to build** (spec Q3, Q10; ADR-0096)

- **`worklist.md`.** A step of its own, before *A Track's trace* is asked: judge each Pack's *Applies when*, the own
  *Applies when* of the Stages in both tooling Tracks' `nodes`, and the runtime (`track-scan.md`, *Judging*). It may
  run in a subagent. Skipped where the call names a ticket.
- **Its result is reused.** *A Track's trace* leaves out the Stages judged not applicable from it; *The seed from
  the trace* (`tooling-parser.md`) takes `packs`, `not_applicable` and `runtime` from it; `track-scan.md` step 2 and
  the pick-up check in `selection.md` take it instead of judging again. Where no worklist judged — a
  `continuous-housekeeping` run — they judge as before.
- Docs where they describe the worklist or the trace: `docs/playbooks/run.md`, `docs/architecture.md`,
  `CONTEXT.md` (**worklist**) as far as they say what is judged when.
- A changelog fragment.

**Done when** r5 and r1 still pass as walk-throughs, and tests and validator are green.

## Comments
