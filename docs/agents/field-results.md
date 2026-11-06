# Field results

What the suite has done on real targets, path by path. The [scenarios](evals/README.md) test the skill text in a
made-up situation; this record says where a path has held, or failed, in the field. A path nobody has seen in the
field is missing here, and is a candidate for a scenario.

A maintainer's record: it does not ship. Rows come from the closing step of a [field eval](field-eval.md), or from a
maintainer who saw the path run.

## Writing a row

- **Path** — a step or situation of the suite as a reader of the skills would name it: onboarding, a Track, a Stage
  or a group of Stages, the design point's plan, rework after a request for changes, a base update, Housekeeping
  set up or worked, the Driver's review, a scenario's situation.
- **Environment** — described, never named: the kind of project (application or library, language, framework), the
  forge, where the tickets live, the agent. The same environment keeps one short label (E1, E2, …) across rows, kept
  in the list under *Environments*.
- **Version** — the suite release the run used, or a range.
- **Dates** — when it ran, as a date or a range.
- **Result** — **confirmed**, **in progress**, **rejected** (the human declined it, and the rejection was recorded),
  or **miss** (the suite went wrong; the row says how, and names the ticket's subject, not its number).
- **Scenario** — the scenario that covers the path, where one does.
- **Source** — *trace* when it shows on the forge or tracker, *maintainer* when a maintainer confirms what no trace
  shows.

No row names a project, a repository, a person, or a ticket or merge request number.

## Environments

| Label | Environment |
|---|---|

## Results

| Path | Environment | Version | Dates | Result | Scenario | Source |
|---|---|---|---|---|---|---|
