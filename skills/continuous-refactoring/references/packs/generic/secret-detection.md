# Secret Detection

The Tool for the Role Secret Scanning in the generic Pack: any secret scanner (gitleaks, detect-secrets, trufflehog or an equivalent); the concrete one is chosen at adoption. It reads git history and file contents directly, so it is language-neutral and in the generic Pack.

**Why this order.** A Guardrails Stage: it is workable only once the Safety Net is fulfilled, so a target's first runs are never asked to wire up a secret scanner before the deterministic tooling has settled. It never holds the Safety Net up.

### `secret-detection`

- **Purpose:** CI-gated protection against committing secrets, credentials and tokens. Once fulfilled, the search for structural candidates reads the scanner's findings as the evidence for the Security signal (`../../signals.md`), in place of the generic recognition method.
- **Fulfilment check:** a CI job runs a recognized secret scanner. It is the presence of the invocation, not proof that it fails the pipeline on a finding; the same conservative approximation Semgrep uses. The scanner this CI job invokes is the one Housekeeping's scan over the Git history runs.
- **MR scope:** the scanner's setup (however it installs), a CI job wiring it in, and one initial scan of the working tree: fix what it reports or explicitly baseline it, a target's own judgement call at adoption time.
- **Out of scope:** a scan of the full git history for secrets already committed, and tickets for anything found. That is a recurring task of the Housekeeping Track.
