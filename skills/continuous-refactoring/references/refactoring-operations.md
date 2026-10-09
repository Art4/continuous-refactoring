# Reference: Refactoring operations

The suite reaches a target's issue tracker through **operations**, never through the tracker's name. They
live in the target's `docs/agents/issue-tracker.md`, in a section `## Refactoring operations`: one bullet
per operation, a fixed bold name followed by prose in that file's own language and with that tracker's own
commands. The file's other sections (creating, reading, commenting on and closing an issue) stay as whoever
wrote them left them; a skill that needs one of those follows the file.

The dispatcher checks once per invocation that the section exists (`../SKILL.md` step 0). Onboarding writes
it (`onboarding-setup-interview.md`).

## The operations

| Operation | What the section states | Section lacks it |
| --- | --- | --- |
| **Candidate** | How an issue is marked a refactoring candidate, and how to list the open ones | — required |
| **Priority** | How a candidate is marked to jump the queue, and how to list those | — required |
| **Done** | How a finished issue is recognised, and how one is marked finished | — required |
| **Filed date** | Where an issue's creation date is read | — required |
| **Merge requests** | Where merge requests live and which tool reaches them | — required |
| **Linked merge request** | How a merge request refers to its issue, and how to get from an issue to its merge request | Remembered merge requests live in the Refactoring Notes' `merge-requests.md`; the merge request names its issue in plain words |
| **Comment author and time** | How to read who wrote a comment, and when | A flagged candidate is never re-checked for a human's answer |
| **Claim** | How an issue is assigned to whoever works on it | Nothing is assigned |
| **Bookkeeping** | Where the suite's own state lives when not in local files, what the Bookkeeping pointer's value means there, how it is fetched and stored, and — where the suite may create that place — how | The bookkeeping lives in local files |

Skills keep saying `refactor:candidate` and `refactor:priority`. On a tracker whose **Candidate** and
**Priority** name something other than a label, those two words mean whatever the section says.

Where the section states where the suite's issues live, that wins over the rest of the file for the suite's
own issues — the case of a target that tracks its work elsewhere and keeps refactoring issues as local files.

**Bookkeeping** has one requirement: what was stored comes back unchanged at the next fetch — the bookkeeping
document, every learned rejection, and the merge-request ledger where the tracker has no **Linked merge
request**. How that is achieved is the target's (`remote-bookkeeping.md` holds the suite's side).

**Merge requests** names the **forge** (`CONTEXT.md`), which is read from the Git remote and may be a
different system than the tracker. Its three shapes:

- `origin` on `github.com` → `pull requests on this GitHub repository, via gh pr`
- `origin` on `gitlab.com` → `merge requests on this GitLab project, via glab mr`
- another host → what the human names; no `origin` → `none — the prepared branch is handed to the human`

## Templates

Written as they stand, with the **Merge requests** bullet replaced when tracker and forge differ.

### GitHub

```markdown
## Refactoring operations

Used by `/continuous-refactoring`.

- **Candidate**: the label `refactor:candidate`. List the open ones with `gh issue list --state open --label refactor:candidate`.
- **Priority**: the label `refactor:priority`, next to `refactor:candidate`.
- **Done**: a closed issue is done. There is no `done` label.
- **Filed date**: the issue's `createdAt`.
- **Merge requests**: pull requests on this GitHub repository, via `gh pr`.
- **Linked merge request**: the pull request's description carries `Closes #<issue>`. From the issue: `gh issue view <n> --json closedByPullRequestsReferences`.
- **Comment author and time**: `author` and `createdAt` of each entry in `gh issue view <n> --json comments`.
- **Claim**: `gh issue edit <n> --add-assignee @me`.
- **Bookkeeping**: one issue of this repository; the pointer is its URL. Its body is two plain sentences for a human who lands there (what the issue holds, that editing it changes what the loop does), a line `---`, then the bookkeeping document from its `# Refactoring Bookkeeping` title on. Each learned rejection is one comment whose first line is `<!-- refactor:out-of-scope <slug> -->`; any other comment is a human talking. Fetch: `gh issue view <n> --json state,body,comments`; a closed issue still counts, say so in the closing report. Store: replace the body, add a comment for a new entry, edit one whose text differs, delete one whose entry is gone. Create: look for an open issue titled `Continuous Refactoring` first and ask whether to adopt it; otherwise `gh issue create` with that title, the body above and no labels.
```

### GitLab

```markdown
## Refactoring operations

Used by `/continuous-refactoring`.

- **Candidate**: the label `refactor:candidate`. List the open ones with `glab issue list --label refactor:candidate -O json`.
- **Priority**: the label `refactor:priority`, next to `refactor:candidate`.
- **Done**: a closed issue is done. There is no `done` label.
- **Filed date**: the issue's `created_at`.
- **Merge requests**: merge requests on this GitLab project, via `glab mr`.
- **Linked merge request**: the merge request's description carries `Closes #<issue>`. From the issue: `glab api projects/:id/issues/<n>/closed_by`.
- **Comment author and time**: `author` and `created_at` of each entry in `glab api projects/:id/issues/<n>/notes`.
- **Claim**: `glab issue update <n> --assignee @me`.
- **Bookkeeping**: one issue of this project; the pointer is its URL. Its body is two plain sentences for a human who lands there (what the issue holds, that editing it changes what the loop does), a line `---`, then the bookkeeping document from its `# Refactoring Bookkeeping` title on. Each learned rejection is one comment whose first line is `<!-- refactor:out-of-scope <slug> -->`; any other comment is a human talking. Fetch: `glab issue view <n> --comments -F json`; a closed issue still counts, say so in the closing report. Store: replace the body, add a comment for a new entry, edit one whose text differs, delete one whose entry is gone. Create: look for an open issue titled `Continuous Refactoring` first and ask whether to adopt it; otherwise `glab issue create` with that title, the body above and no labels.
```

### Local Markdown

```markdown
## Refactoring operations

Used by `/continuous-refactoring`. Refactoring issues live as markdown files in
`.scratch/refactor/issues/`, one file per issue at `<NN>-<slug>.md`, numbered from `01`. A `Status:`, a
`Labels:` and a `Filed:` line sit near the top; comments append under a `## Comments` heading at the bottom.

- **Candidate**: `refactor:candidate` on the `Labels:` line. The open ones are the files whose `Status:` is neither `done` nor `wontfix`.
- **Priority**: `refactor:priority` on the `Labels:` line, next to `refactor:candidate`.
- **Done**: `Status: done`.
- **Filed date**: the `Filed:` line (`YYYY-MM-DD`), set to the day the file is created.
- **Merge requests**: <one of the three shapes>
```

### Another tracker

No template. Onboarding fills the section from what the file already states and what the human answers.
