# 2 — CHANGELOG.md with a fragment-file mechanism, enforced by convention + CI

**What to build:** Now that the repo is public, track releases and their changes in a `CHANGELOG.md`.
Per-change work doesn't write directly into it; instead each noteworthy PR drops a small fragment file,
and a manual release step consolidates all pending fragments into a new `CHANGELOG.md` section, deletes
the fragments, tags, and syncs the GitHub release body. `CHANGELOG.md` is also backfilled retroactively
for the two versions already tagged (`0.1.0`, `0.2.0`), since no release notes exist for them today.

**Why:** User request, ahead of the repo going public — a public repo needs a legible record of what
changed release to release, without relying on readers combing through merged-PR history.

**Blocked by:** none.

**Priority:** medium — not urgent, but wanted before/soon after the next release.

**Status:** done

Settled via `/grill-me` (three rounds):

- [x] **Fragment files:** `.changelog.d/<NN-or-PR>-<slug>.md` — number when a ticket or PR number
  exists, plain slug otherwise. Free-form, user-facing prose; no category tags (`Added`/`Fixed`/etc.).
- [x] **What counts as noteworthy:** only changes with a visible effect for someone installing/using
  the suite (new/changed skill capability, bugfix, breaking change). Internal-only work (ticket
  bookkeeping, `.scratch/` maintenance, CI tuning, no-behaviour-change wording fixes) gets no fragment.
- [x] **`CHANGELOG.md` format:** Keep-a-Changelog-*flavoured* but flat — `## [X.Y.Z] - YYYY-MM-DD`
  headers, a plain list underneath, no `### Added/Changed/Fixed` subcategories (same "flat until
  content justifies structure" reasoning as `docs/FAQ.md`).
- [x] **Release process:** pure convention, no new skill — a recipe in `CONTRIBUTING.md`: collect
  fragments → write a new `CHANGELOG.md` section → delete the fragments → tag → sync the same section
  into the GitHub release body (`gh release create`/`edit`). Version number is SemVer, chosen by hand
  by whoever runs the release — no per-fragment bump level.
- [x] **Enforcement:** a CI gate (extends `skills-validation.yml` or a new workflow) fails a PR that
  touches `skills/**`, `docs/**` (except `docs/adr/**`), `README.md`, or `CONTRIBUTING.md` without
  adding a `.changelog.d/*.md` file — unless the PR carries a `no-changelog` label (new triage label,
  same mechanism as the existing labels in `docs/agents/triage-labels.md`).
- [x] **Where documented:** `AGENTS.md` gets a short pointer paragraph (same shape as its existing
  Git-workflow/Issue-tracker/Triage-labels/Domain-docs entries), linking to `CONTRIBUTING.md` for the
  full recipe.
- [x] **Retroactive backfill:** `CHANGELOG.md` gets `## [0.1.0]` and `## [0.2.0]` sections derived
  directly from the merged-PR history between those tags (36 PRs before `0.1.0`, 8 PRs between
  `0.1.0`→`0.2.0`), filtered to the same "noteworthy" bar as future entries, each entry citing its PR
  number in place of a (never-existed) fragment file. Both tags' currently-empty GitHub release bodies
  get the matching section copied in too.

## Comments

> **2026-09-06:** Filed after a full `/grill-me` session (German, three rounds) covering fragment
> location/format, noteworthiness bar, `CHANGELOG.md` shape, release process ownership, version-number
> ownership, enforcement mechanism, doc placement, fragment naming, and retroactive-backfill approach.
> User confirmed shared understanding ("passt."). Ready to implement.
