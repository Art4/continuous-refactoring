# 02 — The Pack route

Type: task
Status: open
Blocked by: 01

Part of `../spec.md`, *The Pack route*. Written against today's skill name; ticket 03 moves it.

**What to build**

- `skills/continuous-refactoring/SKILL.md`, *The call*: a new row, "a Pack of its own / a tool the suite does not
  know", leading to the new reference. Step 1 (*Ready*) still runs; the run skips the worklist and the Track
  choice, and ends with the merge request. `SKILL_MD_WORD_LIMIT` holds.
- `references/own-pack.md`: Pack directory, `pack.json` in the form the suite's own have, a `roles.json` where it
  adds a Role, one Tool file per Tool with Fulfilment check and MR scope, the **Tooling Pack** bullet, the check
  with the parser's `--own-pack` (exit code 2 names both places), `opening-a-merge-request.md`. It takes what is
  agent instruction from `docs/playbooks/own-tool.md` and points at `tooling-model.md`, *A target's own Pack*,
  rather than repeating it.
- `opening-a-merge-request.md` is handed a ticket, and this route has none. Settle how the merge request reads
  without one; a run that files a ticket first only to close it is not the way out.
- `docs/playbooks/own-tool.md` keeps what a human reads: what a Pack is for, the example, how to call it.
- Docs: `docs/playbooks/run.md` (*The call*), `README.md`, `docs/architecture.md`, `docs/FAQ.md` if a "why" arises;
  a changelog fragment.

**Done when** the Pack scenarios of ticket 01 pass, a Pack built this way passes `--own-pack` and is read by a
following run, and tests and validator are green.
