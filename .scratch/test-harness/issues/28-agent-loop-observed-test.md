# 28 — Agent loop test: full-pass, subagent-observed run against fixtures

**Type:** build

**What to build:** Formalize the manual dry-run methodology used to validate ADR-0010 (isolated fixture copy, local issue-tracker override, an Agent-tool subagent following the real `SKILL.md` texts literally, friction reported instead of silently fixed) as a repeatable harness stage against this repo's own fixtures, instead of an ad-hoc scratch copy of an unrelated project.

Unlike `roadmap --opencode` (drives only `refactor-scan`'s proposal step via `opencode` in a Docker subprocess this script can launch itself), this drives the full 6-step orchestrator pass via a Claude Code Agent-tool subagent, which cannot be started from Bash — the harness stage prepares the sandbox + prompt only; running the subagent is a manual step. Same local-only, non-CI scope as `--opencode` (advisory, not a deterministic gate), for the same reason: LLM output isn't deterministic.

Related to ticket 27's Tier 4 sketch ("trigger tests", "LLM-judge rubric grading") but scoped concretely to one thing: observing a real full pass end-to-end against a real fixture, not a broader trigger/negative-control suite.

- [x] `fixtures/harness/run.sh agent-loop <fixture>`: reuses `setup_fixture`, seeds a local issue-tracker override (`docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, `.scratch/refactor/issues/`, minimal `CONTEXT.md`, `docs/adr/`), writes a ready-to-use subagent prompt, prints the manual next step
- [x] `fixtures/harness/lib/assertions.sh`: `assert_git_has_new_commits` — advisory post-run sanity check, not a hard gate
- [x] `fixtures/README.md`: "Agent loop test (full pass, subagent-observed)" section — usage, what it seeds, what to inspect afterward, why it stays local/manual
- [x] Verified once for real: `agent-loop php-partial` sandbox + prompt generated, then an Agent-tool subagent run against it, output inspected

**Blocked by:** —

**Status:** done

## Comments

> **2026-08-27:** Built directly (no separate grilling round — the shape was already established by the manual ADR-0010 dry runs; this just relocates that methodology into the repo's own harness). Verified with a real subagent run against `php-partial`.
