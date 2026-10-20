# Twig-CS-Fixer

The recommended Tool for the Role Code Style in the Twig PHP Pack. It plays the Role in its own scope, so PHP CS Fixer, Laravel Pint and Easy Coding Standard keep theirs on the PHP code and neither takes the other's place.

**Why this order.** It is a Guardrails Stage, workable once the Safety Net is fulfilled: no Safety Net Stage rewrites templates, so the formatting pass collides with no structural work in PHP, and a Twig-only style pass must not hold the Safety Net, and with it every PHP Guardrails Stage, back. It waits until `editorconfig` is decided, so the basic formatting conventions are settled before Twig style rules arrive; a rejected `editorconfig` releases it. `twigstan` waits until it is decided, so the analyser reads templates that are already styled.

### `twig-cs-fixer`

- **Purpose:** automated code style for the Twig templates: the fixer rewrites them in place (`lint --fix`), so TwigStan reads templates that are already styled.
- **Fulfilment check:** a dev dependency (`vincentlanglet/twig-cs-fixer`) is installed, a config is committed (`.twig-cs-fixer.php`), and `vendor/bin/twig-cs-fixer lint` reports no violations on the template paths. The extensions it checks are the ones the project's templates use; `.twig` is only its default.
- **MR scope:** the dependency, the config naming the template paths and extensions, and one formatting pass over the templates (`vendor/bin/twig-cs-fixer lint --fix`).
