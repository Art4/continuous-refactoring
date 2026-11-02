# 01 — The Opener

Type: task
Status: open
Blocked by: —

**What to build** (ADR-0093, spec Q19–Q23, Q25)

- **The Tool file section.** `tooling-model.md`: a Tool file of a Tool on request may name an *Opener* — the
  situation in a run where the Tool would have paid off, judged by the agent.
- **Writing it.** Where a plan is made (`design-point.md`, and the plan of a tooling ticket): when a Tool on request
  that is not in place names an Opener that holds, the plan writes `Opener: <tool> — <why>` under `Decisions`. One
  line per Tool; nothing else changes in the plan.
- **Finding it.** `worklist.md`, *A Track's trace*: a Stage on request with an Opener found through **Search** counts
  as not known, so its Track's scan is due. `track-scan.md`, *Tools on request*: such a Stage is in scope. Decide
  whether the parser's seed needs the Openers (`tooling-parser.md`) or the scan's scope is enough.
- **Using it up.** A ticket of the Tool in any state, or a recorded rejection of the Tool, its Stage or its Role
  (`rejection.md`). After a rejection, no Opener proposes it again; a call naming the Tool still can.
- **Filing it.** `filing-a-ticket.md`: a proposal from an Opener is filed as a ticket that waits for a human's yes,
  in an autonomous run too, with the question "Set up <Tool>?" and the Opener with a link to its plan. It is not
  workable before the answer (design point, *Open questions*).
- `CONTEXT.md`: the term **Opener**, with *Avoid*: trigger; the status on request in **Tool**: "proposed only when a
  human asks for it, or as a question once an Opener was seen".
- **Scenarios.** `docs/agents/evals/r1-opener-seen.md` and `r2-opener-after-rejection.md`, walk-throughs, with
  the prefix `r` explained in the README's table. Both need an Opener to exist, so they are played with ticket 02's
  `bc-promise` or a Tool file stub in the walk-through's state.
- Docs: `docs/playbooks/tracks.md` (on request and the Opener), `docs/FAQ.md` (why a Tool on request is sometimes
  proposed after all), `docs/architecture.md` where it describes on request.

**Done when** r1 (an Opener line in a plan → the next scan files a waiting ticket, no merge request) and r2 (an
Opener after a rejection → nothing filed) pass as walk-throughs, and tests and validator are green.
