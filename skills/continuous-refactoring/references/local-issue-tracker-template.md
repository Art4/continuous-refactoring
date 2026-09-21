# Reference: local Markdown issue-tracker template

The exact content written to a target repo's `docs/agents/issue-tracker.md`
when the onboarding interview
(`skills/continuous-refactoring/references/onboarding-setup-interview.md`)
records "Local Markdown" as the tracker choice — copy it verbatim, don't
restate or paraphrase it (this file is the one place it's defined, to avoid
two independently-drifting copies of the same convention).

```markdown
# Issue tracker: Local Markdown

Issues live as markdown files in `.scratch/refactor/issues/`, one file per
issue, numbered from `01`. A `Status:` / `Labels:` / `Filed:` line near the
top records triage state and the filing date (`YYYY-MM-DD`; see
`docs/agents/triage-labels.md` for the labels). Comments append under a
`## Comments` heading at the bottom of the file.

## When a skill says "file an issue"

Create a new file at `.scratch/refactor/issues/<NN>-<slug>.md`, its `Filed:`
line set to today's date — the only place a filing date exists on this
tracker, read wherever an issue's age matters (e.g. when ranking candidates).

## When a skill says "check the external tracker"

Read the files under `.scratch/refactor/issues/` directly.
```
