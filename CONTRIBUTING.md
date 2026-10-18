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
     The first command includes the tooling-tree parser's tests. The validator needs `pip install pyyaml jsonschema`. No automated check runs an agent
     against a sample project; see [fixtures/README.md](fixtures/README.md).

   See [AGENTS.md](AGENTS.md) for the full policy — pushing untested and iterating on red CI is
   not an acceptable substitute for running it yourself first.
   - A change to a Pack (`packs/*/pack.json`) or to `roles.json`: regenerate first, with
     `python3 scripts/tooling_docs.py`. It writes the JSON in its fixed form and the tables and
     diagrams under `docs/tooling/`; the validator fails on a Pack, a Role or a generated page that is
     out of date (`--check` lists the differences without writing).
4. Open a pull request. CI must be green; merge only after review.

## Skill suite conventions

If your change touches the skills themselves (`skills/**`), skim
[AGENTS.md](AGENTS.md), [CONTEXT.md](CONTEXT.md) and [docs/architecture.md](docs/architecture.md) first —
they define the vocabulary and the shape of the suite: two skills, a run as a chain of decision points,
and everything else a reference one of them loads. The `docs/adr/` directory
records why past design decisions were made; check it before re-litigating one.

**A rule broken twice becomes a check.** When the same rule is violated a second time, or a review
raises it a second time, do not add another paragraph: encode it as a check in `scripts/validate_skills.py`
(or a test beside it), with a unit test of its own. What no tool can decide stays a written rule.

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
