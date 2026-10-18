# Semgrep (OWASP Top 10)

The Tool for the Role Static Security Analysis in the PHP Pack. A standalone binary, Python or Docker tool, not a Composer dependency, and it needs no Composer at all.

**Why this order.** A Guardrails Stage: workable only once the Safety Net is fulfilled. It waits until `ci-runner` is decided; a rejected `ci-runner` releases it.

### `semgrep`

- **Purpose:** broad OWASP Top 10 coverage for the search for structural candidates. It complements Psalm Taint Analysis rather than duplicating it: taint analysis follows tainted data flow (strongest for injection-class bugs: A03, A01, A10), while Semgrep's OWASP Top 10 registry ruleset also catches pattern-matchable categories taint analysis does not reach: crypto misuse (A02), misconfiguration (A05), logging gaps (A09). Once fulfilled, the search prefers its real findings, alongside Psalm Taint Analysis's, over the generic recognition method for the Security signal (`../../signals.md`).
- **Fulfilment check:** a CI job invokes `semgrep` with an OWASP Top 10 ruleset (the registry config `p/owasp-top-ten`, inline in the CI invocation or inside a committed `.semgrep.yml` / `.semgrep.yaml`). Presence of the invocation, not proof that it fails the pipeline on a finding. **Or** a line naming this Stage is already committed to the target's Housekeeping template; the fallback is described in full under Composer Audit (`composer-audit.md`).
- **MR scope:** Semgrep wired into CI (however it installs: pip, Docker or a marketplace CI action; never a `composer.json` entry) with the OWASP Top 10 registry ruleset, plus one initial scan pass: fix what it reports or explicitly baseline it, a target's own judgement call at adoption time. No separate "security checklist" document; the tool's own deterministic CI findings are the check. Also add the Housekeeping line below to the target's Housekeeping template (`../../implement-point.md`, *Slices every kind of ticket can have*).
- **Housekeeping:** re-run Semgrep's OWASP Top 10 ruleset periodically and review new findings; a point-in-time scan whose value is in repetition, the same reasoning as Composer Audit's.
