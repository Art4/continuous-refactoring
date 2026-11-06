# 03 — Track choice checks its stop, and names only the Safety Net's tickets

Type: task
Status: open
Blocked by: 01

**What to build** (spec Q4, Q5, Q6, Q11, Q12, Q14; ADR-0096)

- **`track-choice.md`**, *The recommendation*: where the answer came from the trace seed and is "not fulfilled",
  every Stage of the Safety Net backlog has an open ticket — or the Track counts as having no trace, its scan is
  due, and Safety Net has something. The check does not apply to the answer from this run's scan.
- **The stop.** An autonomous run ends with "Safety Net is unfinished", followed by the Safety Net's tickets alone:
  in review with their merge requests, blocked with the reason, waiting with the reason. *Coming back here* reads
  the same.
- **Docs**, with the same wording: `CONTEXT.md` (**Track**), `docs/FAQ.md`, `docs/playbooks/run.md`,
  `docs/playbooks/tracks.md`, the troubleshooting row in `docs/known-limitations.md`.
- **Scenario** `docs/agents/evals/r7-safety-net-met-guardrails-open.md`, a walk-through, in the README's table.
  An application target; every Safety Net Stage that applies has a closed ticket; no `roave-bc-check` ticket; two
  open Guardrails tickets, one with an open merge request. Expected: `roave-bc-check` in `not_applicable`; Safety
  Net has a trace; the answer from the trace seed is fulfilled; the run recommends the free Guardrails ticket and
  does not end on Safety Net. Variant: one Safety Net Stage never had a ticket → its scan is due, the run does not
  end.
- A changelog fragment. The PR closes #234.

**Done when** r7 passes in both variants, r5 still passes, and tests and validator are green.

## Comments
