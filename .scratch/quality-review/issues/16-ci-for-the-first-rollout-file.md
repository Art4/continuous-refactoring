# 16 — The part that creates a rollout file does not say it adds it to CI

Type: task
Status: done
Blocked by: —

**What the plays showed** (r7 on 2026-11-11, r7 A on 2026-11-12; named twice, so a ticket under Q54).
`php-cs-fixer.md` *Taking in a rule* says CI runs `check` with the main config "and with the rollout file wherever it
exists", and the adoption's Fulfilment check asks the same. But the rollout Stage's *MR scope* of a part is "the
rollout file widened by the part's paths, or created for the next rule, and the tool's formatting run, one commit with
nothing typed by hand". A part that creates the rollout file therefore has no word for the CI change it needs, and
the CI line, the `.gitignore` entry for the rollout file's cache and the `Not yet:` comment's "rolled out via …" are
typed by hand, against "nothing typed by hand". The last part, which deletes the rollout file, has the same gap in
reverse: CI's invocation of the file goes too. ESLint's rollout file (`eslint.md`) is built the same way and may share
it; PHPMD's rollout ruleset is to be checked.

**To decide**

- Whether a part that creates or deletes a rollout file has two commits (the config and CI by hand, then the tool's
  run with nothing typed by hand), or one commit whose hand-typed lines are only config and CI.
- Whether CI runs the rollout file through a fixed invocation set up once at the adoption (a step that runs it only
  where it exists), so later parts never touch CI.

**Done when** each rollout Stage's *MR scope* says what a part that creates or deletes the rollout file holds, the
scenarios that cover the Tool files pass, and tests and validator are green.

## Comments

**2026-11-12 — Also named twice, same paragraph.** When an earlier plan for a PHP CS Fixer part still stands is said
only for PHPStan's baseline (`planning-a-baseline-ticket.md`, step 2: "a group that still has all its entries"); for
a rollout the counterpart would be "the plan's rule and paths are still not taken in" (r7 A, p1 B). And a rule whose
first part is also its last creates no rollout file, which the text leaves to inference (r7 on 2026-11-11, r7 A). Both
belong to *Taking in a rule* and a part's *MR scope*, so they are built here.
