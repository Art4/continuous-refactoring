# PHP_CodeSniffer

A recognized Tool for the Role Code Style in the PHP Pack: counted when it is there, never proposed. A target that runs PHP_CodeSniffer has the Role filled, so PHP CS Fixer is out. PHP_CodeSniffer reports violations with `phpcs` and fixes the fixable ones with `phpcbf`; it reads a ruleset (`phpcs.xml`, `phpcs.xml.dist`, `.phpcs.xml`, `.phpcs.xml.dist` or `ruleset.xml`).

### `phpcs`

- **Purpose:** automated code style, so later Rector output lands styled.
- **Fulfilment check:** `squizlabs/php_codesniffer` or `phpcsstandards/php_codesniffer` is installed as a dev dependency, a ruleset is committed, and `vendor/bin/phpcs` runs locally with zero reported violations.
