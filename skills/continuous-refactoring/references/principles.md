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

## A merge request a person can review

**Applies when** planning a tooling or baseline ticket, or any plan whose branch will touch many files.

A reviewer reads every file, or can check that every file follows a pattern they have understood. What
keeps a merge request reviewable is its kinds of change, not only its size: a tool run that rewrites many
files the same way is reviewable at a large count, the same count of different changes is not. Estimate
the size first (the tool's dry run, a count of the files) and ask: can the reviewer say, for each commit,
what to look for? Where not, cut the work into parts at a seam of kind or risk: rules that only restate
the code apart from rules that change what it does (stricter tests, cases the plan had to skip); a rule
that touches a large part of the code on its own; the switch to the tool's prepared set together with the
configuration, last. Each part leaves the branch green and is worth merging without the others. The
plan's *This merge request* names the part, what stays, and in one sentence why the cut is there. Work the
goal of the ticket does not need is proposed as a ticket of its own, through the usual finding at the
design point, and does not ride along. A Stage's
**MR scope** is the most one merge request holds, never the least.

*Fails when* the parts are so small that a reviewer has to hold several to understand one, or a cut is made
by file count alone, one merge request per rule.

## Strangler Fig

**Applies when** old and new have to live side by side: the target's **BC promise** covers the old API
(`refactoring-operations.md`, **BC promise**; what it covers is the promise's own call, `@internal` code is
often left out), or the migration is too wide to replace in one reviewable step. While the target's
**BC promise** bullet is missing, the question is not settled: treat whatever code outside the repository
could reach as covered.

Replace the old piece by piece, old and new working side by side until the swap is complete — never a
big-bang rewrite. Under a promise the old path is deprecated the way the promise says — the marker, and
the triggered notice and upgrade note where its procedure has reached that step — and never deleted in
the same wave. Its removal is a **Breaking change** the promise may allow, but never one for the refactor
label: it is proposed as an ordinary ticket for the human.

*Fails when* a rewrite lands in one merge request nobody can review.

## Migrate callers, then delete

**Applies when** a new internal API replaces an old one, every caller of the old one is in this
repository, and the target's **BC promise** does not cover it, or says `none`. The plan records that call under `Decisions`.

Move every caller to the new API and delete the old one in the same wave: no shim, no parallel old and
new path. Tests that only protected the old implementation go with it; the pin at the seam stays.

*Fails when* the "internal" API was in fact covered by the promise: deleting it breaks a user of the
package or an addon of the application, which no refactoring may do.

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
