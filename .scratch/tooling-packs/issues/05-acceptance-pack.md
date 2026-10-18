# 05 — Acceptance case: a new Pack or Tool

Type: task
Status: ready-for-agent
Blocked by: 02, 03

The model is meant to make adding tools cheap. This ticket proves it: add the smaller of a Twig Pack
(Applies when: `.twig` templates in the repository) or Infection (`.scratch/php-tooling-tree/issues/09`),
and count what it took.

**What to build**

- The Pack or Tool: its rows in `pack.json`, its Tool file with Fulfilment check and MR scope per Stage,
  the regenerated docs, a changelog fragment.
- A comment on this ticket: which files changed and whether anything outside the Pack, its Tool file and
  the generated docs had to change. Anything else that had to change is a finding against the model.

**Done when** the new Stages appear in the parser's output on a fixture where they apply and not on one
where they do not, tests and validator are green, and the comment is written.

## Comments
