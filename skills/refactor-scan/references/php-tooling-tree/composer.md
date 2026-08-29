# `composer`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** Composer
- **Tool:** Composer
- **Purpose:** dependency management for the Composer-stack track.
- **Fulfilment check:** `composer.json` present; `composer.lock`'s git treatment matches `composer.json`'s `type` — committed for `type: project` (or any other non-library type), gitignored for `type: library`; install runs locally and once CI can run it.
- **MR scope:** composer files and lockfile per the type-dependent rule above; `vendor/` added to `.gitignore`; a missing or generic `description` in `composer.json` is derived from the target repo's README or existing code where possible, left empty if it can't be derived; no tool adoption inside this MR.
