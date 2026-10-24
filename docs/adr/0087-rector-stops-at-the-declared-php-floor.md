# Rector stops at the declared PHP floor

> Supersedes [ADR-0041](0041-php-minimal-version-only-corrects-never-raises.md): `php-minimal-version` and the Role
> Runtime Floor go.

ADR-0041 kept `php-minimal-version` as a *Floor correction*: once `rector-php-set` had rewritten the code for a newer PHP,
declaring that PHP in `require.php` was "telling the truth". But the rewrite is what moved the truth. A Rector PHP set
above the declared floor makes the code need a newer PHP than the project promises — on a package, every user on the
older PHP breaks on the next release. The Stage legitimised a **Floor raise** after the fact, under the refactor label.
Its own Housekeeping line ("update the declared version if a newer release exists") was a raise outright.

## Decision

- **`rector-php-set` targets the declared floor and no higher** — Rector's `withPhpSets()` without an argument, which
  reads `composer.json`, or the level that equals it. The Stage is fulfilled when the applied level equals the floor and
  no rule finding is left.
- **A floor a human raises later** makes the Stage unfulfilled again; Housekeeping's re-check of the tooling Tracks finds
  it and offers a ticket for the next level.
- **Code that already needs more than the declared floor**, before the suite came, gets no Stage. Whoever notices it
  proposes an ordinary ticket: raising the floor or lowering the code is a product decision.
- **`php-minimal-version`, the Role Runtime Floor and the term Floor correction go.** A Floor raise covers both ways of
  committing a project to a newer PHP: raising `require.php`, and rewriting the code above it.

## Considered Options

- **Keep the correction, drop only the Housekeeping line.** Still writes the raise into `composer.json` after Rector made
  it. Rejected.
- **Keep the Stage for the case where the code already needs more.** Its check compares against Rector's level only and
  never saw that case. Rejected; an ordinary ticket fits a product decision better than a Stage.

## Consequences

- A rejection of `php-minimal-version` on record names a Stage that no longer exists and is ignored.
- The PHP Pack loses one Stage and one Role; the Rector prose, the generated pages and `CONTEXT.md` change with it.
