# Easy Coding Standard

A recognized Tool for the Role Code Style in the PHP Pack: counted when it is there, never proposed. A target that runs ECS has the Role filled, so PHP CS Fixer is out. ECS runs PHP CS Fixer and PHP_CodeSniffer rules from one config.

### `ecs`

- **Purpose:** automated code style, so later Rector output lands styled.
- **Fulfilment check:** `symplify/easy-coding-standard` is installed as a dev dependency, a config is committed (`ecs.php`), and `vendor/bin/ecs check` runs locally with zero reported diffs.
