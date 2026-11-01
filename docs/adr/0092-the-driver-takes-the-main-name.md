# The Driver takes the main name; a run gets a skill of its own

> Amends [ADR-0075](0075-one-skill-with-references-the-targets-own-skills-first.md): the suite is three skills. The
> run keeps every reference, and moves to `continuous-refactoring-run`.

`continuous-refactoring` did one run and stopped; what continued was the Driver, a prompt in a playbook that every
copy let go stale. The playbook was an agent's instruction filed where no skill can reach it, so an agent had to be
pointed at a doc that never ships.

## Decision

- **`continuous-refactoring` is the Driver.** It works rounds, starts without asking, and says back what it took.
  `continuous-refactoring-run` is one run, as the old skill was. `continuous-housekeeping` keeps its name.
- **A round** is a run, its review and rework, up to three runs. Rework has no cadence, and the end counts rounds.
- **Defaults:** `review only`, five rounds, 30 minutes between rounds, a stop at more than three open merge requests.
- **The cadence defaults on,** for three reasons: a job not yet moved to the new name gets a chance to be noticed
  after the breaking change; rate limits and CI costs are real; and the suite is meant to keep a project refactored
  slowly and steadily, beside other agents and humans, not as fast as possible. The default shows that this works.
- **Waiting** is in the session with the environment's timer, otherwise the Driver ends and says when the next round
  is due. A long cadence is the user's. Nothing prevents a call below the cadence, or two Drivers.
- **The merge checks** that proved themselves in review move into the Driver: a stacked child before a branch is
  deleted, and that the merge landed the branch's content.
- **All references stay with the run.** The Driver reaches them through `../continuous-refactoring-run/`.

## Considered options

- **A skill `continuous-driver`, names unchanged.** No breaking change, but the main name keeps saying what it does
  not do.
- **`continuous-refactoring-once`.** "Run" is already the suite's word.
- **No default cadence.** Fastest, but it makes the fast case look like the intended one.
- **A daily default.** Too long: a session cannot hold it, and the session jobs of an environment end with the session.
- **A guard against a call below the cadence.** It would need a state the suite does not keep, and how often the skill
  is called is the user's.

## Consequences

A breaking change: an installed target needs a third symlink, a call that means one run moves to the new name, and a
target's own Pack changes its `$schema` line. A call of the old name still does something, a Driver instead of a run;
the defaults keep that safe, since it merges nothing and stops by itself.
