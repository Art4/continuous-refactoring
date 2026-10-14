# `secret-detection`

Node on the generic **tooling tree** (`../tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **signal**, **Guardrails**).

- **Name:** Secret Detection
- **Tool:** any secret scanner
- **Purpose:** CI-gated protection against committing secrets/credentials/tokens — a Signal-producing
  node, not a Safety Net one. Never gates `structural-scan`: adopting it enriches the search for
  structural candidates (the Security signal), it doesn't hold up structural work the way the tree's
  deterministic-tooling leaves do.
  A generic, tool-agnostic node (like `test-runner-if-missing`'s own `any test runner`); a concrete tool is chosen at adoption time.
- **Required parent:** `structural-scan` (`../tooling-tree.md`'s own gate) — a **Guardrails** node
  (`CONTEXT.md`): workable only once the Safety Net is fulfilled, not from `onboarding-setup` directly, so a
  target's first runs are never asked to wire up a secret scanner before the deterministic
  Safety Net has settled. Stays outside
  `php-safety-net` on purpose — it's language-neutral, gated on the generic root's own
  `structural-scan` directly rather than any language specialization's aggregation node.
- **Fulfilment check:** a CI job that runs a recognized secret scanner (gitleaks, detect-secrets,
  trufflehog, or an equivalent) — presence of the invocation, not proof it actually fails the pipeline
  on a finding, same conservative approximation `composer-audit`'s own CI-gate check already uses.
  The scanner this CI job invokes is the one Housekeeping's scan over the Git history runs.
- **MR scope:** dependency/tool setup (however the chosen scanner installs) + CI job wiring it in +
  one initial scan of the working tree (fix or explicitly baseline what it reports — a target's own
  judgement call at adoption time, same as `phpmd`'s equivalent note).
- **Signal:** Security (`../signals.md`) — once fulfilled, the search for structural candidates reads the
  scanner's findings as the evidence for this factor, in place of the generic (reading-the-code)
  recognition method.

**Out of scope for this node's own adoption MR:** a scan of the target's full git history for secrets
already committed, and tickets for anything found — that is a recurring task of the Housekeeping Track.
