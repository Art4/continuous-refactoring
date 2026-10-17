# Reference: principles

Aids to judgement, not rules. Where an entry's *Applies when* fits, weigh it; departing from it is fine
when the plan's `Decisions` or the review says why. What binds without exception is in
`foundational-refactoring-rules.md`.

## Reader load

**Applies when** judging whether a slice or a diff is worth keeping, shaping a plan, or reviewing.

Reader load is the work a reader has to do to follow the code. Part of it comes from the problem and stays;
a refactoring can lower only the rest. Two sources, independent of each other: the **layers** between a
question and its answer, and the **state** the reader has to hold in mind. A reader holds about four
things at once. The test: can someone new say where X comes from and what can change X, without chasing
through the code? A slice that lowers reader load nowhere is not kept, and a change that "might help
later" is not kept either. What lowers it: early returns instead of nested conditions, a named
intermediate for a complex condition, composition instead of a deep inheritance chain, one deep module
instead of many shallow ones, state kept in the narrowest scope.

*Fails when* a method is extracted because it was long and has one caller: the reader now jumps between
two places and learned nothing.

*Source:* Zakirullin, "Cognitive Load in Software Development" (https://minds.md/zakirullin/cognitive).

## Strangler Fig

**Applies when** old and new have to live side by side: something outside this repository depends on the
old API (a published library's public interface, a documented or marked-public contract), or the
migration is too wide to replace in one reviewable step. When in doubt whether something outside depends
on it, treat it as depended on.

Replace the old piece by piece, old and new working side by side until the swap is complete — never a
big-bang rewrite.

*Fails when* a rewrite lands in one merge request nobody can review.

## Migrate callers, then delete

**Applies when** a new internal API replaces an old one, every caller of the old one is in this
repository, and nothing outside depends on it. The plan records that call under `Decisions`.

Move every caller to the new API and delete the old one in the same wave: no shim, no parallel old and
new path. Tests that only protected the old implementation go with it; the pin at the seam stays.

*Fails when* the "internal" API was in fact someone else's contract: deleting it breaks a user of the
library, which no refactoring may do.

## Subtract before you add

**Applies when** a plan sequences a reshape, an addition or a rewrite.

Remove what is dead first — unused code, a wrapper with one caller, a validator nobody needs — then
reshape on the simpler base, then do the follow-up. After the pin, the commits run in that order.

*Fails when* a new layer is built around dead code that would have been cheaper to delete.

## Technique vocabulary

**Applies when** a plan is broken into slices.

The small, behavior-preserving transformations are the standard moves: extract method or class, move
method, rename, introduce parameter object, replace conditional with polymorphism, and the rest of
Kent Beck's list. A slice is one of them, or a few in a row.

*Fails when* a slice names no move and mixes a restructuring with a change of behaviour.
