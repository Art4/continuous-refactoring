# `composer-audit`

Node on the PHP **tooling tree** (`../php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**, **Signal wave**).

- **Name:** Composer Audit
- **Tool:** composer audit
- **Purpose:** dependency vulnerability visibility, enforced as a CI gate (absorbs what was originally
  tracked as a separate dependency-vulnerability-scan concern, now folded into this node). A **Signal
  wave** node — moved out of the Safety
  Net (it used to carry a `resolved` edge into `php-safety-net`): third-party CVEs are findings a
  target's own structural refactoring neither creates nor fixes, unlike `psalm-taint-analysis`'s own
  taint-flow findings, which stayed a Safety Net leaf.
- **Required parents:** `composer` (unchanged) and, additionally, `php-safety-net` — kept additive
  rather than replacing `composer` outright, because a *rejected* `composer` must still permanently close
  this node the ordinary required-edge way; a bare `php-safety-net` edge alone wouldn't do that (a
  rejected `resolved` parent still counts as resolved). `ci-runner` is a **recommended**, not required,
  parent (downgraded from required — see *Fulfilment check* below for why dropping it outright would
  have lost real gating value).
- **Fulfilment check:** a CI job exists that runs `composer audit` (the pipeline fails when it reports a
  known advisory), **or** a line naming this node is already committed to the Refactoring Notes'
  `housekeeping-template.md` (`../../../continuous-housekeeping/references/housekeeping-template-file-format.md`) — no
  proof of a completed run required, matching every other CI-gated check in this tree (presence/invocation
  is sufficient, never proof of a passing run history). The second path exists because `ci-runner` is now
  only a recommended parent: a target with no CI at all can still fulfil this node by adopting `composer
  audit` locally and committing the Housekeeping line that promises to keep reviewing it, the same
  "local adoption alone still fulfils" shape `phpunit`/`phpstan`/`psalm` already have — this node and
  `semgrep` are the first two audit-style nodes to get it (point-in-time audits whose value is in
  repetition, not one-time adoption), documented here as the pattern to reuse once further audit-style
  nodes are added (more are planned).
- **MR scope:** wire `composer audit` into CI as a gate — no production-code change. Also contribute this node's `Housekeeping` line (below) to the Refactoring Notes' `housekeeping-template.md`, creating that file fresh if it doesn't exist yet (`../../../continuous-housekeeping/references/housekeeping-template-file-format.md`).
- **Housekeeping:** review `composer audit`'s current report; attempt a fix for any advisory with an available patched version. A CI gate only fails on advisories present *right now* — it never surfaces one that appears later against an already-passing, unchanged lockfile.
- **Stop conditions / when not to propose:** `composer` fulfilled is necessary but not sufficient — this
  node also stays blocked until `composer.json`'s `require` block names at least one real package
  (platform pseudo-packages — `php`, `hhvm`, `ext-*`, `lib-*`, `composer-plugin-api`,
  `composer-runtime-api` — don't count; `composer audit` has nothing to check without a real dependency).
  There is no longer a fallback for a dependency-free target — this node isn't a `php-safety-net` leaf
  any more, so leaving it permanently blocked no longer risks leaving `structural-scan` blocked with it.
