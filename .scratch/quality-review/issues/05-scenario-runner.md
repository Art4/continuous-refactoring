# 05 — A scenario runner with a separate judge

Type: task
Status: done
Blocked by: 04

**What to build** (spec S2.2, S2.3; Q4, Q9, Q10)

- A skill local to this repository under `.claude/skills/`, not under `skills/` and not shipped. Given a branch, it
  picks the scenarios whose `Covers:` line names a file the branch changes (or a list it is handed), and plays each
  by *Playing one* in `docs/agents/evals/README.md`: a fresh subagent, the *Situation* and the *Call*, never the
  expected behaviour; live scenarios on a fixture copy in a temporary folder, walk-throughs as told.
- **The judge.** A second fresh subagent per scenario gets the player's record and the expected list and judges line
  by line. The result is pass, or the lines that failed, quoted.
- The runner proposes the line for `## Results` (date, skill commit, result); it changes no skill file.
- No CI step.
- `.claude/` is ignored today: decide how the skill is committed (an exception in `.gitignore`, or another place that
  Claude Code reads).

**Done when** the runner has played every scenario once with its judge, the results are noted, and tests and
validator are green.

## Comments

- 2026-11-07: Runner written; `.claude/skills/` is committed through a `.gitignore` exception (`.claude/*`,
  `!.claude/skills/`). The playing of every scenario runs block by block; plan, cost, results and findings are in
  `../scenario-playing-2026-11.md`.
- 2026-11-07: Done. Every scenario played once with its judge, block by block on the maintainer's go: 29 plays,
  25 pass, 4 fail (d10, r1, r5, r6); d9 is the maintainer's. Results are in each scenario's `## Results`; findings
  and cost in `../scenario-playing-2026-11.md`, left for later. d10's earlier pass came with a timer tool whose
  description said how to end it; without one, the skill's text names no call.
