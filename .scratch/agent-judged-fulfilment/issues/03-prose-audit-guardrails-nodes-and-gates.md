# 03: Prose audit — Guardrails nodes and gates

Spec: `agent-judged-fulfilment`.

**What to build:** The same audit as for the Safety Net, for everything else the parser detects: the Guardrails nodes (dependency audit, mess detection, coverage floor, minimal PHP version, PHPStan levels above the Safety Net's leaf and the deprecation rules, semgrep), `secret-detection` and the consumers of its detection in the scan, and the description of the structural-scan gate. Every rule the parser applies but the prose lacks moves into the prose (for example a coverage-floor value read from configuration, a secret scanner recognized by CI job content, the "a Housekeeping line alone fulfils this audit-style node" path). No runtime behavior changes; the parser is untouched.

**Blocked by:** 01 (Stop-conditions become recognition-only gate nodes) — the audit node's doc is edited there too.

**Status:** implemented — PR #105, open items listed in Comments

- [x] Every Guardrails node's tree doc, `secret-detection` and the structural-scan gate description are audited; Comments list each as "prose extended" (with what was added) or "already covered".
- [ ] Every heuristic the parser applies to these nodes is stated in prose or listed as intentionally dropped, with a reason.
- [ ] The scan steps that read parser detail values today (highest PHPStan level, secret-detection state, coverage value) have prose procedures an agent can follow without the script.
- [x] The gate nodes from ticket 01 and this ticket's prose are consistent with each other.
- [x] The validation checks the repo already runs on skill and tree docs still pass.

## Comments

**PR:** [#105](https://github.com/Art4/continuous-refactoring/pull/105)

Audit outcome per node, reconstructed from `0a71f2c` (three files) and a comparison of the
pre-deletion parser (`54105f5^`) with each node's prose. The commit message records no per-node verdicts,
so "already covered" is this reconstruction.

Prose extended (`0a71f2c`, plus `30efb61` for the first item):

- `php-minimal-version` (`30efb61`): the applied PHP level is read from `rector.php`/`rector.neon`, constant
  `LevelSetList::UP_TO_PHP_XY` (`UP_TO_PHP_82` -> 8.2).
- `coverage-floor`: `.coverage-floor` is a file with one numeric percentage, absent/unparseable means no
  floor set (node stays unfulfilled); the CI half looks for the `--coverage` invocation in CI job files.
- `secret-detection`: the Fulfilment check now says the judgement identifies which scanner CI invokes
  (first match among gitleaks/detect-secrets/trufflehog), reused by `refactor-scan` step 4c. `990d4f1`
  later reworded it because the script no longer exposes a scanner name.
- `structural-scan` (gate description): an effectively rejected leaf (rejected required ancestor) counts as
  resolved, not only a directly recorded rejection.

Already covered:

- `composer-audit` (CI `composer audit` needle, the Housekeeping-line path, the real-dependency stop
  condition incl. platform pseudo-packages), `phpmd` (dep + `phpmd.xml`/`phpmd.xml.dist`/`.phpmd.xml`),
  `semgrep` (CI invocation, OWASP reference inline or in `.semgrep.yml`/`.yaml`, Housekeeping-line path),
  `has-real-dependency` (ticket 01 prose names the platform pseudo-packages).
- `phpstan-deprecation-rules`: the parser only checked that `phpstan/phpstan-deprecation-rules` is a
  dependency; the prose ("rules enabled, run green with them") is stricter, so nothing is lost.
- `test-runner-if-missing` is covered under ticket 02.

Gate consistency (item 4): `composer-audit.md`'s stop condition, `phpstan.md`'s baseline/Psalm stop
conditions and the three gate nodes' Fulfilment checks in `php-tooling-tree.md` state the same conditions.
Residual wording: `phpstan.md` still says "the parser treats them as blocked by equivalence".

Not covered (open items, see the unticked boxes):

- Item 2: `phpstan-level-6`..`-10` share the ticket-02 gap (no written "configured level >= N" predicate).
- Item 3: `refactor-scan/SKILL.md` step 4b still says to read the `detected` map from the script run and take
  the highest fulfilled `phpstan-level-N`. There is no procedure for finding that level without the script
  (the manual fallback returns only proposable/withheld sets), and the level predicate above is what such a
  procedure would need. Steps 4c (scanner identity, `secret-detection.md`) and the coverage value
  (`coverage-floor.md`) have prose procedures. Also, `structural-scan.md`'s own Fulfilment check does not
  mention the "Safety Net section present, `Open` empty" condition; it lives in `investigation-track.md`
  and ADR-0056.

Checks: validation and unit suite pass on the branch head (item 5).
