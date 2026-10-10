# 03: Acceptance run on a project with Redmine tickets and GitLab merge requests

**Status:** done

**What to do:** Run the onboarding in the youthweb project (`docs/agents/issue-tracker.md` already describes Redmine; `origin` is on `gitlab.com`) and then one full pass.

- Onboarding offers "Redmine, as `docs/agents/issue-tracker.md` describes it" as the recommended tracker and asks how a candidate and a priority candidate are marked.
- The written `## Refactoring operations` section names GitLab under **Merge requests**.
- A pass files its ticket in Redmine, comments the plan there, opens the merge request on GitLab, and remembers the pairing in `merge-requests.md`.
- The following pass recognises the merged merge request and finishes the ticket as **Done** says.

Record what went wrong as new tickets in this folder.

**Blocked by:** 01.

## Comments

**2026-10-10 — accepted by the maintainer on an onboarding run and a dry run, without a real pass.**

- Onboarding in youthweb (2026-10-09, on the `remote-bookkeeping` branch) offered "Redmine (Recommended)", asked how a candidate is marked (answer: ticket category "Refactoring", priority "Hoch" or higher) and wrote `## Refactoring operations` with all eight operations; **Merge requests** names GitLab. Nothing was created in Redmine or GitLab. The state question offered "In Redmine" and proposed a wiki page; the maintainer chose local files.
- A dry run of a pass found the category through **Candidate**, listed zero open candidates, selected the Safety Net Track and planned the ticket in Redmine and the merge request on GitLab under the project's own title convention. It started no Track skill and wrote nothing.
- Not observed, because no real pass ran: a ticket filed with the category, the plan's markup in Redmine, the merge request opened, and the following pass recognising it as merged.
- Seen in the onboarding run and unrelated to this change: the summary before writing was skipped, and all files were written in one command without a status line each.
