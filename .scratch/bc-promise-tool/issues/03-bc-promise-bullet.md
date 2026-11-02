# 03 — The bullet: a URL, and several promises

Type: task
Status: done
Blocked by: 02

**What to build** (ADR-0093, spec Q8, Q16)

- **A URL.** `refactoring-operations.md`, **BC promise**: the target may name an `https://` URL in place of a path.
  `bc-promise.md`'s Fulfilment check counts it without fetching it. Where the suite reads the promise
  (`principles.md`, `rector.md`, Roave), an unreadable URL makes that run careful, with a finding. A promise found on
  a website gets the bullet with its URL, no draft. Versioned docs: the link to the current release line, and a
  Housekeeping line in the Tool file that keeps it current after a major release.
- **Several promises.** The bullet may list parts, each `<scope>: <path | URL>`. A scope is an area of the code (a
  path such as `packages/client/`) or a surface (PHP API, HTTP API, CLI, …). Overlapping scopes → the stricter
  promise applies. Code no part covers → the careful default. `none` alone holds only for the whole repository. The
  promise is that of the default branch's release line.
- **Readers.** `principles.md` applies the part that covers the code a plan changes. The bullet template in
  `refactoring-operations.md`, *Bullets the target chooses*, gets the list form.
- `CONTEXT.md`, **BC promise**: a project may have several, each with its scope.
- Docs: `docs/FAQ.md` (several APIs, versioned docs), `docs/known-limitations.md` (older maintained branches are not
  the suite's).
- Changelog fragment.

**Done when** walk-throughs hold: a list with an overlapping scope picks the stricter part; an unreadable URL makes
the run careful with a finding; and tests and validator are green.

## Comments

> **2026-11-02:** Done. The reading rules live once, in `refactoring-operations.md`, *Reading the BC promise*; the
> other readers point there. Played as walk-throughs: an overlap picks the stricter part (Strangler Fig), an unreadable
> URL leaves its part unsettled, named in the plan's `Decisions` and the closing report. Open for the human: a part
> whose document only narrows another ("follows the PHP API promise, except …") loses its exception under the
> stricter-part rule.
