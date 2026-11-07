# 01 — Is a tooling Track's scan due while it has open tickets?

Type: task
Status: open
Blocked by: —

**What happened.** A walk-through of r7 (2026-11-07) and an earlier field observation of the maintainer hit the
same question: Guardrails had open tickets, while several of its Stages that apply had no ticket at all. Was a scan
due for those Stages?

**Where the text disagrees.**

- `skills/continuous-refactoring-run/references/worklist.md`, *A Track's trace*: the trace is "asked only of a Track
  with no open ticket".
- `skills/continuous-refactoring-run/SKILL.md`, step 5, and `references/track-choice.md`, the Safety Net / Guardrails
  row: the scan runs "only when the Track has no trace yet".

For a Track with open tickets the trace is never asked, so "no trace yet" is neither true nor false. A reader can take
it either way. If it is read as "not due", a Stage without a ticket is not filed until every open ticket of its Track
is closed. If it is read as "due", the run scans beside open work.

**What to build**

- Decide which is meant, and why. Is a Track's open work finished before new Stages are filed, or are Stages without
  a ticket filed beside it?
- Make `worklist.md`, the run's `SKILL.md` step 5 and `track-choice.md` say the same.
- A scenario under `docs/agents/evals/`: a tooling Track with an open workable ticket and a Stage that applies and is
  not known, expecting the decided behaviour.
- Docs where they describe when a scan runs (`docs/playbooks/tracks.md`, `docs/playbooks/run.md`), and a changelog
  fragment if the behaviour changes.

**Done when** the three places agree, the scenario passes, and tests and validator are green.
