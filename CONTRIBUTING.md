# Contributing

Thanks for considering a contribution to `continuous-refactoring`.

## Reporting bugs and requesting features

Open a [GitHub Issue](https://github.com/Art4/continuous-refactoring/issues/new/choose) — that's
the right place for anything coming from outside the project. (The maintainer's own working
backlog lives as markdown files under `.scratch/`, per
[docs/agents/issue-tracker.md](docs/agents/issue-tracker.md); that's an internal convention, not
where external reports go.)

## Making a change

1. Create a branch — never commit directly to `main`.
2. Make your change.
3. Run the tests relevant to what you touched, locally, before pushing:
   - Any change under `skills/**` or `docs/**` (this includes `CONTEXT.md`):
     ```
     python3 -m unittest discover -s scripts -p 'test_*.py'
     python3 scripts/validate_skills.py .
     ```
   - A change touching the tooling-tree parser or `fixtures/`: additionally run the relevant
     `fixtures/harness/run.sh` tier (see [fixtures/README.md](fixtures/README.md)).

   See [AGENTS.md](AGENTS.md) for the full policy — pushing untested and iterating on red CI is
   not an acceptable substitute for running it yourself first.
4. Open a pull request. CI must be green; merge only after review.

## Skill suite conventions

If your change touches the skills themselves (`skills/**`), skim
[AGENTS.md](AGENTS.md) and [CONTEXT.md](CONTEXT.md) first — they define the vocabulary and the
orchestrator's data-flow rules (ADR-0010) that every skill follows. The `docs/adr/` directory
records why past design decisions were made; check it before re-litigating one.
