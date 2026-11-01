# 04 — The reviewer loop becomes a field eval, and the scenarios move in beside it

Type: task
Status: done
Blocked by: 03

Part of `../spec.md`, *The field eval*.

**What to build**

- `docs/playbooks/reviewer-loop.md` moves to `docs/agents/field-eval.md`, with a maintainer's framing: what it
  tests, started from this repository, what it is not (a skill, shipped, or for a target).
- *Anomaly detection* becomes the fixed checklist of expected behaviour, one verdict per round: pass, miss,
  anomaly. Add what a run should now do that the list does not name.
- Personas: **Gatekeeper**, **Observer**, **Project reviewer**, as test conditions. Drop the benevolent and the
  security-focused one. Project reviewer's fallback as the spec has it; a skill only a human can call does not
  count as callable, and a target's own skill needs a checkout of the target.
- Merge checks stay in the Driver (ticket 03): point at them, do not repeat them.
- Rules that so far live only in the maintainer's notes go in: everything on the forge in English; a request for
  changes describes the problem and its cause and leaves the fix open, so the watched agent's own solution stays
  observable. Line 112's "concrete, actionable reason" follows.
- All headings in English; the anomaly heading becomes `## ⚠️ Anomaly`. Keep the findings log's path under `.scratch/`.
- `scripts/validate_skills.py`: drop `DOC_SCRATCH_ALLOW` and its entry, with its test. `docs/agents/` is already
  exempt from the citation rules.
- `README.md`: the doc table loses the reviewer-loop row. `grep` for the old name outside `docs/adr/`.
- `CONTRIBUTING.md` names the field eval as the way to test a suite change on a real target.
- `../evals/` moves to `docs/agents/evals/`. Its `README.md` loses the pointers to `../spec.md` and the note on the
  skill's name before ticket 03; a scenario then changes when the behaviour it expects is meant to change.
- `CONTRIBUTING.md` says: a change to skill text plays the scenarios that cover it before the merge.

**Done when** a round of the field eval can be played from the file alone, nothing outside `docs/adr/` names the
old file, the scenarios play from `docs/agents/evals/` with no `.scratch/` file to hand, and tests and validator are
green.

## Answer

`docs/agents/field-eval.md` replaces the playbook, and `docs/agents/evals/` holds the scenarios, which now read
without this folder. The list of expected behaviour gained lines for what a run and a Driver should do. `.gitignore`
covers the findings logs, since a log names its target and no committed file does. Maintainer rules that lived only
in notes went in as well: the forge in English, a request for changes that leaves the fix open, a status per round, a
fresh log per eval, the checkout held still. The field eval itself has not been played.
