# Reference: triage-label table template

The exact content written to a target repo's `docs/agents/triage-labels.md` when the onboarding interview
(`skills/continuous-refactoring/references/onboarding-setup-interview.md`) continues without the
engineering-skills setup — copy it, don't restate or paraphrase it (this file is the one place it's defined, to
avoid drifting copies; the static copies under `fixtures/` are seeds for tests). The shape is the engineering
skills' own label table, so their setup skill can later update the file in place. `needs-triage` and
`ready-for-human` are that setup's own roles; the suite never applies them, so they are not written here — a
table without those two rows is how the minimal form is told apart from the full one.

```markdown
# Triage Labels

The skills speak in terms of triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |
| —                          | `done`               | Work complete, delivered, no longer open |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

Edit the right-hand column to match whatever vocabulary you actually use.
```

## Variants

- **`done` row: Local Markdown tracker only.** On GitHub/GitLab a closed issue is done, so drop that row. An existing
  table on a Local Markdown tracker that lacks it gets just that one row appended.
- **Overrides.** A role whose label already exists on the forge under a different spelling (e.g. `wont-fix`) gets
  that spelling in the right-hand column. Only when this template is written — an existing table is never edited
  for overrides.
