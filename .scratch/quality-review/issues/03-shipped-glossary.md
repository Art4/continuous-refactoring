# 03 — A shipped glossary

Type: task
Status: done
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

## Comments

> **2026-11-07:** Done, reshaped by spec Q21–Q23: no marker and no generator. Every term (all 55 occur under
> `skills/`) moved with its *Avoid* line into `references/glossary.md`; `CONTEXT.md` keeps its head and points there.
> The three `SKILL.md` and `tooling-model.md`, `packs/php/psr-4.md`, `packs/php/rector.md` point to the glossary
> instead of `CONTEXT.md`, which no shipped file names any more. `validate_skills.py` reads the glossary from its new
> path and leaves it out of the text its vocabulary checks count as use; four tests. `AGENTS.md`,
> `docs/agents/domain.md`, `CONTRIBUTING.md`, `README.md` and `docs/architecture.md` name the new place.
