# 01 — The recommended Roave invocation fails out of the box

Type: task
Status: open
Blocked by: —

**What was seen**

- `packs/php/roave-bc-check.md` names the GitHub Action `docker://nyholm/roave-bc-check-ga` as one way to fulfil
  the Stage. On a current GitHub runner its first run failed before any comparison:
  `fatal: detected dubious ownership in repository at '/github/workspace'`. The run fixed it with a step that sets
  `safe.directory` in the container's home.
- The comparison against the last tag then reported 32 breaks: one "was marked `@internal`" per class the BC promise
  leaves uncovered, marked after that tag. The Stage's MR scope says such breaks go into
  `.roave-backward-compatibility-check.xml` as commented `<ignored-regex>` entries. With the Action the entries did
  not take effect (two variants of the regex, the file passed explicitly). The run dropped the file and compared
  against a later commit with `--from=<sha>` instead.
- The Driver's review called the result mergeable and named `--from` only as a note for later, not as a departure
  from the ticket's and the Stage's MR scope.

**Open**

- Why the ignore file did not apply: an old tool version in the Action image, or a wrong path or format. Not
  verified.
- Whether the Pack should recommend another invocation, name the `safe.directory` step, or name `--from` as the
  allowed way for breaks that only marking `@internal` after the last release causes.
- Whether the review should hold the result against the Stage's MR scope, or the miss is a one-off.

## Comments
