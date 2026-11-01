# The Driver becomes the main skill; a run gets its own

**Status:** open — tickets 01–04

Grilled 2026-11-01. The ADR comes with ticket 03.

## Problem Statement

A skill knows nothing of `docs/playbooks/`, so whoever wants an agent to drive runs, build a Pack or watch a
run has to point it at a doc that never ships. Two of those docs are misfiled by the suite's own rule (what an
agent reads lives under `skills/`, what a human reads under `docs/playbooks/`): `driver.md` holds a prompt that
is a skill in disguise and goes stale in every copy, and `reviewer-loop.md` is nearly all agent instruction.
`own-tool.md` really is for humans, but no skill leads an agent to what it needs.

The name is off as well: `continuous-refactoring` does one run and stops; what continues is the Driver.

## Solution

Everything an agent executes moves under `skills/`, or to `docs/agents/` where it is a maintainer tool. The
playbooks keep only what a human reads to steer.

- `continuous-refactoring` becomes the **Driver**. `continuous-refactoring-run` is one **run**, as the old skill
  was. `continuous-housekeeping` keeps its name: there is no Housekeeping loop to tell apart from it.
- A new call of the run skill builds a target's own Pack and ends in one merge request.
- The reviewer loop becomes a **field eval**: a maintainer tool, not a skill, not shipped.
- Skill text is checked against hand-written scenarios before it merges.

## Terms

- **Run** — unchanged: ends when its merge request is open, or earlier (nothing workable, an open question).
- **Round** — one unit of the Driver: a run, its review, and rework. It ends when the merge request is
  mergeable (`review only`), merged (`merge`), or handed to the human after two reworks. A round holds up to
  three runs.
- **Cadence** — the wait between two rounds. Not within a round. Not Housekeeping's rhythm (when its ticket is
  due), and not a schedule (when something outside calls a skill).

## Decisions

### The Driver

| Setting | Default | The call can say |
|---|---|---|
| Merge | `review only` | `merge` |
| End | five rounds | a number of rounds, of merged merge requests, a time, or "until nothing is workable" |
| Cadence | 30 minutes | another duration, or "no pause" |
| Call | none: each run makes its own Track choice | a Track or a restriction |
| Log | none | a file the repository ignores |

- **It starts without asking.** It says back in one sentence what it understood.
- **Stops stay as in the playbook**: nothing workable; a run failed; a dirty tree after a run; two runs in a row
  without a merge request and without a new waiting ticket; with `review only`, more than three of its merge
  requests open.
- **The first call** on a project without a `## Refactoring operations` section runs onboarding in the main
  session, by invoking `continuous-refactoring-run` there, and then stops as a run does: commit, call again.
- **Waiting:** in the session with the environment's timer where it has one. Otherwise the Driver ends and says
  when the next round is due. A long cadence, and whatever keeps it alive, is the user's: it depends on the
  repository, the agent and the system.
- **No guard against a short interval.** How often the skill is called is the user's. The suite does not prevent
  a call below the cadence, nor two Drivers side by side. `docs/known-limitations.md` says so.
- **Why a cadence at all, and a default one:** runs not yet moved to the new name get a chance to be noticed and
  changed after the breaking change; rate limits and CI costs are real; and the suite is meant to keep a project
  refactored slowly and steadily, beside other agents and humans, not as fast as possible.
- **Merge checks** proven in the reviewer loop move into the Driver's merge step: a stacked child before a
  branch is deleted, and that the merge really landed the branch's content.

### Skills and references

All references move to `skills/continuous-refactoring-run/references/`; the Driver reaches them by
`../continuous-refactoring-run/`. A target's own Pack changes one line (`$schema`). No project of the
maintainer's has a Pack yet.

### The Pack route

A call such as "a Pack of its own for Deptrac" leads from `continuous-refactoring-run` to a new
`references/own-pack.md`: Pack directory, Tool files, the **Tooling Pack** bullet, the check with `--own-pack`,
one merge request. It skips worklist and Track choice, and the run ends there.

### The field eval

`docs/playbooks/reviewer-loop.md` becomes `docs/agents/field-eval.md`, started from this repository.

| Reviewer loop | Field eval |
|---|---|
| Anomaly detection | Expected behaviour, a fixed checklist |
| Personas | Test conditions: **Gatekeeper** (today's strict one), **Observer** (today's observer-only), **Project reviewer** |
| Findings log | The result, per round |

**Project reviewer** judges with a review skill: the target's, otherwise a global one such as `code-review`. Where
none can be called, the eval says so at the start and asks for another persona. The benevolent and the
security-focused persona go.

### Evals

Scenarios by hand: a situation and the expected behaviour, written before the skill text and played through by a
fresh subagent before the merge. First for the Pack route and the Driver. They live in
`.scratch/driver-and-run-skills/evals/` while they are the acceptance of this work, and move to `docs/agents/evals/`
with ticket 04: they stay regression tests for later changes to the skill text. No runner and no CI step.

### Reference depth

Existing references stay as they are. New text keeps to one level below `SKILL.md`. Act on the rest only once an
agent is seen reading a nested file in part.

## Considered and rejected

- **Ship the playbooks under `references/`.** A reference is reached only through a `SKILL.md`, so this alone
  gives an agent no way in.
- **Point at `docs/` through the symlink, or at a GitHub URL.** The first needs a local checkout, the second can
  drift from the installed version.
- **A skill `continuous-driver`, names unchanged.** No risk, but the main name keeps saying what it does not do.
- **Ship the reviewer as a skill.** Only ever used to develop the suite; its value in a target is untested, and
  the Driver covers review there. Can follow if a need shows.
- **A repository-local reviewer skill.** A new kind of file for what a path in a prompt does.
- **A daily default cadence.** Too long: a session cannot hold it reliably (Claude Code's wake-up reaches one hour
  per step, its session jobs end with the session).
- **Reading the last round's time from the forge to enforce the cadence.** How often the skill is called is the
  user's to decide.
- **A cadence on every run, rework included.** The cap of two reworks bounds their cost; the cadence is between
  rounds.

## Breaking change

- `/continuous-refactoring` no longer means one run. A scheduled `/continuous-refactoring do it yourself` now
  starts a Driver: review only, five rounds, 30 minutes apart.
- A target adds a symlink for `continuous-refactoring-run`; the existing one stays and now holds the Driver.
- Every installed target is affected and needs the symlink.

## Out of Scope

- Automated evals, a runner, a CI step.
- Reworking nested references.
- A target's own schedule, or keeping a session alive for a long cadence.
- Reviewing runs the Driver did not start.
