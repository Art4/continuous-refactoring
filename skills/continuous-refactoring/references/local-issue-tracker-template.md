# Reference: local Markdown issue-tracker template

The exact content written to a target repo's `docs/agents/issue-tracker.md`
when the onboarding interview
(`onboarding-setup-interview.md`)
records "Local Markdown" as the tracker choice and the file doesn't exist
yet — copy it verbatim, don't restate or paraphrase it (this file is the one
place it's defined, to avoid two independently-drifting copies of the same
convention). The section it ends on is `refactoring-operations.md`'s Local
Markdown template, which holds the issue-file convention.

```markdown
# Issue tracker: Local Markdown

## When a skill says "file an issue"

Create a new file as `## Refactoring operations` describes, its `Filed:`
line set to today's date.

## When a skill says "check the external tracker"

Read the files under `.scratch/refactor/issues/` directly.

<the Local Markdown `## Refactoring operations` section>
```
