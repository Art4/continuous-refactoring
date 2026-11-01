# 01 — Scenarios for the Pack route and the Driver

Type: task
Status: done

Part of `../spec.md`, *Evals*. Written before the skill text of tickets 02 and 03, so that text is held against
expectations set beforehand.

**What to build**

`.scratch/driver-and-run-skills/evals/`, one file per scenario: the situation, the call, the expected behaviour as
a checkable list. At least three each.

- **Pack route:** a tool the suite does not know, on an onboarded target; a slug that clashes with the suite's
  (the parser ends in exit code 2); a project not yet onboarded.
- **Driver:** nothing workable and nothing waiting; a ticket that waits on a human and nothing else; a red check
  and a request for changes that needs two reworks; `review only` with three open merge requests; a call with no
  settings (defaults said back, starts without asking); a project without `## Refactoring operations`.

How to play one through: a fresh subagent with the skill, on a fixture or scratch target, nothing written to the
suite (see the note on skill-text experiments in the maintainer's notes: such a dry run changes no real skill
file and no external state).

**Done when** the scenarios exist and tickets 02 and 03 can name the ones they must pass.

## Answer

`../evals/`: `p1` to `p3` for ticket 02, `d1` to `d8` for ticket 03, with `README.md` on how to play them. The Pack
scenarios are played live, the Driver scenarios as walk-throughs, since a fixture has no forge. Two Driver scenarios
more than the ticket named: `d7` (no timer) and `d8` (`merge`). Setups of `p1` and `p2` checked against the parser;
the scenarios themselves can only be played once the skill text exists.
