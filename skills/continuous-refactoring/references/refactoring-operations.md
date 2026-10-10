# Reference: Refactoring operations

The suite reaches a target's issue tracker through **operations**, never through the tracker's name. They
live in the target's `docs/agents/issue-tracker.md`, in a section `## Refactoring operations`: one bullet
per operation, a fixed bold name followed by prose in that file's own language and with that tracker's own
commands. The rest of the file (creating, reading, commenting on and closing a ticket) stays as its author
wrote it, and a step that needs one of those follows the file. Where the section says where the suite's
tickets live, the section wins for those tickets — the case of a target that tracks its work elsewhere and
keeps refactoring tickets as local files.

A target is onboarded when its tracker file has the section. The onboarding interview writes the section,
and completes one that lacks a required operation — **Search**, in a section written before this cut
(`onboarding-setup-interview.md`).

## Required operations

| Operation | What the bullet states |
| --- | --- |
| **Search** | How tickets are searched by words in title and text, open and closed together, and how the result is narrowed to the open ones |
| **Done** | How a finished ticket is recognised, and how one is marked finished |
| **Merge requests** | Where merge requests live and which tool reaches them |

**Merge requests** names the **forge**, read from the Git remote; it may be a different system than the
tracker. Its three shapes:

- `origin` on `github.com` → `pull requests on this GitHub repository, via gh pr`
- `origin` on `gitlab.com` → `merge requests on this GitLab project, via glab mr`
- another host → what the human names; no `origin` → `none — the prepared branch is handed to the human`

## Optional operations

An absent bullet means the tracker lacks the capability, and the suite takes the fallback in the last
column.

| Operation | What the bullet states | Without it |
| --- | --- | --- |
| **Candidate** | How a ticket is marked as refactoring work, and how the open ones so marked are listed — a hint that narrows **Search** | A ticket is recognised by its subject alone; one a human wrote freely is worked only when the call names it |
| **Priority** | How a ticket is marked to come first, and how those are listed — a hint for the order | The order is the Track's own; no ticket comes first |
| **Linked merge request** | How a merge request refers to its ticket, and how to get from a ticket to its merge request | The merge request names its ticket in plain words and is found by searching the forge's merge requests for it |
| **Comment author and time** | How to read who wrote a comment, and when | A human's answer in a comment goes unrecognised; the ticket waits until the human names it in the call |
| **Claim** | How a ticket is assigned to whoever works on it | Nothing is assigned |
| **Rejected** | How a rejection is recorded with its reason and found again: a closed ticket or a file, and where | At the decision point that records the first rejection the suite proposes a place, and writes the bullet from the answer |
| **Blocked by** | How a ticket states which tickets block it, and when it counts as unblocked | The suite writes the dependency as a sentence in the ticket's text and reads it there |
| **Housekeeping** | Where the **Housekeeping template** lives and how the next **Housekeeping ticket** is made from it | Housekeeping's mechanism counts as missing: the Housekeeping Track proposes to set it up and writes the bullet |

## Templates

Each template is written as it stands, with the **Merge requests** bullet replaced by the fitting shape
when tracker and forge differ. A template holds what its tracker answers by itself; the bullets a target
chooses are added from *Bullets the target chooses* below.

### GitHub

```markdown
## Refactoring operations

Used by `/continuous-refactoring`.

- **Search**: `gh issue list --state all --search "<words>" --json number,title,state,labels,updatedAt` searches title and text, open and closed together; `--state open` narrows it to the open ones. Raise `--limit` when the default of 30 cuts the list.
- **Done**: an issue closed as completed: `gh api repos/{owner}/{repo}/issues/<n> --jq .state_reason` gives `completed`. Mark one finished with `gh issue close <n> --reason completed`.
- **Merge requests**: pull requests on this GitHub repository, via `gh pr`.
- **Linked merge request**: the pull request's description carries `Closes #<issue>`. From the issue: `gh issue view <n> --json closedByPullRequestsReferences`.
- **Comment author and time**: `author` and `createdAt` of each entry in `gh issue view <n> --json comments`.
- **Claim**: `gh issue edit <n> --add-assignee @me`.
- **Rejected**: an issue closed as not planned, the reason in its closing comment: `gh issue close <n> --reason "not planned" --comment "<reason>"`. Found again with **Search**, its query extended by `reason:"not planned"`.
- **Blocked by**: a line `Blocked by: #<n>, #<n>` in the issue's description. The issue is unblocked when every issue on that line is done.
```

### GitLab

```markdown
## Refactoring operations

Used by `/continuous-refactoring`.

- **Search**: `glab issue list --all --search "<words>" -O json` searches title and text, open and closed together; without `--all` it lists the open ones only. Raise `--per-page` when the list is cut.
- **Done**: a closed issue is done. Mark one finished with `glab issue close <n>`.
- **Merge requests**: merge requests on this GitLab project, via `glab mr`.
- **Linked merge request**: the merge request's description carries `Closes #<issue>`. From the issue: `glab api projects/:id/issues/<n>/closed_by`.
- **Comment author and time**: `author` and `created_at` of each entry in `glab api projects/:id/issues/<n>/notes`.
- **Claim**: `glab issue update <n> --assignee @me`.
- **Blocked by**: a line `Blocked by: #<n>, #<n>` in the issue's description. The issue is unblocked when every issue on that line is done.
```

### Local Markdown

```markdown
## Refactoring operations

Used by `/continuous-refactoring`. Tickets live as markdown files in `.scratch/refactor/issues/`, one file
per ticket at `<NN>-<slug>.md`, numbered from `01`. A `Status:` line sits near the top, followed by a
`Blocked by:` line where something blocks the ticket; comments append under a `## Comments` heading at the
bottom.

- **Search**: `grep -rli "<word>" .scratch/refactor/issues/` searches title and text, open and closed together. The open ones are the files whose `Status:` is neither `done` nor `wontfix`.
- **Done**: `Status: done`; set the line to mark a ticket finished.
- **Merge requests**: <one of the three shapes>
- **Rejected**: `Status: wontfix`, the reason as the last entry under `## Comments`. Found again with **Search**.
- **Blocked by**: `Blocked by: <NN>, <NN>`. The ticket is unblocked when every file on that line is `Status: done`.
```

### Another tracker

No template. The interview fills the section from what the tracker file already states and what the human
answers.

### Bullets the target chooses

Added to any section above when the target names the mark or the place; each replaces a template bullet of
the same name.

- **Candidate**, as a label: ``the label `<label>`. List the open ones with `<the tracker's list command, narrowed to that label>`.`` Where the tracker has no labels: the mechanism the human names (a custom field, a subject prefix, child tickets of one collecting ticket).
- **Priority**, as a label: ``the label `<label>`, next to the **Candidate** mark.``
- **Rejected**, as a closed ticket: ``a closed ticket carrying `<mark>`, the reason in its last comment. Found again with **Search**, narrowed to that mark.``
- **Rejected**, as a file: ``one file per rejection at `<folder>/<slug>.md`, holding the reason. Found again with `grep -rli "<word>" <folder>/`.`` The engineering skills' `.out-of-scope/` folder is the natural `<folder>` when the target uses it.
