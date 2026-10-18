# Composer

The Tool for the Role Package Management in the PHP Pack. Most PHP Tools wait for it.

### `composer`

- **Purpose:** dependency management for the Composer stack.
- **Fulfilment check:** `composer.json` is present; `composer.lock`'s git treatment matches `composer.json`'s `type`: committed for `type: project` (or any other non-library type), gitignored for `type: library`. Install runs locally, and in CI once CI can run it.
- **MR scope:** the composer files and the lockfile per the type-dependent rule above; `vendor/` added to `.gitignore`; a missing or generic `description` in `composer.json` is derived from the target repo's README or existing code where possible, left empty if it cannot be derived. No tool adoption inside this merge request. Also add the Housekeeping line below to the target's Housekeeping template (`../../implement-point.md`, *Slices every kind of ticket can have*).
- **Housekeeping:** run `composer update`; record the output.
