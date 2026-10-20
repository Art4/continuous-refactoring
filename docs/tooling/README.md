<!-- Generated from the Packs by scripts/tooling_docs.py — do not edit. Regenerate with: python3 scripts/tooling_docs.py -->

# Tooling: Roles, Tools and Packs

What a tool is for (Roles), which tools can play them, and the Packs the tools come in. The words are defined in the suite's glossary; the rules are in [tooling-model.md](../../skills/continuous-refactoring/references/tooling-model.md).

## Packs

| Pack | Applies when |
| --- | --- |
| [generic](packs/generic.md) | Always. |
| [php](packs/php.md) | The repository contains PHP code: a composer.json (or composer/composer.json), or at least one *.php file outside vendor/. |
| [twig-php](packs/twig-php.md) | The PHP Pack applies and composer.json (or, for an indirect requirement, composer.lock) requires twig/twig or a package that brings Twig along, such as symfony/twig-bundle. The file extension of the templates does not decide. |

## Roles

| Role | Purpose | Signal | Tools |
| --- | --- | --- | --- |
| Editor Settings (`editor-settings`) | The basic formatting conventions (indentation, charset, line endings) are written down once, for every editor. | – | .editorconfig (recommended, generic) |
| Continuous Integration (`continuous-integration`) | A pipeline that runs the quality jobs on every change. | – | CI Runner (recommended, generic) |
| Package Management (`package-management`) | Dependencies are declared and installed by a package manager. | – | Composer (recommended, php) |
| Autoloading (`autoloading`) | Classes are found by a convention, not by hand-written includes. | – | PSR-4 Autoloading (recommended, php) |
| Code Style (`code-style`) | An automatic fixer keeps the code in one style, so later automated rewrites land styled. | – | PHP CS Fixer (recommended, php); Laravel Pint (recognized, php); Easy Coding Standard (recognized, php); PHP_CodeSniffer (recognized, php); Twig-CS-Fixer (recommended, twig-php) |
| Testing (`testing`) | A test suite that runs locally and catches regressions. | – | PHPUnit (recommended, php) |
| Test Coverage (`test-coverage`) | The share of the code the tests reach is measured and may not fall. | Untested / hard-to-test | Test Coverage Floor (recommended, php) |
| Static Analysis (`static-analysis`) | A tool reads the code without running it and reports defects, at a level of strictness the project raises step by step. | – | PHPStan (recommended, php); Psalm (recognized, php); TwigStan (recommended, twig-php) |
| Taint Analysis (`taint-analysis`) | A tool follows data from untrusted input to dangerous operations. | Security | Psalm Taint Analysis (recommended, php) |
| Automated Refactoring (`automated-refactoring`) | Rule sets rewrite code mechanically, one reviewable set at a time. | – | Rector (recommended, php) |
| Code Smell Detection (`code-smell-detection`) | A tool measures complexity and flags code that is hard to read. | Understandability | PHPMD (recommended, php) |
| Dependency Audit (`dependency-audit`) | Known vulnerabilities in the third-party dependencies are reported and gate the pipeline. | Security | Composer Audit (recommended, php) |
| Secret Scanning (`secret-scanning`) | Committed secrets and credentials are found before they ship. | Security | Secret Detection (recommended, generic) |
| Static Security Analysis (`static-security-analysis`) | A rule-based scanner looks for common vulnerability patterns in the source. | Security | Semgrep (OWASP Top 10) (recommended, php) |
| Runtime Floor (`runtime-floor`) | The declared minimum runtime version matches what the code demonstrably needs. | – | PHP Minimum Version (recommended, php) |
