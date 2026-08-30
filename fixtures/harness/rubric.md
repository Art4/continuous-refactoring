# LLM-judge rubric (Tier 5, ticket 27)

Used by `fixtures/harness/run.sh judge <fixture> --opencode` — a second, independent
opencode invocation grades a fixture's post-pass artifacts against the dimensions
below, one score 1–5 each plus a one-line justification. Local-only advisory (this
repo's CI has no model credentials to run a judge with), same posture as
`roadmap --opencode`, `agent-loop`, and the rest of Tier 4/5's behavioral layer —
see `fixtures/README.md`.

A judge run is a second opinion, not a gate: nothing here fails a build. It exists
to catch drift a deterministic assertion can't — prose quality, whether a chosen
candidate was actually the highest-leverage one available, whether a merge request's
description would make sense to a human reviewer who wasn't in the loop.

## Dimensions

| # | Dimension | 1 (poor) | 5 (excellent) |
|---|-----------|----------|----------------|
| 1 | **Process fidelity** | Skipped or reordered steps the relevant `SKILL.md` requires (e.g. `refactor-implement` opening a merge request before its diff review loop went clean) | Every step ran in the documented order, and any precondition or gate that fired is named in the output |
| 2 | **Candidate selection** | Picked a low-leverage or already-in-flight candidate `refactor-prioritize`'s own factors (heat, leverage, tooling pressure, risk) wouldn't rank first | The recommended candidate is defensible against `refactor-prioritize`'s stated factors, and the one-line "why it wins" actually holds up |
| 3 | **Artifact quality** | A filed issue or merge request a human reviewer would have to re-derive context for — missing `## Where`/`## Problem`/`## Signal`, vague rationale | Issue/MR reads like a human wrote it with full context: concrete file/line pointers, a problem statement a stranger could act on |
| 4 | **State hygiene** | `docs/refactoring/config.md` / `merge-requests.md` left inconsistent with what actually happened (stale `Pending candidates`, missing `Fulfilled nodes` entry) | State exactly reflects the pass: `refactor-learn` wrote it once, last, and it matches git history |
| 5 | **Honesty about ambiguity** | Silently guessed past an ambiguous instruction, or invented an outcome not supported by tool output | Named ambiguity explicitly instead of improvising past it (same bar `fixtures/README.md`'s `agent-loop` prompt sets) |

## Scoring a run

```bash
./fixtures/harness/run.sh judge <fixture> --opencode
# reads /tmp/judge-<fixture>.log afterwards
```

The judge prompt (`run_judge` in `fixtures/harness/run.sh`) points the model at this
file directly, so editing the table above changes what the next `judge` run grades
against — no code change needed.

## Using it with `lift`

`fixtures/harness/run.sh lift <fixture> --opencode` produces two transcripts (with
skills mounted, without). Running `judge` isn't wired to compare them automatically —
grade each transcript against this rubric by hand, or point a `judge`-style prompt at
both logs, and read the delta as the lift measurement.
