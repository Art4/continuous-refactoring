# Psalm Taint Analysis is a Guardrails Stage

> Amends [ADR-0054](0054-onboarding-safety-net-and-signal-wave.md), which rejected moving `psalm-taint-analysis` out of the Safety Net.

ADR-0054 kept the Stage in the Safety Net because its findings are the kind structural work collides with. The criterion
points the other way: the Safety Net is settled so that structural work can start, and a taint finding in the target's
own code is often fixed only by restructuring (moving the escaping to one place, splitting a function that mixes input
handling with output). Such a Stage waits on its own precondition: the Safety Net cannot be fulfilled until the findings
are fixed, and they cannot be fixed before the Safety Net is fulfilled. The only way through was to skip the Stage.

## Decision

- **`psalm-taint-analysis` is a Guardrails Stage.** It keeps its `requires` (PHPStan Level 4 or Psalm, both Safety Net
  Stages) and is worked once the Safety Net is fulfilled, where the restructuring it may need is possible.
- **The Role's Signal is unchanged.** Security still feeds the search for structural candidates once the Stage is adopted.

## Considered Options

- **Keep it in the Safety Net and skip it by rejection.** Loses the Stage and its Signal for a reason that is not a
  rejection of the Tool. Rejected.
- **Keep it in the Safety Net and adopt it with a baseline of today's findings.** Hides the findings that most need
  the structural work. Rejected.

## Consequences

- The Safety Net no longer waits on a Stage whose findings need work the Safety Net forbids.
- A target can run structural work before the first taint scan; Semgrep, already a Guardrails Stage, covers the Security
  Signal in the same phase.
