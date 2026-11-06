# 08 — Cut rationale and repeated preambles, then a word budget

Type: task
Status: open
Blocked by: 07

**What to build** (spec S4.3, S4.4; Q20)

- **Rationale.** Sentences that explain why a rule is so leave the runtime text; the reason lives in the ADR. A reason
  stays where a scenario fails without it. Decide here where rationale goes that a model needs.
- **Preambles.** The opening most references repeat on how a decision point is laid out becomes a pointer to the
  run's `SKILL.md`, *Decision points*.
- Thin out section jumps where a pointer is not needed.
- Every cut played against the affected scenarios.
- **The budget.** Last: `validate_skills.py` checks a word limit per reference, with targets taken from ticket 07's
  numbers and this ticket's cuts. A unit test.
- A changelog fragment.

**Done when** the cuts are in, the affected scenarios pass, the budget check is in, and tests and validator are green.
