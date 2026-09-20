# 03: Prose audit — Guardrails nodes and gates

Spec: `agent-judged-fulfilment`.

**What to build:** The same audit as for the Safety Net, for everything else the parser detects: the Guardrails nodes (dependency audit, mess detection, coverage floor, minimal PHP version, PHPStan levels above the Safety Net's leaf and the deprecation rules, semgrep), `secret-detection` and the consumers of its detection in the scan, and the description of the structural-scan gate. Every rule the parser applies but the prose lacks moves into the prose (for example a coverage-floor value read from configuration, a secret scanner recognized by CI job content, the "a Housekeeping line alone fulfils this audit-style node" path). No runtime behavior changes; the parser is untouched.

**Blocked by:** 01 (Stop-conditions become recognition-only gate nodes) — the audit node's doc is edited there too.

**Status:** ready-for-agent

- [ ] Every Guardrails node's tree doc, `secret-detection` and the structural-scan gate description are audited; Comments list each as "prose extended" (with what was added) or "already covered".
- [ ] Every heuristic the parser applies to these nodes is stated in prose or listed as intentionally dropped, with a reason.
- [ ] The scan steps that read parser detail values today (highest PHPStan level, secret-detection state, coverage value) have prose procedures an agent can follow without the script.
- [ ] The gate nodes from ticket 01 and this ticket's prose are consistent with each other.
- [ ] The validation checks the repo already runs on skill and tree docs still pass.
