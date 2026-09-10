# `secret-detection`

Node on the generic **tooling tree** (`skills/refactor-scan/references/tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **signal**).

- **Name:** Secret Detection
- **Tool:** any secret scanner — a generic, tool-agnostic node (like `test-runner-if-missing`'s own
  `any test runner`); a concrete tool is chosen at adoption time.
- **Purpose:** CI-gated protection against committing secrets/credentials/tokens — a Signal-producing
  node, not a Safety Net one. Never gates `structural-scan`: adopting it enriches candidate selection
  (the Security signal), it doesn't hold up structural work the way the tree's deterministic-tooling
  leaves do. Proposed and ranked through the ordinary scan/prioritize cycle like any other node.
- **Fulfilment check:** a CI job that runs a recognized secret scanner (gitleaks, detect-secrets,
  trufflehog, or an equivalent) — presence of the invocation, not proof it actually fails the pipeline
  on a finding, same conservative approximation `composer-audit`'s own CI-gate check already uses.
- **MR scope:** dependency/tool setup (however the chosen scanner installs) + CI job wiring it in +
  one initial scan pass (fix or explicitly baseline what it reports — a target's own judgement call at
  adoption time, same as `phpmd`'s equivalent note).
- **Signal:** Security (`skills/refactor-prioritize/references/signals.md`) — once fulfilled,
  `refactor-prioritize`'s Select mode prefers a clean CI-gated scan as positive evidence over the
  generic (reading-the-code) recognition method for this factor.

**Out of scope for this node's own adoption MR:** a retroactive scan of the target's full git
history for secrets already committed, and filing remediation candidates for anything found — handled
separately, once this node is fulfilled, by `refactor-scan/SKILL.md` step 4c.
