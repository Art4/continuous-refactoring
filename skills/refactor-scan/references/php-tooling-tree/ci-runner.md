# `ci-runner`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** CI Runner
- **Tool:** GitHub Actions / GitLab CI
- **Purpose:** an existing pipeline that later hosts quality jobs.
- **Fulfilment check:** CI config file present; forge determined from `git remote`; unknown CI → ask, do not record a rejection.
- **MR scope:** pipeline file only. `composer-audit` (`composer-audit.md`) is a quality-job child with two parents (this node + `composer`). `phpunit` (`phpunit.md`) and `phpstan-level-0` (`phpstan.md`) do not get their own two-parent children — once this node is fulfilled, each self-wires its own CI gate as part of its own fulfilment check instead.
