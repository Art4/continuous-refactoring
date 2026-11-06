# 01 — The field record and the field eval's closing step

Type: task
Status: done
Blocked by: —

**What to build** (spec S1.1, S1.2, S1.4; Q1, Q2, Q11)

- **The record.** `docs/agents/field-results.md`: one table, a row per path of the suite and environment — path,
  environment (kind of project, forge, tracker, agent), suite version, dates, result (confirmed, in progress,
  rejected, miss), and the scenario that covers the path where one does. Anonymous: no project's name, no ticket or
  merge request number. A short head says what counts as a path and how a row is written.
- **The closing step.** `docs/agents/field-eval.md`: at both ends of an eval — six quiet rounds, or the human's stop —
  the observing agent drafts the rows from its log, the maintainer confirms them, and a PR lands them. Only then may
  the log be deleted. A new eval's start checks that the old log is recorded, and stops to ask where it is not.
- **A field case becomes a scenario.** The same file: a miss found in the field becomes a ticket *and* a scenario
  under `docs/agents/evals/`; a newly confirmed path becomes a scenario where it is cheap to rebuild. Both anonymised.
- `docs/agents/evals/README.md`: a line pointing to the record for tests on a real target.

**Done when** the record exists with its head and an empty table, `field-eval.md` carries the closing step and the
start check, and tests and validator are green.

## Comments

> **2026-11-06:** Done. `docs/agents/field-results.md` with *Writing a row* (path, environment by label, version,
> dates, result, scenario, source: trace or maintainer) and empty tables. `field-eval.md` gains *Closing* (draft rows,
> hand them to the human with the paths not seen, land them by PR, name the miss's ticket and scenario, mark the log
> `Recorded: <date>`), a start check for an unrecorded old log, and pointers from *The log* and *Rounds*. Pointers
> from `evals/README.md` and `CONTRIBUTING.md`.
