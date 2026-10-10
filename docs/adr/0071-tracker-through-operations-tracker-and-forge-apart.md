# The tracker is reached through operations, and tracker and forge are two things

> Amends [ADR-0012](0012-remembered-merge-requests-follow-the-tracker.md): remembered merge requests
> follow the tracker when it has a **Linked merge request** operation, not when it "supports labels
> natively".
>
> Amends [ADR-0024](0024-loop-config-interview-decides-tracker-create-mode-storage.md): the tracker
> question no longer sends "something else" to the Local Markdown template.

Installing the suite in a project with Redmine tickets and GitLab merge requests failed at onboarding:
the agent saw that Redmine was in use and offered GitHub, GitLab or local files. Two assumptions were
behind it. Skills decided tracker behaviour by name — "`docs/agents/issue-tracker.md` names a
native-label tracker (GitHub, GitLab)" at a dozen sites — and read every other name as Local Markdown.
And the tracker was also where merge requests live: `Closes #<n>`, the linked pull request, `gh`/`glab`.
In that project a Redmine ticket number after `Closes` in a GitLab merge request would close an
unrelated GitLab issue.

## Decision

Skills read **operations** from a `## Refactoring operations` section in the target's
`docs/agents/issue-tracker.md` — the shape the engineering skills use for `## Wayfinding operations`: a
"Used by" line, then one bullet per operation with a fixed bold name and free prose behind it.

- Required: **Candidate**, **Priority**, **Done**, **Filed date**, **Merge requests**.
- Optional: **Linked merge request**, **Comment author and time**, **Claim**. A missing bullet means the
  capability is absent; the skill takes its fallback (the `merge-requests.md` ledger, no re-check of a
  flagged candidate, no assignment). There is no "not available" line.
- Creating, reading, commenting on and closing an issue stay in the file's other sections.

The **issue tracker** is what that file describes; the **forge** hosts the repository and its merge
requests and is read from the Git remote. **Merge requests** records it. The suite prescribes no
`Closes #<n>`: the GitHub and GitLab templates carry it under **Linked merge request**, and a target
with its own convention writes that there.

Onboarding writes the section — from a template for GitHub, GitLab and Local Markdown, from the human's
answers otherwise. A tracker an existing `issue-tracker.md` describes is offered as its own, recommended
answer; without the file the human can describe the tracker in the interview. Local Markdown stays an
answer in every case, chosen rather than fallen into.

The dispatcher checks for the section before a pass and ends the invocation when it is missing.

## Considered

- **Redmine as a fourth named tracker.** Rejected — every further tracker (Jira, Forgejo) would add a
  branch at each of the dozen sites.
- **Fall back to the template by title when the section is missing.** Rejected — it keeps one name
  switch alive for targets onboarded earlier, which can run the onboarding again instead.
- **Operations for the target's status workflow, and a line for language and markup.** Rejected — which
  status a ticket gets when work starts, and how ticket texts are written, are the target's conventions.
  The suite follows what the target's files say and neither sets nor asks for them.
- **A strict section format the validator checks.** Rejected for now — fixed names are enough for a
  skill to find a bullet; the content differs per tracker.

## Consequences

A target onboarded earlier stops at the dispatcher's check until its onboarding is run again, which adds
the section and changes nothing else. "Native-label tracker" leaves the vocabulary; `CONTEXT.md` gains
**Issue tracker**, **Forge** and **Refactoring operations**. Issue mode stays written against `gh`/`glab`
and is offered only on GitHub and GitLab. Nothing in the tests, fixtures or the validator was changed
with this decision.
