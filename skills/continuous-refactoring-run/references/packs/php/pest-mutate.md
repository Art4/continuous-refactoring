# Pest Mutation Testing

A recognized Tool for the Role Mutation Testing in the PHP Pack: counted when it is there, never proposed.
Pest has mutation testing built in since version 3 (`pest --mutate`). A target that runs it has the Role
filled, so Infection is out. Unlike Infection, Pest mutates by default only the code a test file names with
`covers()` or `mutates()`; `--everything` widens it to all of it.

### `pest-mutate`

- **Purpose:** judge the tests by the faults they catch, not by the lines they reach (`infection.md`).
- **Fulfilment check:** Pest 3 or later is a dev dependency, and a CI job runs `pest --mutate`, with a
  minimum score (`--min`). With no CI, a local run of `pest --mutate` that meets its minimum.
