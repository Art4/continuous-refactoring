# Reference: local Markdown issue-tracker template

The exact content written to a target repo's `docs/agents/issue-tracker.md`
when `loop-config`'s interview
(`skills/continuous-refactoring/references/loop-config-interview.md`)
records "Local Markdown" as the tracker choice — copy it verbatim, don't
restate or paraphrase it (this file is the one place it's defined, to avoid
two independently-drifting copies of the same convention).
`fixtures/harness/run.sh`'s `agent-loop` sandbox-seeding step draws from
this same file for the same reason — keep both in sync.

```markdown
# Issue tracker: Local Markdown

Issues live as markdown files in `.scratch/refactor/issues/`, one file per
issue, numbered from `01`. A `Status:` / `Labels:` line near the top records
triage state (see `docs/agents/triage-labels.md`). Comments append under a
`## Comments` heading at the bottom of the file.

## When a skill says "file an issue"

Create a new file at `.scratch/refactor/issues/<NN>-<slug>.md`.

## When a skill says "check the external tracker"

Read the files under `.scratch/refactor/issues/` directly — there is no
external forge in this sandbox.
```
