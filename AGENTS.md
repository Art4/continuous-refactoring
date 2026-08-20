## Agent skills

### Issue tracker

Issues live as markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label strings, one per role. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## The continuous-refactoring suite

This repo IS the skill suite. The skills live under `skills/` and are consumed by symlinking them into a target repo's `.agents/skills/` (see `README.md`):

- `continuous-refactoring` — the loop pass orchestrator (scan → prioritise → design → implement → review → learn)
- `refactor-baseline` — tooling floor for a PHP project (php-cs-fixer, Rector, PHPStan, CI)
- `refactor-scan` — find and file `refactor:candidate` issues
- `refactor-prioritize` — rank the backlog, recommend next
- `refactor-design` — grill a candidate into a plan
- `refactor-implement` — execute the plan test-first
- `refactor-review` — two-axis review (standards / spec)

Loop vocabulary lives in `CONTEXT.md` (candidate, backlog, baseline, cadence, hot spot, deepening, seam, deletion test). Human-facing docs live in `docs/playbooks/`.