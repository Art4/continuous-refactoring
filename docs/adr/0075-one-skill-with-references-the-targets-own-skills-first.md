# One skill with references, and the target's own skills first

> Supersedes [ADR-0057](0057-refactor-loop-and-per-track-skills.md) (the dispatcher, `refactor-loop` and
> the per-Track skills), [ADR-0010](0010-orchestrator-explicit-data-flow.md) (the data pipe between
> lifecycle skills, and "scan detects, learn writes"),
> [ADR-0038](0038-candidate-selection-moves-to-prioritize.md) (selection as a mode of
> `refactor-prioritize`) and [ADR-0051](0051-refactor-learn-requires-a-genuine-event.md) (the
> precondition of a skill that no longer exists).
>
> Amends [ADR-0003](0003-external-skill-references-carry-a-fallback.md): the fallback stays, but for
> design and implementation the preferred skill is whatever the target has, looked up at the decision
> point, not a fixed list of global skills.
>
> Amends [ADR-0014](0014-tooling-tree-parser-ships-under-refactor-scan.md): the parser and its tree docs
> still ship together under a skill, now one that remains.

The suite was ten skills, eight of them internal, each symlinked into a target and listed among the
developer's skills. The split existed to give each step a context of its own and to keep one skill as the
only writer of the bookkeeping. The second reason is gone
([ADR-0074](0074-state-lives-in-the-tracker-found-by-search.md)); the first does not need a skill.
Meanwhile a target with its own skills for planning and implementing had its refactoring work built
differently from all its other work.

## Decision

Two skills a human calls:

- `continuous-refactoring` — the run.
- `continuous-housekeeping` — the Housekeeping Track alone, with no Track choice, so it can be scheduled.

Both read the same Housekeeping reference. Everything else — Track choice, scan, selection, the per-Track
rules, the fallback design and implement procedures, onboarding — is a reference one of them loads when a
run reaches it. A step that deserves a context of its own is handed to a subagent together with its
reference.

Removed as skills: `refactor-loop`, `refactor-scan`, `refactor-prioritize`, `refactor-design`,
`refactor-implement`, `refactor-learn`, `continuous-safety-net`, `continuous-guardrails`,
`continuous-investigation`. What each knew that still applies becomes a reference.

The rule "only one skill writes" is removed. The scan may act on what it finds, through a decision point.

**The target's own skills first.** At the design and at the implement point the suite looks at the skills
available in the target and at what its `AGENTS.md` says, recommends the target's own, and falls back to
its own references. That choice is a decision point and is never stored: installing a skill tomorrow
changes the recommendation tomorrow. The suite expects from a design skill a ticket carrying an
implementable plan, and from an implement skill a branch with green checks. It opens the merge request
itself unless one already exists, so a run always ends the same way.

An ADR and a glossary change travel in the candidate's merge request, and only where the target's domain
docs say ADRs are kept.

## Considered

- **Keep the internal skills, hide them from the list.** Rejected — the symlinks and their upkeep remain,
  and a step still gets a context of its own through a subagent.
- **One skill only, Housekeeping as a named Track of it.** Rejected — an entry point that needs no Track
  choice is what makes Housekeeping schedulable.
- **Ask once which skills to use and store the answer.** Rejected — it would be the suite's first piece of
  state again, and it goes stale the day a skill is installed or removed.

## Consequences

Installing the suite is two symlinks; a target moving over from 0.6.0 removes the symlinks of the removed
skills. The flow texts are written new from the spec instead of being transformed from the old skills. No
tests were written or changed; the validator, the trigger-control tests and the fixture harness are left
red where the rebuild breaks them until the decision about tests.
