# The BC promise

The suite cannot tell a project with a promise to outside code from one without. `principles.md` judges it ad hoc
("when in doubt, treat it as depended on"), `rector-type-coverage` adds return types that break a subclass in another
repository, and Roave BackwardCompatibilityCheck, the tool that would catch such a break, has no place in the tree
because nothing says when it applies. "Library" is the wrong cut: Friendica is an application (`type: project`,
calendar tags) with a promise to its addons — Symfony-style, with `@internal`, `final` and extending non-abstract
classes excluded, and a deprecation path counted in time and releases (`@deprecated`, then a triggered notice, then
removal no sooner than five months and one release later). A SemVer package promises the same by major versions.

## Decision

**The BC promise is the project's own document.** The suite reads it and models no variant of its own. A Breaking change
the promise allows is still a Breaking change, never shipped under the refactor label.

**Where it is recorded.** An optional operation **BC promise** in `## Refactoring operations` names the document's path,
or `none`. Its absence means the question is not settled yet — unlike every other optional operation, whose absence
means the capability is missing.

**How it is settled.** The suite searches `AGENTS.md`, `CONTRIBUTING`, `README`, `docs/` and `UPGRADE*` files and proposes
a path or `none`: in the onboarding interview for a new target, and in the onboarding step of the next run for a target
onboarded before. An autonomous run writes a path it found unambiguously; it never writes a guessed `none`. Until the
question is settled it acts as if a promise exists and proposes no Roave Stage.

**What reads it.**

- `principles.md`: code the promise covers is reshaped by Strangler Fig only, the old path deprecated, never deleted in
  the same wave; *Migrate callers, then delete* holds only for code it does not cover. The suite may hard-deprecate
  by the promise's own procedure, an upgrade note included. Removal is an ordinary ticket.
- `rector-type-coverage` gets a second path, `rector-bc-library`, taken when the promise covers extending and overriding
  non-final classes and methods; otherwise Rector's own set, as for Friendica, whose promise excludes exactly that.
  The package's compatibility table is not copied; the Tool file points at its README.
- **Roave BC Check** joins the PHP Pack: Tool `roave-bc-check`, recommended, Role API Compatibility (no Signal), one
  Safety Net Stage that requires `composer` and waits for `ci-runner`. It applies when the promise follows SemVer and
  the repository has at least one SemVer tag. `rector-type-coverage` waits for it: the detector before the rewriter.

## Considered Options

- **Judge the promise on every run.** Five places read it, and a wrong judgement in `principles.md` or in the Rector
  path cannot be undone by a rejection. Rejected.
- **A term "BC library" recognised by `type: library` and a SemVer tag.** Misses Friendica and every application with
  extension points. Rejected.
- **A Housekeeping task that keeps deprecations moving** (hard-deprecate what is no longer used, propose removal past
  the window). Fits Friendica, means nothing to a SemVer package or a project without a promise. Rejected; it stays
  the target's own work.
- **Roave in Guardrails.** The break it catches comes from the suite's own structural work, so it has to stand before
  it. Rejected.

## Consequences

- An onboarded target is asked once, in its next run. An autonomous target without an unambiguous document stays
  careful until a human answers.
- A promise that is not SemVer gets no mechanical gate; Roave would report every removal the promise allows.
- New: the operation, the onboarding question, the Role and Tool, the second Rector path, the term in `CONTEXT.md`.
