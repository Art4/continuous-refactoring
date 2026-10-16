# pstack learnings

Source: Lauren Tan's (poteto) pstack plugin, https://github.com/cursor/plugins/tree/main/pstack —
read 2026-10-15. Interactive, router-driven (one `poteto-mode` skill, 23 playbooks, ~25 one-principle
skills); our suite is a tracker-driven chain of decision points. Only ideas that transfer are listed.

The user's priority order, most important first: 1, 2, 5, 6, 8, 9, 10, 13, 3, 7, then 12 (own item);
11 is folded into 2 and 3.

| # | Idea | pstack source | Ticket |
|---|------|---------------|--------|
| 1 | Pin behavior before structure moves (characterization test / snapshot / equivalence harness); type check and lint are not a pin; no coverage → write the pin first | `playbooks/refactoring.md` steps 1, 6 | issues/01 |
| 2 | Success measure is reduced reader load; a diff that lowers it nowhere is reverted; speculative cleanup is reverted. Includes 11: principles carry a "when it applies" trigger, the report names which principle shaped which decision | `principle-minimize-reader-load`, `refactoring.md` step 7 | issues/02 |
| 5 | MR report names the one fact the change is safe because of, and how far it was proven (said → line cited → bad case excluded → ran it → reproduced) | `skills/blast-radius` | issues/03 |
| 6 | Findings triaged into act on / consider / noted / dismissed, each with a reason; independent agreement is the strongest signal | `skills/interrogate` | issues/04 |
| 8 | Unattended run: checkable exit predicate never relaxed, smallest justified change per iteration, discard what did not help, decision trail, stop on a real dead end | `playbooks/autonomous-run.md`, `skills/show-me-your-work` | issues/05 |
| 9 | Before asking the human: a fact observable by running something is not theirs to answer; only genuine preference/product calls are | `poteto-mode` non-negotiables | issues/06 |
| 10 | Catch-up report: one opening sentence (how many things need the human), decisions with recommendation and what happens if unanswered, < 150 words | `skills/ketchup` | issues/07 |
| 13 | Test a skill-text change blinded before promoting it (stays scratch-only research, see memory) | `playbooks/eval.md`, `authoring-a-skill.md` | issues/08 |
| 3 | Migrate all callers and delete the old API in one wave; no shims; subtract (dead code, one-caller wrappers) before reshaping; commit order subtraction → reshape → follow-up. Includes 11 | `refactoring.md` steps 4–5, `principle-migrate-callers-then-delete-legacy-apis` | issues/09 |
| 7 | Review-bot comments: assess each on its merits, fix / dismiss with concrete reason / ask; do not churn code for noise | `references/bugbot-triage.md` | issues/10 |
| 12 | Same rule violated twice → encode as a check (`validate_skills.py`), not another paragraph | `principle-encode-lessons-in-structure` | issues/11 |

## Gap check (2026-10-16)

Read against `skills/continuous-refactoring/` as of `main` after #150; detail in each ticket's comments.

| Ticket | Status |
|---|---|
| 01 | partial |
| 02 | missing |
| 03 | partial |
| 04 | partial |
| 05 | partial |
| 06 | mostly covered |
| 07 | mostly covered |
| 08 | n/a |
| 09 | conflict to decide |
| 10 | missing |
| 11 | partial |

Nothing is fully built; 06 and 07 need only a sentence each. 09 needs a decision first, 04 a word that
does not collide with **Finding**.

## Where each item helps

- **Working in the target repo** (changes what a run does there): 1, 2, 3, 4, 5, 6, 7, 9, 10. Of these, 3, 4 and 7 shape what the target's humans read (MR description, findings, catch-up report), so they follow the forge-facing writing rule.
- **Improving this repo** (changes how the suite itself is built and kept honest): 12, 13.
- **Both:** 12 can also surface as a candidate in a target (a rule that lives only as a comment becomes a type, lint rule or check); 2 adds a principles reference to this repo whose content then steers target runs.

## Tooling-tree table

Independent of the table, but 1 and 5 make the decoupling of Tracks safer (see their tickets) and 11
covers the table's own consistency check. Build 1 and 5 before or with the table.

Also worth a look (not ticketed): rename spot-check — renames miss usages in strings, prose and
back-references, so verify each rename against the real files (`refactoring.md` step 5).

Not adopted: Cursor-specific mechanics (`/loop`, model slugs, `.mdc` rule), the single large router,
bundled TypeScript/bun scripts inside skills, `unslop` stylistic rules.

Before building any ticket: compare against the current `skills/` — part of this may already be
covered.
