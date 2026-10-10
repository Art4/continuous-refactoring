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

### Changelog

A noteworthy, user-visible change (`skills/**`, `docs/**`, `CONTEXT.md`, `README.md`,
`CONTRIBUTING.md`) needs a
`.changelog.d/<slug>.md` fragment — CI enforces this. See `CONTRIBUTING.md`'s "Changelog" section
for the fragment convention and the release recipe that consolidates them into `CHANGELOG.md`.

### Docs stay in sync

A change to a skill's behaviour is done only when every human-facing doc that describes it reads true against the change — in the same PR. `grep` the changed skill, Track, or term across `README.md` and `docs/` (outside `docs/adr/`) and update each hit:

- Skill roster, the run and its decision points, Track choice → `README.md` (skills table, "How it works"), `docs/architecture.md`, `docs/playbooks/tracks.md`, `docs/playbooks/run.md`
- A Track's own process → its playbook (`docs/playbooks/housekeeping.md`)
- New limits, fallbacks, or reasons a run ends early → `docs/known-limitations.md` (troubleshooting table)
- A design choice a user would ask "why?" about → `docs/FAQ.md`
- New or changed vocabulary → `CONTEXT.md`

`README.md` and `docs/**` explain in their own words: they cite no ADR numbers, ticket numbers, or `.scratch/` paths.

## The continuous-refactoring suite

This repo IS the skill suite. The skills live under `skills/` and are consumed by symlinking both into a target repo's `.agents/skills/` (see `README.md`):

- `continuous-refactoring` — one run: a chain of decision points from the target's open tickets to an opened merge request. Its `SKILL.md` holds the call, the decision-point rules and the steps; each step's detail is a file under its `references/`, where the tooling-tree parser and the tree docs live too.
- `continuous-housekeeping` — the Housekeeping Track alone, with no Track choice; `continuous-refactoring` reads the same `references/housekeeping-track.md` when its Track choice lands on Housekeeping.

Both are user-invocable. The suite keeps no state of its own: tickets, merge requests and rejections are found by searching the target's tracker and forge.

The suite's vocabulary lives in `CONTEXT.md` (run, decision point, worklist, candidate, tooling tree, Track, merge request, signal, proposals, findings). Human-facing docs live in `docs/playbooks/`. A reference doc a skill needs at runtime lives under `skills/<owning-skill>/references/` instead — `docs/playbooks/`, like `docs/adr/` and `docs/agents/`, never ships with the skills.
