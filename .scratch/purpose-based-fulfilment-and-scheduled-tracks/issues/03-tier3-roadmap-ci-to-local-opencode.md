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

**Status:** done

- [x] `tier3` and the `roadmap` fixture matrix are removed from `test-harness.yml`'s gating jobs.
- [x] Both remain runnable locally via the harness's `--opencode` flag, the same invocation shape as
      `tier4`'s non-deterministic parts / `judge` / `lift` / `agent-loop` / `decision-gate-bypass`.
- [x] `fixtures/README.md` documents this posture for `tier3`/`roadmap`, with the same "no model
      credentials in CI" reasoning already given for `tier4`.
- [x] `tier1` and `tier2` remain unchanged and still gate CI.
- [x] A pull request that only changes Safety Net/Guardrails fulfilment behavior no longer fails CI due
      to stale deterministic-ground-truth expectations.

## Comments

PR: (branch `tickets/03-tier3-roadmap-local-only`, stacked on `tickets/02-guardrails-track` — link
recorded in a follow-up commit once opened, matching tickets 01/02's own convention).

Turned out to be a plain job-list edit, no split needed: `tier3` and `roadmap` were already their own
separate jobs in `test-harness.yml` (not sharing a job with `tier1`/`tier2`), each only `needs: tier1`,
so removing both job blocks outright was enough — `roadmap`'s per-fixture matrix strategy went with it.
Both functions (`run_tier3`, `run_roadmap`) and their `--opencode` support already existed unchanged in
`fixtures/harness/run.sh` from before this ticket (ticket 01/02 built the local-only pattern this one
generalizes, not the harness plumbing itself) — no `run.sh` code changes were needed, only removing the
two CI job blocks and updating docs.

Judgement calls:
- Left `CONTRIBUTING.md`/`AGENTS.md` untouched. Both already say "run the relevant `fixtures/harness/run.sh`
  tier" generically, without naming `tier3`/`roadmap` specifically — that phrasing stays accurate (running
  them locally is still good practice, just no longer CI-required), so there was nothing stale to fix.
- Beyond the ticket's own required `fixtures/README.md` update, also touched the "Tier 5" section's
  now-stale "CI gate" framing for the baseline-regression check (it described a CI `tier3` job and
  `actions/cache` step that no longer exist) and a handful of "excluded from the CI roadmap matrix"
  asides on the `php-decision-gate-bypass`/`php-safety-net-*`/`php-guardrails-*` fixtures, so the doc
  doesn't contradict itself elsewhere. No prose style invented — followed the existing "local-only,
  advisory" phrasing `tier4`/`judge`/`lift` already use throughout the file.
- Did not touch `tooling_tree.py`, `scripts/test_tooling_tree.py`, or the harness's `tier2`/`tier3`
  precision-recall *mechanism* itself (only removed `tier3`'s CI job) — explicitly out of scope per the
  spec.

Verification: `python3 -m unittest discover -s scripts -p 'test_*.py'` (339 tests, green),
`python3 scripts/validate_skills.py .` (same pre-existing advisories as `main`, no new errors/warnings).
`docker build -t test-harness fixtures/harness/` + `./fixtures/harness/run.sh tier2
php-project-with-candidates` (20/20 assertions passed) and `python3 -m unittest
scripts.test_trigger_controls -v` (tier4's deterministic module, 7 tests green) confirm `tier1`/`tier2`/
`tier4`-deterministic are unaffected. `./fixtures/harness/run.sh roadmap <fixture>` (4 fixtures spot-checked:
`php-empty`, `php-p0-nonempty`, `php-clean`, `non-php-project`) and `./fixtures/harness/run.sh tier3
php-project-with-candidates` both still run cleanly locally, unchanged in behavior — confirming the
"remains runnable locally" checklist item, not just removed from CI. `python3 -c "import yaml; ...
list(d['jobs'].keys())"` on the edited workflow confirms the gating job list is now exactly
`['tier1', 'tier2', 'tier4']`.
