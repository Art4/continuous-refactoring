- Dev-repo CI: `tier3` (Ground Truth) and the `roadmap` fixture matrix no longer gate `test-harness.yml`.
  Both asserted against `tooling_tree.py`'s own deterministic, hardcoded-dependency-name matching for
  Safety Net/Guardrails nodes — which tickets 01/02 (ADR-0055) made no longer the operative fulfilment
  path for those nodes — and CI has no model credentials to run the agent-judged check that replaced it.
  Both remain runnable locally via `fixtures/harness/run.sh`'s existing `--opencode` flag, the same
  local-only/advisory posture `tier4`'s non-deterministic parts, `judge`, `lift`, `agent-loop`, and
  `decision-gate-bypass` already use. `tier1`/`tier2` are unaffected and still gate CI.
