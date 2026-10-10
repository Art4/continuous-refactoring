# 02: Operations and onboarding

**What to build:** A developer who installs the suite answers where their tickets live and how the
operations work there, and nothing else. Afterwards the target's tracker file carries a
`## Refactoring operations` section in the new cut, and the suite can search that tracker.

Spec: `../spec.md` (sections *Refactoring operations*, *Rejections*, *Onboarding and existing targets*).
Written new with the `writing-for-agents` skill; the existing operations reference is carried over as
content, the existing interview is not transformed.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The operations reference lists **Search**, **Done**, **Merge requests** as required and
      **Candidate**, **Priority**, **Linked merge request**, **Comment author and time**, **Claim**,
      **Rejected**, **Blocked by**, **Housekeeping** as optional, each with what happens when it is missing
- [ ] **Bookkeeping** and **Filed date** are gone from the reference and from every template
- [ ] The GitHub, GitLab and Local Markdown templates are written in the new cut, **Search** covering open
      and closed tickets
- [ ] The interview asks for the tracker and the operations only; no question on ticket mode,
      merge-request mode or bookkeeping remains, and it writes no config file and no bookkeeping document
- [ ] An existing section without **Search** gets it added by running the interview again
- [ ] The interview's text to the human says "skill suite" and "run"
- [ ] No test is written or changed
