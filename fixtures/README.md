# Fixtures

Small sample projects a target could look like. Each lives under `php/<name>/project/` and is a complete
repository tree; copy one to a temporary folder, run `git init` in it, and it is a target to try the
suite against by hand.

| Fixture | The project |
| --- | --- |
| `non-php-project` | A static site: HTML, CSS, JavaScript. No `composer.json` |
| `php-empty` | PHP source files and nothing else: no Composer, no tooling |
| `php-partial` | Composer, PHPUnit and PHP CS Fixer; no static analysis, no CI |
| `php-project-with-candidates` | Composer only, with five planted structural problems |
| `php-psalm` | Composer, PHPUnit and Psalm |
| `php-p0-empty` | CI, PHP CS Fixer, PHPUnit and PHPStan at level 0 with an empty baseline |
| `php-p0-nonempty` | The same, with entries in the PHPStan baseline |
| `php-own-pack` | A project with a Pack of its own: Deptrac with a Role the suite does not have, and Mago in place of PHPStan |
| `php-own-pack-clash` | The same kind of project, whose Pack reuses the slug `phpunit` of the suite's: the parser refuses it |
| `php-twig` | Composer requiring `twig/twig`, with one template named `page.html.twig` |
| `php-clean` | A well-kept project: `.editorconfig`, CI, PHP CS Fixer, PHPUnit with a coverage floor, PHPStan, PHPMD, Rector |

Where a fixture has `expected/issues/`, those files describe the structural problems planted in its
source — the shallow service, the SQL injection, the hard-coded secret, the unused class, the style
violations. They are the ground truth an exploration of that project should come upon.

## What is tested where

- **The tooling-tree parser** — `python3 -m unittest scripts.test_tooling_tree`. The tests build their
  own small repositories and Packs; they do not read these fixtures.
- **Negative controls for the parser** — `python3 -m unittest scripts.test_trigger_controls`.
- **The skill texts** — `python3 scripts/validate_skills.py .`: references that do not exist, glossary
  use, avoided terms.

No automated check runs an agent against a fixture. How a run behaves is observed in a real target.
