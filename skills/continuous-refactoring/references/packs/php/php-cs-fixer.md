# PHP CS Fixer

The recommended Tool for the Role Code Style in the PHP Pack. Laravel Pint (`pint.md`) and Easy Coding Standard (`ecs.md`) are recognized: on a target that runs either, the Role is filled, PHP CS Fixer is out and is not proposed.

**Why this order.** It waits until `editorconfig` is decided, so the target's basic formatting conventions are settled before language-specific style rules arrive; a rejected `editorconfig` releases it. `rector-php-set` waits until it is decided, so Rector's rewrites land on already-styled code.

### `php-cs-fixer`

- **Purpose:** automated code style, so later Rector output lands styled.
- **Fulfilment check:** a dev dependency (`friendsofphp/php-cs-fixer` or `php-cs-fixer/php-cs-fixer`) is installed, a config is committed (`.php-cs-fixer.php` or `.php-cs-fixer.dist.php`), and it runs locally with zero reported diffs.
- **MR scope:** the dependency, the config and one formatting pass.
