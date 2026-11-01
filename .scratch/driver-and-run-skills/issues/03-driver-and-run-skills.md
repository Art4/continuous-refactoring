# 03 — `continuous-refactoring` becomes the Driver, `continuous-refactoring-run` the run

Type: task
Status: done
Blocked by: 01, 02

Part of `../spec.md`, *The Driver*, *Skills and references*, *Breaking change*. One pull request: the rename and the
Driver skill belong together. Git rename first, in a commit of its own, so the review can follow it.

**What to build**

- **Rename:** `skills/continuous-refactoring/` to `skills/continuous-refactoring-run/`, references included: `name`
  and description in `SKILL.md`; the paths in `continuous-housekeeping` and its references; `scripts/`
  (`validate_skills.py` with its allow-list keys, `tooling_docs.py`, the tests); the `$schema` lines in `fixtures/`
  and in `own-tool.md`; generated tooling docs; `docs/agents/skill-references.md`.
- **Driver:** a new `skills/continuous-refactoring/SKILL.md` from the prompt in `docs/playbooks/driver.md`, with the
  settings, defaults and rules of the spec. A description that tells a subagent to call the run skill, not this one.
  Merge step: stacked child, merge landed (from `docs/playbooks/reviewer-loop.md`). Rounds, cadence, waiting, first
  call as the spec has them. Longer detail goes one level below `SKILL.md`.
- **Target-facing text:** `Used by /continuous-refactoring` in `refactoring-operations.md` and every template a
  target receives. Tracker files already written keep the old line; harmless, named in the changelog.
- **ADR-0092:** three skills, amending ADR-0075. It records why the main name moved and why the cadence defaults
  on; `docs/adr/README.md` and the banners follow.
- **Vocabulary:** `CONTEXT.md`: *Run* (the skill's name), *Driver*, new *Round* and *Cadence*, `_Avoid_` lines.
- **Docs:**
  - `AGENTS.md` (the suite section).
  - `README.md`: skills table, *How it works*, install (three symlinks), updating, and the doc table, where
    `driver.md` is missing today.
  - `docs/architecture.md` (*Two skills*).
  - `docs/playbooks/driver.md`: no prompt any more; settings, defaults, what waits for you.
  - `docs/playbooks/run.md` (*The call*, *Running it regularly*, "the suite schedules nothing").
  - `docs/playbooks/tracks.md`, `housekeeping.md`, `own-tool.md`.
  - `docs/FAQ.md`: *Why only two skills?*, *Can an agent start a run?*, why a cadence by default.
  - `docs/known-limitations.md`: a session holds a short cadence only; a long one is the user's; a call below the
    cadence and two Drivers side by side are not prevented.
  - `grep` both names across `README.md` and `docs/` once more at the end.
- **Changelog:** a breaking fragment with the steps: add the symlink, and move any call that means one run to
  `/continuous-refactoring-run`.

**Done when** the scenarios `d1` to `d8` of ticket 01 pass, a call with no settings runs review only with five rounds
30 minutes apart, `/continuous-refactoring-run` behaves as the old skill did, and tests and validator are green.

After the merge, outside this repository: add the symlink in every installed target.

## Answer

The rename is a commit of its own; `/continuous-refactoring-run` differs from the old skill only in its name, its
description, a heading and the paths. The Driver is `skills/continuous-refactoring/SKILL.md`, with
`references/merging.md`. ADR-0092 amends ADR-0075.

`d1` to `d8` pass on 83f57b2, all as walk-throughs: no scenario ran on a real forge or with a real timer. Left open on
purpose: `merging.md` names no limit on waiting for CI, and no notification tool is named.
