# TwigStan

The recommended Tool for the Role Static Analysis in the Twig PHP Pack. It builds on PHPStan, so it plays the Role in its own scope and does not compete with PHPStan or Psalm on the PHP code.

**Why this order.** It requires `phpstan-level-5`: TwigStan reads the PHP types that reach a template through PHPStan, and its findings are only useful once the PHP side is analysed without baseline entries. It is a Guardrails Stage, workable once the Safety Net is fulfilled, because its findings in templates are not what structural work in PHP collides with. It waits until `twig-cs-fixer` is decided.

### `twigstan`

- **Purpose:** static analysis of the Twig templates against the types the PHP code hands them.
- **Fulfilment check:** the dev dependency (`twigstan/twigstan`) is installed, its config is committed and, once `ci-runner` is fulfilled, a CI job runs `vendor/bin/twigstan`; it exits without errors, with a baseline only where the Ratchet allows it.
- **MR scope:** the dependency, its config and, where the first run reports findings, the baseline it generates; no template is rewritten here.
