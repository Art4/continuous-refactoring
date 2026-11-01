# 04 — The reviewer loop becomes a field eval

Type: task
Status: open
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

**Done when** a round of the field eval can be played from the file alone, nothing outside `docs/adr/` names the
old file, and tests and validator are green.
