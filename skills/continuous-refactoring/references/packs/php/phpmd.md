# PHPMD

The Tool for the Role Code Smell Detection in the PHP Pack.

**Why this order.** A Guardrails Stage: workable only once the Safety Net is fulfilled, and it needs Composer. Adopting it enriches the search for structural candidates; it never holds structural work up.

### `phpmd`

- **Purpose:** cyclomatic-complexity and code-quality measurement. Once fulfilled, the search for structural candidates reads its real output for the Understandability factor (nested conditionals, long methods, deep coupling) and for Defect density (complexity correlates with bug rates), both in `../../signals.md`, in place of the generic recognition method.
- **Fulfilment check:** the dev dependency `phpmd/phpmd` is installed, a ruleset config is committed (`phpmd.xml`, `phpmd.xml.dist` or `.phpmd.xml`), and it runs locally.
- **MR scope:** the dependency, the ruleset config and one pass over the codebase: fix what the initial run reports or explicitly baseline it, a target's own judgement call at adoption time.
