# Secret Detection

The Tool for the Role Secret Scanning in the generic Pack, proposed only on request: Housekeeping's scan over the Git history already finds committed secrets in every cycle, and a gate reports a leak at most one rhythm earlier. Any secret scanner (gitleaks, detect-secrets, trufflehog or an equivalent), the concrete one chosen at adoption, or the forge's push protection. It reads git history and file contents directly, so it is language-neutral and in the generic Pack.

**Why this order.** A Guardrails Stage: workable only once the Safety Net is fulfilled. It waits until `ci-runner` is decided; a rejected `ci-runner` releases it.

### `secret-detection`

- **Purpose:** protection against committing secrets, credentials and tokens, on every change.
- **Fulfilment check:** a CI job runs a recognized secret scanner, the presence of the invocation, not proof that it fails the pipeline on a finding; the same conservative approximation Semgrep uses. **Or** the forge's push protection for secrets is on (GitHub's or GitLab's secret push protection), read through the forge's API. Where the run cannot read it — no forge access, a token without the right, an edition without the feature — it counts as off, and the findings say it could not be checked. A pre-commit hook alone does not fulfil it: nobody has to run it.
- **MR scope:** the scanner's setup (however it installs), a CI job wiring it in, and one initial scan of the working tree: fix what it reports or explicitly baseline it, a target's own judgement call at adoption time. Where the human prefers the forge's push protection, the merge request holds nothing for it: it is a setting the human turns on, and the run says where.
- **Out of scope:** a scan of the full git history for secrets already committed, and tickets for anything found. That is a recurring task of the Housekeeping Track, which runs this scanner once it is in place.
