# 02: Operations and onboarding

**What to build:** A developer who installs the suite answers where their tickets live and how the
operations work there, and nothing else. Afterwards the target's tracker file carries a
`## Refactoring operations` section in the new cut, and the suite can search that tracker.

Spec: `../spec.md` (sections *Refactoring operations*, *Rejections*, *Onboarding and existing targets*).
Written new with the `writing-for-agents` skill; the existing operations reference is carried over as
content, the existing interview is not transformed.

**Blocked by:** 01

**Status:** done

- [x] The operations reference lists **Search**, **Done**, **Merge requests** as required and
      **Candidate**, **Priority**, **Linked merge request**, **Comment author and time**, **Claim**,
      **Rejected**, **Blocked by**, **Housekeeping** as optional, each with what happens when it is missing
- [x] **Bookkeeping** and **Filed date** are gone from the reference and from every template
- [x] The GitHub, GitLab and Local Markdown templates are written in the new cut, **Search** covering open
      and closed tickets
- [x] The interview asks for the tracker and the operations only; no question on ticket mode,
      merge-request mode or bookkeeping remains, and it writes no config file and no bookkeeping document
- [x] An existing section without **Search** gets it added by running the interview again
- [x] The interview's text to the human says "skill suite" and "run"
- [x] No test is written or changed

## Comments

Done on `suite-rebuild`: `refactoring-operations.md` (reference and templates),
`local-issue-tracker-template.md` and `onboarding-setup-interview.md` under
`skills/continuous-refactoring/references/`. Nothing else was touched.

- **Red afterwards, for ticket 09:**
  - Unit tests: nothing newly red. The same two as before this ticket fail
    (`test_trigger_controls.CleanRepoReportsCleanTests.test_next_holds_only_structural_scan`,
    `test_validate_skills.EndToEndTests.test_real_repo_passes`); 227 of 229 are green.
  - `python3 scripts/validate_skills.py .` stays red for the reasons ticket 01 names. Five of its errors
    are gone (the glossary terms now in use); one warning is new: an orphan advisory for
    `triage-labels-template.md`, which the interview no longer names.
  - Fixture harness, not run here (it needs an agent run), red by reading: the expected behaviour of
    `php-onboarding-abort`, `-direct-track`, `-fresh`, `-interrupted`, `-migration`,
    `-second-invocation`, `-set-up`, `php-issue-mode-unreadable` and `php-ticket-create-mode-ask`
    describes the old interview (setup-gap question, create-mode questions, `config.md`,
    `bookkeeping.md`, the `AGENTS.md` section, the triage-label table). `fixtures/README.md` and
    `fixtures/harness/run.sh` describe it the same way.
- **Texts that still describe the old interview or the old operations, left for their tickets:** step 0
  of `continuous-refactoring/SKILL.md`, the `onboarding-setup` node doc, `filing-a-ticket.md`,
  `opening-a-merge-request.md`, `refactoring-bookkeeping.md`, `remote-bookkeeping.md`, and the
  `refactor-*` and `continuous-housekeeping` skills (**Filed date**, **Bookkeeping**, the create-modes).
- **Decided here, not stated by the spec:**
  - The interview writes one file, the tracker file. It no longer writes `docs/agents/triage-labels.md`
    or a section into `AGENTS.md`, and the setup-gap question is gone. `triage-labels-template.md` is
    now unreferenced; ticket 05 (labels of a flagged candidate) or 08 decides whether it stays.
  - The summary is a decision point (write it / change an answer / stop). An autonomous run takes the
    recommendation only when every required operation has an answer; otherwise it ends with the open
    question and writes nothing. The old fallback "nobody answers → Local Markdown" is gone.
  - A new step runs **Search** and the merge-request tool once after writing, so "the suite can search
    that tracker" is observed, not assumed.
  - The interview ends with its report; whether the run goes on afterwards is left to the entry skill
    (ticket 04).
  - Running it again on an existing section adds the missing required bullets and removes
    **Bookkeeping** and **Filed date**; every other bullet stays as written.
  - **Candidate**, **Priority** and a file-based **Rejected** are proposed only when the target already
    uses such a mark or an `.out-of-scope/` folder. **Housekeeping** is left to the Housekeeping Track
    (ticket 07).
  - Templates: **Blocked by** is a `Blocked by:` line in the ticket's text on all three trackers.
    **Rejected** is "closed as not planned" on GitHub and `Status: wontfix` on Local Markdown, which
    makes **Done** on GitHub "closed as completed"; GitLab has no closing reason, so **Rejected** is
    left for the target to choose there. Local tickets stay under `.scratch/refactor/issues/`, so
    existing local targets keep their tickets; the path is the target's and can be changed in its
    section.
  - A self-hosted forge gets a question of its own ("Where do merge requests live?"); on GitHub, GitLab
    and without `origin` the answer is read from the remote.
- **Carried over unchanged, worth a look at acceptance (ticket 09):** the GitHub template's **Linked
  merge request** uses `gh issue view --json closedByPullRequestsReferences`, which the `gh` 2.45.0
  installed here does not offer; the GitLab **Claim** uses `--assignee @me`, which `glab`'s help does not
  confirm. The new bullets avoid `stateReason` for the same reason and read the closing reason through
  `gh api` and the `reason:` search qualifier.
