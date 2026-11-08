# 08 — Cut rationale and repeated preambles, then a word budget

Type: task
Status: done
Blocked by: 07

**What to build** (spec S4.3, S4.4; Q20)

- **Rationale.** Sentences that explain why a rule is so leave the runtime text; the reason lives in the ADR. A reason
  stays where a scenario fails without it. Decide here where rationale goes that a model needs.
- **The glossary.** Every entry cut to its meaning at runtime, in one to three sentences; *Avoid* stays a list of
  words without their history. A term's history and reasons go to the ADRs where they are missing there. A rough
  target is half its size, the number taken from ticket 07.
- **Preambles.** The opening most references repeat on how a decision point is laid out becomes a pointer to the
  run's `SKILL.md`, *Decision points*.
- Thin out section jumps where a pointer is not needed.
- Every cut played against the affected scenarios.
- **The budget.** Last: `validate_skills.py` checks a word limit per reference, with targets taken from ticket 07's
  numbers and this ticket's cuts. A unit test.
- A changelog fragment.

**Done when** the cuts are in, the affected scenarios pass, the budget check is in, and tests and validator are green.

## Comments

**2026-11-08 — narrowed** by Q30–Q33 after ticket 07's numbers: the glossary stays as it is (no run opens it), no
rationale sweep (little to cut; the rule is in `CONTRIBUTING.md`), section pointers stay. Done here: the eleven
preamble copies became a one-line pointer (about 400 words); `word_budget_issues` checks one limit per skill file,
its size plus a tenth, with unit tests. Plays: r8 and r3, on the maintainer's go.
