# Changelog

All notable changes to this project are documented here. Format inspired by
[Keep a Changelog](https://keepachangelog.com/), kept flat (no `Added`/`Changed`/`Fixed`
subcategories) — see `CONTRIBUTING.md`'s "Changelog" section for how entries are produced.

## [0.4.0] - 2026-09-15

- `refactor-prioritize` now selects and minimally files a structural or PHPStan-baseline-shrink
  candidate itself (a second, fresh dispatch — "Select mode"), the moment one is chosen — visible
  on the tracker right away instead of only once its full plan is finished. `refactor-design`
  grounds and grills that already-filed candidate afterward, adding the plan as a comment rather
  than filing a second issue. (#63)
- `refactor-prioritize`'s Select mode now files every genuine structural/PHPStan-baseline-shrink
  candidate it finds, not just the strongest — sorted into a `refactor:priority` tier (Security or
  Blast-Radius-of-inaction signals, exempt from `refactor-scan`'s backlog cap) or the ordinary
  capped tier. New `signals.md` catalogues seven additional Signal factors (Security, defect
  density, blast radius of inaction, understandability, observability, domain/business criticality,
  timing) used only in Select mode's own candidate search and ranking. `CONTEXT.md` gains a
  `Signal` glossary entry; `docs/playbooks/loop.md` introduces "Safety Net" as a human-facing
  reading aid for the existing tooling tree. (#64)
- Two new Signal-producing tooling-tree nodes — `phpmd` (PHP tree) and `secret-detection` (generic
  root) — are real, adoptable nodes now, not just `signals.md` documentation; once adopted,
  `refactor-prioritize`'s Select mode reads their real tool output for the
  Understandability/Defect-density and Security factors instead of the generic recognition method.
  Neither carries a `resolved` edge into `structural-scan` — adopting them enriches candidate
  selection, they never gate structural work. Node docs gain an optional `Signal` field (mirroring
  the existing `Housekeeping` field). Three PHP-tree edges simplified: `test-runner-if-missing`
  drops its direct `php-structural-scan` resolved edge (`ci-runner` already gates `structural-scan`
  independently); `php-cs-fixer` drops its own direct resolved edge in favor of a new `recommended`
  edge into `rector-php-set`; the PHPStan level chain's resolved-leaf moves from level 10 to level 5
  (its first structural fork point), leaving levels 6–10 ordinary, non-gating, still-proposable
  nodes. (#65)
- `php-minimal-version` no longer proposes raising `composer.json`'s declared PHP floor beyond what
  the codebase's own code already requires — only a Floor correction (bringing the declared floor
  in line with syntax `rector-php-set` has already landed) is ever auto-proposed now, never a Floor
  raise (committing the application to a newer PHP than its code currently needs, a real breaking
  change). `CONTEXT.md` gains `Floor correction`, `Floor raise`, and `Breaking change` glossary
  entries. (#67)
- `psr-4` now also wires Composer's autoloader (`vendor/autoload.php`) into the target's own
  composition root (or every entry point when there's none), on top of its existing check that the
  mapping mechanism actually works — closing the gap where a target could adopt PSR-4 yet keep
  loading classes by hand indefinitely. `CONTEXT.md` gains `Entry point` and `Composition root`
  glossary entries. (#68)
- `refactor-scan` now runs a one-time full git-history secret scan once `secret-detection` is
  fulfilled, reusing the same scanner already gating CI and its own baseline mechanism to avoid
  re-filing known findings — each new finding becomes a `refactor:priority` candidate issue (the
  secret's value redacted), filed by `refactor-learn`. (#71)
- New `coverage-floor` tooling-tree node (PHPUnit child, Signal-producing — no `structural-scan`
  gating): measures test coverage against a self-tightening ratchet committed to the target repo
  (`.coverage-floor`, only ever rises via a normal reviewed commit, never auto-bumped by CI) instead
  of a fixed percentage. Driver-agnostic — PCOV is the adoption default, Xdebug works too. (#72)
- New `semgrep` tooling-tree node (OWASP Top 10 static analysis, Signal-producing — no
  `structural-scan` gating): complements the existing `psalm-taint-analysis` node rather than
  duplicating it (crypto misuse, misconfiguration, and logging-gap categories taint analysis
  doesn't reach on its own). No separate manual security checklist — the tool's own CI-gated
  findings supersede it. (#73)
- `psr-4`'s autoloader-wiring check now reports exactly which entry points still need
  `vendor/autoload.php` wiring instead of only a boolean — a tooling-tree node's own generated
  CI-helper script can structurally never need it, and telling that apart from genuine unaddressed
  application work is now a documented judgement call, not a guess the parser itself makes. (#74)
- The suite now has an official website, [continuous-refactoring.de](https://continuous-refactoring.de/),
  linked from `README.md` and set as this GitHub repo's homepage URL. (#75)
- Every currently-unblocked tooling-tree node now gets a minimal candidate issue filed as soon as
  it's proposable, not just the one the loop picks to work on next — giving a human a chance to
  comment or reject a proposed tool before any implementation work is spent on it. `loop-config`'s
  own onboarding interview now summarizes the concrete decisions and actions about to happen before
  writing anything; a cold-start pass on a target with no Refactoring Notes yet skips straight to
  proposing `loop-config` instead of walking the whole tooling tree first. (#76)
- `Skip streak` is gone — replaced by two signals `refactor-prioritize`'s Rank mode now reads
  directly off each proposal's own pre-filed issue: its age, and a human-settable
  `refactor:priority` label (a hard override — narrows the candidate pool to only priority-labeled
  proposals when any exist). Local Markdown issue trackers gain a `Filed: YYYY-MM-DD` line so age
  is readable there too. (#77)
- Suite merge requests no longer stack — every branch this suite opens now always branches directly
  off the default branch, unconditionally. Reverses an earlier decision after two real incidents
  where a stacked PR got silently auto-closed by the forge when its base branch was deleted on
  merge. (#78)
- Fixed a bug where a target with a rejected `composer` node (out of scope) could get permanently
  stuck with zero proposable tooling-tree candidates, never reaching `structural-scan`, even though
  the rejection should have cascaded down and resolved everything beneath it — the internal
  gate-closure checks mistook a legitimate diamond-shaped dependency for a cycle and returned a
  false negative. (#79)
- `rector-type-coverage` and `semgrep` now carry a `composer` required parent, alongside their
  existing recommended parent(s) — they were the only two nodes in the whole tooling tree with no
  required/required-any chain back to `composer` at all, so a rejected `composer` could never
  automatically close them, forcing a manual issue-file-and-reject cycle on a target with no PHP
  application code. (#79)
- Clarified `CONTEXT.md`'s `Recommended edge`/`decided` definition: a recommended parent counts as
  decided-rejected not only via its own `out-of-scope/` entry, but also transitively, when one of
  its own required ancestors is rejected — a rule the tooling has always implemented but the
  glossary never stated. (#80)
- `refactor-design` now applies a pre-implementation decision gate while grounding/grilling or
  planning a fix: a design decision that's hard to reverse, surprising without context, or a real
  trade-off — while the candidate itself stays behavior-preserving — gets written as a plan with a
  proposed default plus an explicit open question on the candidate issue, and the existing
  `ready-for-agent` label is deliberately withheld until a human confirms or overrides it. A genuine
  breaking change discovered mid-design is now handled too: `refactor-design` hands it forward as a
  finding, and `refactor-learn`'s closing call applies its existing rejection machinery (`wontfix`,
  a closing note or `out-of-scope/` entry). (#82)
- A new shared reference tells every lifecycle skill how to write text that lands on the target
  repo's own forge (issue comments, closing notes, `out-of-scope/` entries, merge request
  descriptions): the reader has never seen this suite's own repo, so skills no longer cite this
  suite's own file paths or use its controlled-vocabulary labels as justification — they state the
  rule or finding itself in plain words instead. (#83)
- `refactor-learn` now requires a genuine event (a finding, a freshly opened merge request, or a
  design-time breaking-change finding) before it writes anything — a call with nothing to react to
  stops immediately instead of opening a bookkeeping merge request that only refreshed the
  `Fulfilled nodes` cache, and checks only what it was actually handed rather than independently
  investigating to find a reason to act. `refactor-design` now reads existing issue comments, not
  just the body, everywhere it grounds itself in a candidate, and posts a **Decision trail** comment
  recording any grilling question that met the ADR bar, separate from the decision gate. A
  tooling-tree candidate's "what this unlocks next" note moves off the merge request description
  and onto the candidate's own issue. `Secret history scan: done` now carries the date it ran.
  `refactor-scan` also now resolves `tooling_tree.py` relative to wherever the suite's skills are
  actually installed rather than assuming the suite's own repo is the current working directory —
  no more sub-agent dispatch just to locate it when running from a target repo. (#84)

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

[0.4.0]: https://github.com/Art4/continuous-refactoring/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/Art4/continuous-refactoring/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/Art4/continuous-refactoring/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/Art4/continuous-refactoring/releases/tag/0.1.0
