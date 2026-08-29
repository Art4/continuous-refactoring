# `composer`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**, **Learnings**).

- **Tool:** Composer
- **Purpose:** dependency management for the Composer-stack track.
- **Fulfilment check:** `composer.json` plus committed lockfile; install runs locally and once CI can run it.
- **MR scope:** composer files and lockfile; no tool adoption inside this MR.
- **Learnings:**
  - `composer.json`'s `type` decides `composer.lock`'s git treatment: `library` → `composer.lock` goes in `.gitignore`, not committed; `project` (or any other non-library type) → `composer.lock` is committed.
  - A missing or generic `description` in `composer.json` is derived from the target repo's README or existing code where possible; if it can't be derived, it's left empty rather than filled with a placeholder.
  - `vendor/` always belongs in `.gitignore`, regardless of type.
