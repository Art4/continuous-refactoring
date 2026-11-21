# 04 — Tickets filed after the Candidate operation lack its mark

Type: task
Status: open
Blocked by: —

**What was seen**

- During the run the maintainer added a **Candidate** operation to the target's `## Refactoring operations` (a label)
  and labelled every existing suite ticket.
- About twenty minutes later two new suite-style tickets appeared without that label: one for the release-bound task
  of 02, one for an outdated "Known issues" section in the target's `AGENTS.md`. `filing-a-ticket.md` asks for
  "**Marks** — the **Candidate** mark, where the target has that operation".

**Open**

- The cause: the operations read before the change and not read again; or the tickets written by the Driver or its
  review outside `filing-a-ticket.md`. Not known from the forge.
- If the first: whether a run, or the Driver per round, must read the operations afresh. If the second: whether the
  Driver may file tickets at all, or must hand them to a run.
- A change the run wants in `AGENTS.md` is meant to go into the Driver's status as wording for the human
  (step 5); here it became a ticket instead. Part of the same question.

## Comments
