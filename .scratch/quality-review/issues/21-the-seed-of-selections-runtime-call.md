# 21 — Which call selection's runtime check takes

Type: task
Status: open
Blocked by: —

**What the plays showed** (ticket 13's plays, ticket 17's play, r7 A for ticket 18; named three times, so a ticket
under Q81). `selection.md` reads "a call whose seed holds the Packs and the runtime judged this run (`worklist.md`,
*5. Judge what applies*) for what the runtime blocks". Players were unsure whether the seeded call Track choice or the
trace already made counts, or whether selection makes a call of its own, and with which lists: only `packs`,
`not_applicable` and `runtime`, or the seed from the trace. In the plays both gave the same answer.

**To decide**

- Whether selection reuses this run's seeded call where one was made, and makes its own only where none was.
- What its own call's seed holds: the Packs, `not_applicable` and the runtime alone, since `runtime_blocked` depends
  on nothing else.

**Done when** `selection.md` names the call it reads, the scenarios that cover selection pass, and tests and
validator are green.
