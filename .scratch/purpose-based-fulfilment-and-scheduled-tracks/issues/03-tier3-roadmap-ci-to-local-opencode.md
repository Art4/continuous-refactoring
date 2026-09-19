# 03: `tier3`/`roadmap` out of the CI gate, local-only via an opencode subagent

**What to build:** Once tickets 01/02 land, `tier3` (Ground Truth) and the `roadmap` fixture matrix no
longer test anything meaningful in CI — both assert against `tooling_tree.py`'s own deterministic output
for Safety Net/Guardrails nodes, which is no longer the operative fulfilment path for those nodes, and CI
has no model credentials to run an agent-judged check instead. Both jobs are removed from
`test-harness.yml`'s gating jobs and become local-only, run through the harness's existing `--opencode`
flag — the same advisory/local-only posture `tier4`'s non-deterministic parts, `judge`, `lift`,
`agent-loop`, and `decision-gate-bypass` already use. `tier1` (static validation) and `tier2` (artifact
contracts) are unaffected and keep gating CI as before.

**Blocked by:** 01, 02

**Status:** ready-for-agent

- [ ] `tier3` and the `roadmap` fixture matrix are removed from `test-harness.yml`'s gating jobs.
- [ ] Both remain runnable locally via the harness's `--opencode` flag, the same invocation shape as
      `tier4`'s non-deterministic parts / `judge` / `lift` / `agent-loop` / `decision-gate-bypass`.
- [ ] `fixtures/README.md` documents this posture for `tier3`/`roadmap`, with the same "no model
      credentials in CI" reasoning already given for `tier4`.
- [ ] `tier1` and `tier2` remain unchanged and still gate CI.
- [ ] A pull request that only changes Safety Net/Guardrails fulfilment behavior no longer fails CI due
      to stale deterministic-ground-truth expectations.
