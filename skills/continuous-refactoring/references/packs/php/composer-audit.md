# Composer Audit

The Tool for the Role Dependency Audit in the PHP Pack. It has a minimum runtime of PHP 7.2 (`pack.json`).

**Why this order.** A Guardrails Stage: third-party advisories are findings a target's own structural refactoring neither creates nor fixes. It needs Composer, and waits until `ci-runner` is decided so the gate has a pipeline to live in; a rejected `ci-runner` releases it.

### `composer-audit`

- **Purpose:** dependency vulnerability visibility, enforced as a CI gate.
- **Applies when:** `composer.json`'s `require` block names at least one real package. Platform pseudo-packages (`php`, `hhvm`, `ext-*`, `lib-*`, `composer-plugin-api`, `composer-runtime-api`) do not count; `composer audit` has nothing to check without a real dependency. This is the Stage's own condition in `pack.json`, judged by the agent like a Pack's: without it the Stage is handed in as `not_applicable` and gets no ticket.
- **Fulfilment check:** a CI job exists that runs `composer audit` (the pipeline fails when it reports a known advisory), **or** a line naming this Stage is already committed to the target's Housekeeping template. Presence of the invocation is enough, never proof of a passing run history. The second path lets a target with no CI adopt `composer audit` locally and commit the Housekeeping line that promises to keep reviewing it; the same "local adoption alone still fulfils" shape PHPUnit and PHPStan have. Semgrep follows the same pattern for point-in-time audits whose value is in repetition.
- **MR scope:** wire `composer audit` into CI as a gate; no production-code change. Also add the Housekeeping line below to the target's Housekeeping template (`../../implement-point.md`, *Slices every kind of ticket can have*).
- **Housekeeping:** review `composer audit`'s current report; attempt a fix for any advisory with a patched version available. A CI gate only fails on advisories present right now; it never surfaces one that appears later against an unchanged lockfile.
