## Agent skills

### Git workflow

All changes go through feature branches and pull requests — never direct commits to `main`. Create a branch, implement, ensure CI is green, then open a PR. Merge only after review and passing pipeline.

**Run the relevant tests locally before pushing, every time — not just for code changes.** A change to `skills/**` or `docs/**` still needs `python3 -m unittest discover -s scripts -p 'test_*.py'` and `python3 scripts/validate_skills.py .` green locally first (see `.github/workflows/skills-validation.yml`); a change touching the tooling-tree parser or fixtures additionally needs the relevant `scripts/run-test.sh`/`fixtures/harness/run.sh` tier. Pushing untested and then iterating on red CI is not an acceptable substitute for running it yourself first.

### Issue tracker

Issues live as markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label strings, one per role. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## The continuous-refactoring suite

This repo IS the skill suite. The skills live under `skills/` and are consumed by symlinking them into a target repo's `.agents/skills/` (see `README.md`):

- `continuous-refactoring` — the loop pass orchestrator (scan → prioritise → design → implement → learn), a thin data pipe between the lifecycle skills (ADR-0010)
- `refactor-scan` — propose every currently-unblocked tooling-tree node, detect (never act on) closed/merged issues and MRs
- `refactor-prioritize` — rank the proposals, recommend next
- `refactor-design` — grill/search the chosen node into a plan, files it as an issue
- `refactor-implement` — execute the plan test-first, review included
- `refactor-learn` — the suite's only writer: ledger, ADR/CONTEXT.md, issue status

Loop vocabulary lives in `CONTEXT.md` (candidate, backlog, tooling tree, merge request, cadence, hot spot, deepening, seam, deletion test, proposals, findings). Human-facing docs live in `docs/playbooks/`. A reference doc a skill actually needs at runtime lives under `skills/<owning-skill>/references/` instead — `docs/playbooks/`, like `docs/adr/` and `docs/agents/`, never ships with the skills (ADR-0013).