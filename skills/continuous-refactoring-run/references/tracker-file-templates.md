# Reference: tracker file templates

The `## Refactoring operations` section as written for each tracker, for the operations `refactoring-operations.md`
names.

Each template is written as it stands, with the **Merge requests** bullet replaced by the fitting shape
when tracker and forge differ. A template holds what its tracker answers by itself; the bullets a target
chooses are added from *Bullets the target chooses* below.

### GitHub

```markdown
## Refactoring operations

Used by `/continuous-refactoring-run`.

- **Search**: `gh issue list --state all --search "<words>" --json number,title,state,labels,updatedAt` searches title and text, open and closed together; `--state open` narrows it to the open ones. Raise `--limit` when the default of 30 cuts the list.
- **Done**: an issue closed as completed: `gh api repos/{owner}/{repo}/issues/<n> --jq .state_reason` gives `completed`. Mark one finished with `gh issue close <n> --reason completed`.
- **Merge requests**: pull requests on this GitHub repository, via `gh pr`.
- **Linked merge request**: the pull request's description carries `Closes #<issue>`. From the issue: `gh issue view <n> --json closedByPullRequestsReferences`.
- **Claim**: `gh issue edit <n> --add-assignee @me`.
- **Rejected**: an issue closed as not planned, the reason in its closing comment: `gh issue close <n> --reason "not planned" --comment "<reason>"`. Found again with **Search**, its query extended by `reason:"not planned"`.
- **Blocked by**: a line `Blocked by: #<n>, #<n>` in the issue's description. The issue is unblocked when every issue on that line is done.
```

### GitLab

```markdown
## Refactoring operations

Used by `/continuous-refactoring-run`.

- **Search**: `glab issue list --all --search "<words>" -O json` searches title and text, open and closed together; without `--all` it lists the open ones only. Raise `--per-page` when the list is cut.
- **Done**: a closed issue is done. Mark one finished with `glab issue close <n>`.
- **Merge requests**: merge requests on this GitLab project, via `glab mr`.
- **Linked merge request**: the merge request's description carries `Closes #<issue>`. From the issue: `glab api projects/:id/issues/<n>/closed_by`.
- **Claim**: `glab issue update <n> --assignee @me`.
- **Blocked by**: a line `Blocked by: #<n>, #<n>` in the issue's description. The issue is unblocked when every issue on that line is done.
```

### Local Markdown

```markdown
## Refactoring operations

Used by `/continuous-refactoring-run`. Tickets live as markdown files in `.scratch/refactor/issues/`, one file
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
- **Ready after plan**, as a label: ``the label `<label>`: `<the tracker's command to set it>`; removing a blocking label: `<command>`.`` Running it twice leaves the ticket as it is. Where the tracker uses a board column or a status field, the command that moves the ticket there.
- **BC promise**: ``the project's promise to code outside it is `<path or URL>`; read it before changing what it covers.`` Or: ``none — no code outside this repository relies on this one's.`` Or, with several parts, one sub-bullet each: ``<scope>: `<path or URL>` `` or ``<scope>: none``.
- **Rejected**, as a closed ticket: ``a closed ticket carrying `<mark>`, the reason in its last comment. Found again with **Search**, narrowed to that mark.``
- **Rejected**, as a file: ``one file per rejection at `<folder>/<slug>.md`, holding the reason. Found again with `grep -rli "<word>" <folder>/`.`` The engineering skills' `.out-of-scope/` folder is the natural `<folder>` when the target uses it.
