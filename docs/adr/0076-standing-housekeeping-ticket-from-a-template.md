# Housekeeping is one standing ticket, made from a template in the target

> Supersedes in part [ADR-0037](0037-continuous-housekeeping-skill-and-node-housekeeping-contributions.md)
> (the cadence field, the one-question setup, one issue per due cycle and where the template lives; a
> node's `Housekeeping` field and its contribution through the node's own merge request stand),
> [ADR-0055](0055-purpose-based-fulfilment-and-scheduled-tracks.md) (Housekeeping's `Cadence` and
> `Last scan`, and the retirement of `continuous-housekeeping` as an entry point) and
> [ADR-0043](0043-secret-history-scan-as-process-step.md) (the scan as a one-time step of the scan
> remembered by a flag; reusing the target's scanner and its own baseline stands).

Housekeeping was due by a cadence and a `Last scan` date in the bookkeeping document, and the secret scan
over history ran once, remembered by a flag in the same document. With no state of the suite's own
([ADR-0074](0074-state-lives-in-the-tracker-found-by-search.md)) both need another home. Ideas an agent
noticed during feature work had no home at all.

## Decision

There is always one open **Housekeeping ticket** per **Housekeeping template**.

- The template is a file in the target. Where it lives and how the next ticket is made from it are the
  target's, written as the **Housekeeping** operation.
- The template holds the recurring tasks, the rhythm, and as its last item "create the next Housekeeping
  ticket". The new ticket states from when it is due. The cycle carries itself: the open ticket is the
  state.
- The rhythm is chosen by the human when Housekeeping is first set up, with a recommendation drawn from
  the target. Several templates with different rhythms may exist side by side.
- Tooling-tree nodes keep contributing their Housekeeping line to the template through their own merge
  request.
- A run works the recurring tasks and the comments on the ticket. Each comment is carried out in one or
  more commits of its own; one too big for Housekeeping is proposed for a ticket of its own.
- The secret scan over the Git history is a task in the template: the whole history the first time,
  afterwards the commits since the last Housekeeping ticket.
- A line in the target's `AGENTS.md` tells every agent to propose refactoring ideas as a comment on the
  open Housekeeping ticket, after the human allowed it. With two open tickets the human chooses, the
  younger recommended.
- Mechanism missing → the Track proposes to set it up: the template, the first ticket, the `AGENTS.md`
  line. The `AGENTS.md` line is written only after a human agreed, in an autonomous run too.

The Track is recommended when its open ticket's due date is reached, or when the mechanism is missing.
`continuous-housekeeping` is an entry point of its own; the suite schedules nothing.

## Considered

- **Derive "due" from the date of the last closed Housekeeping ticket and a stored rhythm.** Rejected —
  the rhythm would need a place outside the template, and a ticket that states its own due date needs no
  arithmetic.
- **Open a ticket only when a cycle is due.** Rejected — between cycles there would be nowhere to leave
  an idea.
- **Keep the secret scan as a one-time step.** Rejected — "already done" is a flag someone has to keep;
  as a recurring task it also covers history that arrived since.
- **Let agents comment without asking.** Rejected — a comment on a tracker is a write the human did not
  ask for.

## Consequences

`CONTEXT.md` gains **Housekeeping ticket** and **Housekeeping template**; the **Housekeeping** entry loses
its cadence. A cycle without changes closes its ticket with a comment.
