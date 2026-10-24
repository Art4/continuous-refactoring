# 04 — The BC promise

Type: task
Status: done
Blocked by: —

**What to build** (ADR-0088)

- **The operation.** `refactoring-operations.md`: optional **BC promise** — the path of the project's document, or `none`.
  Unlike the other optional operations, its absence means *not settled yet*, not a missing capability.
- **Settling it.** `onboarding-setup-interview.md`: search `AGENTS.md`, `CONTRIBUTING`, `README`, `docs/`, `UPGRADE*` for a
  documented promise and propose a path or `none`. The onboarding step of a run completes the bullet on a target
  onboarded before, as one decision point. Autonomous: write a path found unambiguously; never write `none`; until settled,
  act as if a promise exists.
- **`principles.md`.** *Strangler Fig* applies to code the promise covers (what it covers is the document's call);
  *Migrate callers, then delete* only to code it does not cover; replace "when in doubt, treat it as depended on" with the
  rule above plus the unsettled case. The suite may hard-deprecate by the promise's own procedure, upgrade note
  included; removal is always an ordinary ticket, never under the refactor label.
- `CONTEXT.md`: new term after **Breaking change**:

  > **BC promise**: A project's documented commitment to code outside its repository — the users of a package, the
  > addons of an application — about which parts of its code stay stable and by which path a **Breaking change** to them
  > is allowed: a new major version under SemVer, or a deprecation period counted in time and releases (Friendica:
  > `@deprecated`, then a triggered deprecation notice, then removal no sooner than five months and one release later).
  > The promise is the project's own document; the suite reads it and models no variant of its own. A project without
  > one has no BC promise. A Breaking change the promise allows is still a Breaking change: never shipped under the
  > refactor label.
  > _Avoid_: library (an application with addons can have one, a package may have none), public API (the promise, not
  > the visibility keyword, decides what is covered)

  **Refactoring operations**: add "**BC promise** (where the project's **BC promise** is written down, or `none`)" and
  "— except **BC promise**, whose absence means the question is not settled yet".
- Docs: `docs/FAQ.md` (what the suite does with a BC promise, and why it asks), `docs/playbooks/run.md` (the onboarding
  question), `docs/known-limitations.md` (an autonomous target without a clear document stays careful until asked).

**Done when** an onboarding on a fixture with a promise document proposes its path, one without proposes `none`, and
tests and validator are green.

## Comments

> **2026-10-24:** Done. *Finding the BC promise* and *The BC promise alone* live in `onboarding-setup-interview.md`; `SKILL.md` step 1 calls the latter for a complete section without the bullet and the run goes on. Interactive recommends `none` when nothing was found; autonomous never writes it.
