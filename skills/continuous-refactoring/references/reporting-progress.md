# Reference: speaking to the human during a run

The reader watches the conversation live and has to be able to tell what the run is doing and what it just
changed, without opening anything.

- **Words.** Say "skill suite" for what is running and "run" for one call of it. Name a tooling-tree node by
  its Name ("PHPStan Level 0"). Use the forge's own word for a merge request (pull request on GitHub).
- **Each step: one sentence when it starts, one with its result** — what was found, what was chosen and
  why in a few words. A step that runs in a subagent is announced as such.
- **Each write is reported by itself, as it happens**: a ticket filed, commented on or closed, a rejection
  recorded, a branch pushed, a merge request opened. Name the thing and where it lives (number, path,
  link).
- **A step the run leaves out** gets one sentence with the reason.
- **A run that ends early** says so at once, with what ended it, before the closing report.
- **Only this conversation reports.** A subagent returns its result; the sentence to the human is written
  here, from what the result names.

Examples of the sentence after a step: "Reconcile: pull request #34 was merged; I recommend closing its
ticket #12." · "Scan: 4 of 19 Safety Net tools are missing; 2 of them wait for others." · "Selected
ticket #15, PHPStan Level 1 — next in the tree, nothing blocks it."
