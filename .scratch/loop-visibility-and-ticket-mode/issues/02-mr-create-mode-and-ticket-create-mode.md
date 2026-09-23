# 02: Rename `Create-mode` to `MR-create-mode`; add `Ticket-create-mode`; the loop creates tickets

**What to build:** See ADR-0063 — the design is grilled and recorded there; this ticket is its implementation. Depends on 01 only for the "ticket created" report line.

**Status:** ready-for-agent

## Scope

- **Rename** `Create-mode` → `MR-create-mode` in `refactoring-bookkeeping.md`, `onboarding-setup-interview.md`, `opening-a-merge-request.md`, `refactor-implement`, `refactor-loop`, `refactor-learn`, the `onboarding-setup` node docs, README, `docs/architecture.md`, `docs/playbooks/loop.md`, `docs/known-limitations.md`, the 38 fixtures (`bookkeeping.md`, the two `AGENTS.md` pointers, the three onboarding `expected/behavior.md`). The old name is still read as `MR-create-mode`; `refactor-learn` writes the new name on its next write to that file.
- **New field** `Ticket-create-mode: autonomous | ask-each-time`; absent = `autonomous`. New interview question right after the tracker question; Summarize and Record name it; `AGENTS.md`'s pointer section gains a `Ticket-create-mode:` line. Onboarding fixtures updated.
- **New reference** `skills/continuous-refactoring/references/filing-a-ticket.md`: the mode rule, the draft shape (title, labels, body, dedupe key), the unattended-run behaviour. Read by `refactor-loop`, `refactor-learn` and `continuous-housekeeping`.
- **Loop creates tickets**, right after the ranking (step 3): `refactor-prioritize` returns drafts (pre-filing, Select mode) instead of creating; `refactor-design` never creates one and only updates the existing ticket; `refactor-learn`'s secret-history findings return drafts; Housekeeping's cycle ticket follows the same rule directly.
- **`ask-each-time`:** one batched question for the pre-filing; a separate question for the chosen candidate; a refusal ends the pass, and the loop offers once to reject the node for good (`out-of-scope/`, written by `refactor-learn`); unattended → nothing created, the pass reports it waits for a confirmation and that `Ticket-create-mode` can be set to `autonomous` in `bookkeeping.md`.
- **Docs:** `CONTEXT.md` — add **Ticket** (the human-facing name for an issue; not a synonym for **Candidate**, whose `_Avoid_` line keeps "ticket"), **MR-create-mode** (formerly `Create-mode`) and **Ticket-create-mode**, in the same PR that makes the skills use them (`validate_skills.py` rejects a glossary term no skill uses); `docs/FAQ.md` (why the loop creates tickets and asks), `docs/known-limitations.md` (waiting-for-confirmation ending), a `.changelog.d/` fragment. Tooling-tree parser only if a fixture or test reads the field.

## Acceptance

- A fixture per behaviour: default (`autonomous`, field absent), `ask-each-time` with a yes and a no to the batched question, a refused chosen ticket, an unattended run, an old-name `Create-mode` file.
- `python3 -m unittest discover -s scripts -p 'test_*.py'`, `python3 scripts/validate_skills.py .` and the relevant `fixtures/harness/run.sh` tier pass.
