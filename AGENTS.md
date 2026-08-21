## Agent skills

### Git workflow

All changes go through feature branches and pull requests — never direct commits to `main`. Create a branch, implement, ensure CI is green, then open a PR. Merge only after review and passing pipeline.

### Issue tracker

Issues live as markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label strings, one per role. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## The continuous-refactoring suite

This repo IS the skill suite. The skills live under `skills/` and are consumed by symlinking them into a target repo's `.agents/skills/` (see `README.md`):

- `continuous-refactoring` — the loop pass orchestrator (scan → prioritise → design → implement → review → learn)
- `refactor-scan` — find and file `refactor:candidate` issues
- `refactor-prioritize` — rank the backlog, recommend next
- `refactor-design` — grill a candidate into a plan
- `refactor-implement` — execute the plan test-first
- `refactor-review` — two-axis review (standards / spec)

Loop vocabulary lives in `CONTEXT.md` (candidate, backlog, tooling tree, merge request, cadence, hot spot, deepening, seam, deletion test). Human-facing docs live in `docs/playbooks/`.