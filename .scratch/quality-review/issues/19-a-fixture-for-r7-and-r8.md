# 19 — No fixture matches r7 and r8

Type: task
Status: open
Blocked by: —

**What the plays showed** (r7 and r8 on 2026-11-11, r7 A and p1 B on 2026-11-12). r7 and r8 describe an onboarded PHP
application whose Safety Net is met, but no fixture holds that state. Players run the parser on `php-clean` as a
stand-in, which has no tracker file, so the parser holds every Guardrails Stage back for the missing onboarding; they
borrow `--tracker-file` from another fixture or explain the result away. The briefs also leave the tracker file's
optional operations unsaid (Claim, Candidate, Priority, Linked merge request, Rejected, Ready after plan), so each
player assumes them.

**What to build**

- A fixture with the state r7 and r8 share: `composer.json` of type `project` on `php: ^8.2`, the Safety Net's tools
  configured, a PHPStan config on level 5, a PHP CS Fixer config with rules marked `Not yet:`, and a tracker file with
  the GitHub template's operations and a **Housekeeping** bullet.
- r7's and r8's *Situation* name the fixture and which optional operations the tracker file has.

**Done when** the fixture is in, the parser on it gives the Safety Net fulfilled with the seed the scenarios imply,
r7 and r8 name it, and tests and validator are green. Scenario-only, so no changelog fragment.

## Comments

**2026-11-13 — Also for this ticket.** r7 and r8 say every Safety Net Stage but `roave-bc-check` has a merged ticket,
which would include `bc-promise`, whose merge request writes the **BC promise** bullet the tracker file is said not to
have (named by r8 on 2026-11-11, r8 A on 2026-11-13, and in r9 and r10 before). The *Situation* names `bc-promise` as
never asked for, alongside the fixture.
