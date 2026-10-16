# Hard rules and principles live apart

> Partly supersedes [ADR-0004](0004-foundational-refactoring-rules.md): the Strangler Fig and the Kent Beck
> vocabulary are no longer among the binding rules.

ADR-0004 put five things under one heading, all binding. Two of them are judgement, not rules:
whether a migration is wide enough for a Strangler Fig, and which technique fits a slice, depend on the
code. Read as binding, they push a plan towards pieces and indirection even where one step would do, which
is the cost the new reader-load test is meant to catch.

The binding rules stay short and checkable: no breaking changes, deterministic tools over agents, an own
branch, and the pin. Everything that helps judgement lives in `principles.md`: each entry says when it
applies, what to weigh and how it fails. A plan names the principles that changed a decision; the review
reads them for the reader-load finding. A skill of the target gets the file as guidance, not as an
obligation.

## Consequences

- The Strangler Fig and the technique vocabulary keep their content and move; the validator's keyword
  check for ADR-0004 still finds them in the skill texts.
- A principle can be departed from with a stated reason. A rule cannot.
