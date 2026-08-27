# Tooling tree instead of a baseline skill

> Amended by [ADR-0007](0007-required-recommended-edges.md): tree edges split into **required** and **recommended**; Rector leaves the first wave and becomes suite nodes adopted in levels behind PHPStan (`docs/php-tooling-tree.md`).
>
> Amended by [ADR-0008](0008-generic-tool-tree-and-structural-scan-gate.md): `git` moves to a new generic root (`docs/tooling-tree.md`) alongside a new `loop-config` node; PHP's tree attaches beneath `loop-config` instead of `git` directly.
>
> Amended by [ADR-0010](0010-orchestrator-explicit-data-flow.md): "Scan files missing-tool and structural candidates together" no longer holds — `refactor-scan` proposes tree nodes but files nothing; issues are filed by `refactor-design` once a node is chosen.

The loop must work without a one-shot tooling onboarding. Language specialisation is a **tooling tree**: missing tools are small **candidates** (one reviewable MR each), not a `/refactor-baseline` pass that blocks the loop. Git is the only hard requirement — without it the suite does not run.

A fat floor delayed the first deepening and duplicated “setup” beside the loop. Incremental nodes keep MRs small; the MR outlook names the child the step unlocks. Fill gaps, never downgrade; an equivalent (Psalm for PHPStan, Pest for PHPUnit) fulfils the node. Rejecting a node is recorded under the target repo’s suite root (`docs/refactoring/`, default `out-of-scope/` — path overridable in that config) and closes only that subtree.

This amends ADR-0002: the loop stays language-neutral; PHP is still the first specialisation, delivered as the tree, not as a baseline-skill variant. It supersedes the file locations in ADR-0001: loop config and learned rejections live under `docs/refactoring/`, not `docs/agents/refactoring.md` / root `.out-of-scope/`. Domain ADRs stay in `docs/adr/`. Packages the suite introduces follow the target’s pinning policy; if none, caret ranges plus a committed lockfile.

## Considered Options

- **Keep `/refactor-baseline` as a start-gate** (thin or fat). Rejected: it is a second onboarding process; the loop cannot start until the floor exists.
- **Install a tool, config, and CI gate in one MR.** Rejected: too large to review; policy choices (level, fail-vs-warn) would be smuggled in as silent defaults.

## Consequences

The PHP tree has three tracks that share only git: **Composer-stack**, **standalone**, **scheduled**. First wave is Composer-stack plus a CI-runner node — not security, not DAST.

- **CI-runner** — missing only when there is no GitHub Actions or GitLab CI file. Forge from `git remote`. Existing pipeline (even deploy-only) fulfils the node; quality jobs are added later to *that* pipeline. Unknown CI (Jenkins, Circle, …): ask, do not record a rejection.
- **Composer** — `composer.json`, lockfile, install once CI can run it.
- Parallel children: **php-cs-fixer**, **Rector**, **PHPStan**, **composer audit**, **test runner** only if none exists.

Later wave (own tickets): secret detection, SAST, Trivy/Dependency-Check, DAST (needs a running instance; do not propose without one), composer-normalize/unused, coverage, mutation, analyzer plugins.

A parent node is thin: the tool is a dependency and runnable locally. Strictness, CI jobs, and ignore-lists are **children**. A CI job child has two parents: the tool and the CI-runner. If CI is not fulfilled, propose the CI-runner first; if CI was rejected, skip CI-job children and continue the tool’s other children.

**PHPStan** is the only tool whose child sequence is sketched here; the concrete steps are ticket 18. Sketch: (1) install, locally runnable, level 0, baseline file; (2) CI job if the CI-runner is fulfilled, else CI-runner or skip; then shrink the baseline, and when it is empty raise the level and re-baseline. Rector, CS-Fixer, and audit do **not** inherit that sequence from this ADR.

Scan files missing-tool and structural candidates together. Prioritise recommends an unblocked missing tree node when one exists; the human may pick a deepening. Implement and review use only fulfilled nodes.

`/refactor-baseline` is retired when the skills are updated to this ADR. Pinning, PHPStan levels, and other policy numbers are not defaults on the parent node — they are child candidates, specified when that child is designed.
