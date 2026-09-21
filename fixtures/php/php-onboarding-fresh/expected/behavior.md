# Expected behavior — onboarding, engineering-skills setup missing

A target that has never run the loop and has none of the engineering skills' configuration
(`docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`). Confirms `/continuous-refactoring`
onboards it as step 0 of the dispatcher and **ends there**
(`skills/continuous-refactoring/SKILL.md` step 0,
`skills/continuous-refactoring/references/onboarding-setup-interview.md`).

Not deterministically checkable — the behavior is a skill process, not something `tooling_tree.py`
asserts on. Run via `fixtures/harness/run.sh agent-loop php-onboarding-fresh`, same non-CI, local-only,
advisory posture as `decision-gate-bypass`. Asserts only what the invocation says and writes, never the
wording of skill prose beyond the required announcement and closing content.

## Seeded state

A minimal PHP project (`composer.json`, `src/Greeter.php`). No `docs/`, no `AGENTS.md`/`CLAUDE.md`, no
`bookkeeping.md`, no remote (the harness's sandbox has none).

## Expected: first invocation

1. The **first output** says onboarding is starting. No scan subagent is started, no Track is selected.
2. The engineering-skills setup is reported incomplete; **one** up-front question offers abort (nothing
   written, hint to run `setup-matt-pocock-skills`) or continue. Continue is taken for the rest of this
   scenario. (Answering **abort** instead: nothing is written, the invocation ends.)
3. Q1 (tracker — recommendation Local Markdown, no remote), Q2 (merge-request create-mode) and Q3
   (Refactoring Notes location — recommendation `docs/refactoring/`), asked one at a time, each with a
   recommended answer.
4. An informational summary — no approval gate — naming the files to be written and the recorded backlog
   labels.
5. One status line per write, in this order: the suite's section in a **newly created** `AGENTS.md`
   (`Refactoring Notes:` line, the `Create-mode` pointer, the backlog labels line), `docs/agents/triage-labels.md`
   (`needs-info`, `ready-for-agent`, `wontfix`, plus a `done` row — Local Markdown), `docs/agents/issue-tracker.md`
   (the Local Markdown template), then `docs/refactoring/bookkeeping.md` **last**, holding `Create-mode` and no
   `Pending candidates`.
6. A closing text: what was created; commit or merge the files to the default branch; run
   `/continuous-refactoring` again (optionally naming a Track); the engineering-skills setup can still be
   run later and updates the files in place.
7. The invocation **ends**. No issue is filed, no branch or merge request opened, nothing committed, no
   forge call made.

## Expected: second invocation

After the human commits the files, `/continuous-refactoring` finds `bookkeeping.md`, selects the Safety
Net Track and starts the scan subagent normally — no onboarding text.

## The behavior this regression-tests

Onboarding used to run only after a scan, prioritise and design step whose sole conclusion was "the
config node is the only proposal", behind an announcement that read like an ordinary scan — the human
saw no hint it was onboarding. It also filed an issue and opened a merge request for one-time setup.

## Verified

Not yet manually confirmed live — see the implementing pull request's own report.
