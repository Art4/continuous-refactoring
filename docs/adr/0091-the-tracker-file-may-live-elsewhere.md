# The tracker file may live elsewhere, named in `AGENTS.md`

> Amends [ADR-0071](0071-tracker-through-operations-tracker-and-forge-apart.md): the `## Refactoring operations`
> section lives in the **tracker file**, `docs/agents/issue-tracker.md` only by default.

The suite read its operations from `docs/agents/issue-tracker.md` and nowhere else: the parser held the path as a
constant, the skill text named it at every step. A target that describes its tracker in another file had no way to
say so; the onboarding wrote a second description at the fixed path. The domain docs already had the way out this
lacked: `docs/agents/domain.md`, or what the target's `AGENTS.md` names in its place.

## Decision

- **The tracker file** is the file that says how an agent reaches the tracker and holds the `## Refactoring
  operations` section. `CONTEXT.md` gains the term; the skill text and docs use it and name the path only where the
  rule is stated, once, in `refactoring-operations.md`. `continuous-housekeeping` cites the same rule.
- **Where it is**: the file `AGENTS.md` names for the issue tracker, in its own words, as for the domain docs; where
  `AGENTS.md` names none, the one `CLAUDE.md` names; where neither does, `docs/agents/issue-tracker.md`. Existing
  targets change nothing.
- **`AGENTS.md` and `CLAUDE.md` name different files**: `AGENTS.md` wins; the contradiction is a finding at the Ready
  decision point, the run goes on.
- **A pointer wins over the default file** where both exist; the default file goes unmentioned.
- **A pointer to a file that does not exist** holds: the onboarding writes the section there.
- **A pointer that leaves the repository** — a URL, a path outside it — ends the run, naming the pointer. Falling back
  to the default would write a second description while the human takes the other one for the source.
- **The parser takes `--tracker-file <path>`**, relative to the target, resolved by the agent as the target's own
  Pack is; without it, the default. The parser reads no prose.
- **Paths in the section** (**BC promise**, **Tooling Pack**, **Housekeeping**) stay relative to the repository root,
  not to the tracker file. The recommended place of a target's own Pack, beside the tracker file, moves with it.
- **The onboarding writes no pointer.** A human who wants the file elsewhere writes the pointer.

## Considered Options

- **A config file of the suite's own at a fixed path.** A second place for a fact `AGENTS.md` already carries, the
  suite state ADR-0024, ADR-0025 and ADR-0074 keep out of the target. Rejected.
- **An environment variable or a call argument.** Has to be repeated on every call; a scheduled job forgets it.
  Rejected.
- **A fixed line format in `AGENTS.md`** (`Issue tracker: <path>`). Unambiguous, and the parser could read it, but only
  targets writing that exact line would be found. The domain docs' prose rule already works. Rejected.
- **The parser reads `AGENTS.md` itself.** It would have to judge prose. Rejected.
- **A pointer leaving the repository falls back to the default.** Silent, and a likely second tracker description.
  Rejected.
- **The onboarding offers to write the pointer.** One more question and one more `AGENTS.md` write a human must
  approve, for a case the human sets up once. Left for later.

## Consequences

- A target can keep its tracker description where its other agent docs live; the suite finds it there.
- A run reads `AGENTS.md`/`CLAUDE.md` before the Ready step's tracker check, and hands the resolved path to the
  parser.
- A new reason a run ends early: a pointer outside the repository.
