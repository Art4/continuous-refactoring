# 12 — "Baseline ticket" has no definition

Type: task
Status: done
Blocked by: —

**What the plays showed** (r7 and r8 on 2026-11-11, named by both, so a ticket under Q54). Several Tool files give
their ticket "the shape of a baseline ticket" (ESLint's suppressions and rollout, the PHP CS Fixer and PHPMD rollouts),
`planning-a-baseline-ticket.md` plans one, but the glossary has no entry, and `implement-point.md` says a rollout
ticket "is built like a tooling ticket". The players could not tell whether a rollout ticket counts as a baseline
ticket, whether its parts skip the design steps a plan-less ticket has, and whether a part skips the Housekeeping
slice `design-point.md` asks of a Tool with a Housekeeping field.

**What to build**

- A glossary entry: a ticket that stays open across many merge requests, each a part, for a Stage whose state
  shrinks step by step (a baseline, a suppressions file, rules marked `Not yet:`).
- `implement-point.md` and `design-point.md` say what such a part keeps and skips; the Tool files point to the entry
  instead of "the shape of".

**Done when** the entry is in, the references agree, the scenarios that cover them pass, and tests and validator are
green.

## Comments

**2026-11-11 — Done** (Q55–Q57). r7 and r8 pass at 6011078.
