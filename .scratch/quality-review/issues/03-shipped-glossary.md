# 03 — A shipped glossary

Type: task
Status: open
Blocked by: —

**What to build** (spec S3; Q5, Q12)

- **The marker.** `CONTEXT.md`: an explicit mark on every term a skill needs at runtime. Which terms get it is decided
  here, term by term; design vocabulary used only by humans stays unmarked.
- **The generator.** A script under `scripts/` writes `skills/continuous-refactoring-run/references/glossary.md` from
  the marked terms: the term and its definition, without *Avoid* and examples. `--check` reports a glossary that is
  not current; `validate_skills.py` runs it, as it runs `adr_index.py --check`. Unit tests beside it.
- **The pointer.** `skills/continuous-refactoring-run/references/tooling-model.md` names the glossary instead of
  `CONTEXT.md`, which does not ship. The Driver and Housekeeping reach it through `../continuous-refactoring-run/`
  where they need it.
- Definitions that carry rules in place (the term table in `tooling-model.md`) stay there.
- `CONTRIBUTING.md`: how a term gets shipped. A changelog fragment.

**Done when** no shipped file points to `CONTEXT.md`, the glossary is generated and checked, and tests and validator
are green.
