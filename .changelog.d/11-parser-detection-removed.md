- `skills/refactor-scan/references/tooling_tree.py` no longer detects anything: the hardcoded
  dependency-name detection and the forward-simulating `roadmap` output are deleted, and the script now
  takes a fulfilment seed (`--seed`, or the Refactoring Notes' `fulfilled-set.json`) or derives state
  from `bookkeeping.md`'s Track sections, computing the tree's graph logic only — the ordered `Open`
  backlog, workable and withheld nodes with reasons, rejection cascades, PHP-floor findings, and the
  merge-request outlook (`--unblocked-by`). The harness's `roadmap` tier and the eight
  `expected/roadmap.json` fixtures are removed with it; the drift check comparing the manual tree-walk
  fallback with the script's graph logic continues as `scripts/drift_check.py`, advisory and run
  manually (never collected by CI's `test_*.py` discovery).
