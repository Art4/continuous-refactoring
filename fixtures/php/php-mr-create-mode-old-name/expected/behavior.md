# Expected behavior — a `bookkeeping.md` still carrying `Create-mode`

The seed is an onboarded target whose `bookkeeping.md` was written before the field was renamed:
`**Create-mode:** autonomous`, and no `Ticket-create-mode` at all. Confirms the compatibility rule of the
rename (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`, the `MR-create-mode` row). Not
deterministically checkable; run via `fixtures/harness/run.sh agent-loop php-mr-create-mode-old-name`, local-only
and advisory.

## Expected: `/continuous-refactoring`

1. No onboarding, and **no question about either mode**: the old name is read as `MR-create-mode: autonomous`,
   and the missing `Ticket-create-mode` means `autonomous` — the pass behaves exactly as it did before the
   rename, tickets are created and the merge request is opened without asking.
2. The next write `refactor-learn` makes to `bookkeeping.md` (its bookkeeping merge request) renames the field to
   `MR-create-mode`, value unchanged. It does not add a `Ticket-create-mode` line — absent needs no write.

## Verified

Not yet run live.
