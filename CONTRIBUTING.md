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

## Changelog

If your change has a noteworthy, user-visible effect — a new or changed skill capability, a
bugfix, a breaking change — add a fragment file: `.changelog.d/<slug>.md` (prefix the slug with
your ticket or PR number when you have one, e.g. `.changelog.d/62-faq-section.md`). One short,
user-facing sentence or paragraph; no category tags. Internal-only work (ticket bookkeeping,
`.scratch/` maintenance, CI tuning, wording fixes with no behaviour change) needs none.

CI enforces this: a PR touching `skills/**`, `docs/**` (outside `docs/adr/**`), `CONTEXT.md`,
`README.md`, or `CONTRIBUTING.md` without a `.changelog.d/*.md` fragment fails, unless it carries the
`no-changelog` label.

**Cutting a release** (maintainer-only, by hand):

1. Collect every file under `.changelog.d/`.
2. Pick the next version (SemVer) and today's date, and add a new section to the top of
   [CHANGELOG.md](CHANGELOG.md):
   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD

   - <fragment 1's content>
   - <fragment 2's content>
   ```
   Also add a link reference for it at the bottom of the file, comparing against the *previous*
   tag (or, for the very first release, linking straight to its own release page):
   ```
   [X.Y.Z]: https://github.com/Art4/continuous-refactoring/compare/<previous-tag>...X.Y.Z
   ```
   Without this, `[X.Y.Z]` in the heading is inert text, not a link.
3. Delete the fragment files that section was built from.
4. Commit, tag `X.Y.Z`, push the tag.
5. `gh release create X.Y.Z --title X.Y.Z --notes-file -` (piping in the same section's body,
   minus the heading) — or `gh release edit` if the release already exists — so the GitHub
   release page carries the same text instead of staying empty.
