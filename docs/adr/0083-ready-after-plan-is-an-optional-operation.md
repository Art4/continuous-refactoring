# Ready after plan is an optional operation, set only where the suite posts the plan

> Amends [ADR-0071](0071-tracker-through-operations-tracker-and-forge-apart.md): its rejection of "operations for
> the target's status workflow" stays for the start of work; one trigger is taken in.

Some targets mark a ticket in their tracker once it has an implementable plan: clear a "blocked" column, set a
label. A target with a planning skill of its own does that in the skill. Where the skill cannot run autonomously,
the suite plans with its own procedure and posts the `Plan` comment itself, and nothing marks the ticket.
ADR-0071 rejected status operations because which status a ticket gets when work starts is the target's
convention. That reasoning holds. The moment the plan is on the ticket is different: the design point itself
produces it, and it is the same moment for every target.

## Decision

- **Ready after plan** is an optional operation: how the target marks a ticket ready for implementation, in its
  tracker's own commands. Without it nothing is written.
- **The design point runs it in step 5, after its own successful post of the `Plan` comment**, for every ticket
  that step plans (tooling, baseline, Investigation, other). Not at Claim, not when the target's skill wrote the
  plan, not when a plan already stood, not for Housekeeping.
- **It runs also when the human implements in a session of their own and when the run goes on to the
  implementation.** The post is the trigger, not what follows.
- **It does not run while an open question follows the plan.** Once the answer arrives and the plan is posted
  again, it runs.
- **The bullet must be idempotent**, because a plan posted again triggers it again.
- **A failure does not end the run.** The plan stands; the closing report names the command so the human can
  run it.
- **The templates carry no bullet and the interview does not ask.** Labels and columns are the target's; the
  closing "Left out" line names the operation, and a human who needs it writes the bullet.

## Considered

- **Let the target's `AGENTS.md` or planning skill do it.** Works where the skill runs; not for the autonomous
  case that prompted this.
- **Run it also for plans the target's skill wrote or that already stood.** Rejected — it turns the design point
  into a status reconciliation, which ADR-0071 declined.
- **Ask for it in the onboarding.** Rejected — the interview would ask for status conventions.

## Consequences

A target without the bullet behaves as before. The suite still never sets a status when work starts.
