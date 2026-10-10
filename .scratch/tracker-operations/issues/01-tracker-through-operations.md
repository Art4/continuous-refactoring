# 01: Reach the issue tracker through operations, not by name

**Status:** done — PR #141

**What to build:** The skills decide tracker behaviour by name — "`docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab)" — and treat everything else as Local Markdown. Installing the suite in a project with Redmine tickets and GitLab merge requests showed two wrong assumptions: a tracker is one of three known names, and the tracker is also where merge requests live. Replace the name switch with named operations the target's `docs/agents/issue-tracker.md` describes, in a section `## Refactoring operations` shaped like the engineering skills' `## Wayfinding operations`.

- Operations: **Candidate**, **Priority**, **Done**, **Filed date**, **Merge requests** (required); **Linked merge request**, **Comment author and time**, **Claim** (optional). A missing optional bullet means the capability is absent and the skill takes its fallback.
- Tracker and forge are separate. **Merge requests** comes from the Git remote.
- The suite prescribes no `Closes #<n>`. The GitHub and GitLab templates carry it under **Linked merge request**; without that operation the ledger `merge-requests.md` remembers the pairing.
- Onboarding: templates for GitHub, GitLab and Local Markdown. A tracker an existing `issue-tracker.md` describes is offered as its own, recommended answer. Without the file, the human can describe another tracker in the interview. Local Markdown stays available in every case; an existing file is then left alone apart from the section.
- The dispatcher checks for the section before a pass and ends the invocation when it is missing. No fallback by title for targets onboarded earlier — they run the onboarding again.
- The interview's "It never runs again" sentence goes; the docs gain an entry on running onboarding again.

**Out of scope:** the target's status workflow (which status a ticket gets when work starts or a merge request opens), language and markup of ticket texts, the convention for linking tickets and merge requests — all the target's own. No new or changed tests, fixtures or validator checks.

**Acceptance:** onboarding runs through in a project with Redmine tickets and GitLab merge requests without falling back to Local Markdown, and a full pass works there (ticket filed, plan commented, merge request opened, recognised as merged on the next pass). An existing GitHub target keeps working after running the onboarding again. Verified by 03.
