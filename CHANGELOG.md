# Changelog

All notable changes to this project are documented here. Format inspired by
[Keep a Changelog](https://keepachangelog.com/), kept flat (no `Added`/`Changed`/`Fixed`
subcategories) — see `CONTRIBUTING.md`'s "Changelog" section for how entries are produced.

## [0.3.0] - 2026-09-06

- Fixed two tooling-tree parser false negatives (`phpstan-level-0` and Rector's set-name casing)
  that could report an already-adopted node as unfulfilled. (#48)
- `refactor-scan` now proposes PHPStan baseline-shrink candidates: incrementally reducing an
  existing baseline file instead of leaving it frozen forever. (#49)
- Fixed a staleness bug: the bookkeeping write now reads a fresh `origin/main` immediately before
  writing, instead of a snapshot that could be several commits behind. (#50)
- Fixed the resolved-gate cascade to correctly propagate through a rejected required ancestor,
  instead of leaving descendants stuck — including the same fix applied to `composer-audit`'s own
  fallback gate. (#51, #55)
- Added a `Refactoring goal` field that steers which structural candidates the loop searches for
  next. (#53)
- Fixed Psalm-equivalence detection to respect the documented co-presence rule instead of a
  stricter, undocumented one. (#57)
- Added the `continuous-housekeeping` skill: a separate, recurring maintenance sweep (default
  weekly) for dependency currency, tooling-deprecation cleanup, and documentation sync — plus a
  `Housekeeping` field tooling-tree nodes can contribute to. (#58)
- Added `docs/FAQ.md`, answering recurring questions about the suite's own design decisions,
  linked from the README. (#59)
- Added a `CHANGELOG.md` fragment-file mechanism: noteworthy changes drop a `.changelog.d/*.md`
  fragment (enforced by CI via the `no-changelog` label escape hatch), consolidated into
  `CHANGELOG.md` — and the fragments deleted — at release time. (#60)

## [0.2.0] - 2026-09-04

- Folded native-tracker in-flight bookkeeping into the candidate's own branch instead of a shared
  file, removing a recurring source of merge conflicts. (#40)
- On a native-label tracker, `refactor-design` skips the now-redundant Pending-candidates write.
  (#41)
- Dropped the `rector-early-return` tooling-tree node, folding its scope into
  `rector-code-quality`. (#45)
- Candidate merge requests now open as draft until the fold-in bookkeeping lands. (#46)
- Added a `psr-4` tooling-tree node for app-source autoloading. (#47)

## [0.1.0] - 2026-09-03

Initial release.

- The `scan → prioritize → design → implement → learn` orchestrator loop, plus the generic
  (language-neutral) tooling tree and its `structural-scan` gate. (#8, #9)
- PHP tooling-tree specialization: structural-scan leaves (editorconfig, composer, ci-runner), an
  `is-php-project` recognition gate, the PHPStan adoption chain (levels 0–10, baseline shrinking,
  Psalm mutual exclusion), the Rector rule-set family, and a PHP-minimum-version floor precheck.
  (#6, #7, #21, #23, #24, #26, #27, #28, #29, #30, #31)
- Recommended-edge gating and a CI-gating self-wire, so a node only proposes once its
  prerequisites are actually adopted, not merely present. (#19, #20)
- `loop-config` became a one-time human setup interview instead of guessing the tracker/create-mode.
  (#32)
- Human-readable tooling-tree node names, a per-pass closing report, and Learnings entries
  recording what a past attempt got wrong. (#13, #14)
- A round of fixes from the suite's first live dogfooding run against a real target repo:
  composer-audit timing, config caching, PHPUnit layout detection, `.scratch` cleanup,
  refactor-prioritize starvation, and a further batch of reviewer-loop findings. (#12, #15, #16,
  #17, #18, #36)
- Test harness (Tiers 1–5): fixture-driven regression coverage for the tooling-tree parser,
  trigger tests, and its own CI gate. (#1, #2, #3, #10, #22)
- Every skill's `SKILL.md` radically shrunk for token economy, detail moved into `references/`.
  (#33)
- Repo prepared for going public. (#37)

[0.3.0]: https://github.com/Art4/continuous-refactoring/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/Art4/continuous-refactoring/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/Art4/continuous-refactoring/releases/tag/0.1.0
