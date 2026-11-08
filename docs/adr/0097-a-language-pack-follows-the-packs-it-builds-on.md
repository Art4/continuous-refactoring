# A language Pack follows the Packs it builds on

> Amends [ADR-0079](0079-tooling-model-roles-tools-stages-in-packs.md): the Packs are ordered `generic` first, then by
> name, each after the Packs its `follows` names.

The order of the Packs sets the order of the Stages in a Track, and so which ticket a run files and works first. It
was `generic` first and the rest by name. With a `js` Pack beside `php`, a PHP application's Guardrails would take
ESLint before PHPStan's levels, because `js` sorts before `php`; the name decided what no one had chosen.

## Decision

- **`follows` in `pack.json`** lists Packs of the suite this Pack comes after. `js` and `twig-php` follow `php`.
- **It orders, nothing more.** No Stage waits for a Pack it follows, and a Pack that follows one that does not apply
  stands where the name order puts it: a site of JavaScript alone takes ESLint right after the generic Pack.
- **The parser refuses** a `follows` that names no Pack, and Packs whose `follows` form a cycle.
- A target's own Pack still comes last.

## Considered Options

- **`after`.** Rejected: it was the Stages' name for what is now `waits_for` (ADR-0086), and an old reading would
  come back with it.
- **`recommends`.** Rejected for the reason ADR-0086 gave: it collides with the status *recommended*, and reads as
  advice.
- **A fixed list of Pack names in the parser.** Rejected: a new Pack would have to change the parser.

## Consequences

- PHP applications take the PHP Guardrails first; their ESLint Stages follow, then Twig's.
- Between two Packs that follow the same one, the name still decides (`js` before `twig-php`).
