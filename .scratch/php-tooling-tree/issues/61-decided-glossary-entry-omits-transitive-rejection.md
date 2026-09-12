# 61 — `CONTEXT.md`'s `Recommended edge`/`decided` glossary entry omits transitive rejection, so a reading agent distrusts correct `tooling_tree.py` output as a regression

**What to build:** `CONTEXT.md`'s `Recommended edge` entry defines *decided* as "fulfilled, or rejected"
with no further qualification. `_is_decided()`/`_undecided_recommended_parents()` in `tooling_tree.py`
have always (predating ticket 53, and ticket 60) counted a recommended parent as decided-rejected not
only when it carries its own `out-of-scope/` entry, but also **transitively**, when one of *its own*
required ancestors is itself rejected — exactly the rule [ADR-0016](../../../docs/adr/0016-recommended-edges-gate-until-decided.md)
already states in its own **Decision** section ("A parent counts as rejected either directly ... or
transitively, when one of *its* required ancestors is itself decided-rejected"). That clause never made
it into `CONTEXT.md`'s glossary entry — the one document every skill actually points readers at for
this term (ADRs are maintainer-facing paper trail only, never cited by number from a skill). A
live-running orchestrator that reads only `CONTEXT.md` + `php-tooling-tree.md` therefore has no way to
know the transitive rule exists, and — correctly, per the *incomplete* text it can actually see —
concludes the script's own output "contradicts its own spec."

**Why:** Live finding right after [ticket 60](60-diamond-dependency-shared-seen-set-false-negative.md)
merged (`continuous-refactoring.de`, `composer` rejected as out of scope). Ticket 60 fixed a real bug
that had been *masking* this gap: before the fix, the diamond bug made
`rector-dead-code`/`rector-code-quality`/`phpstan-level-3` all wrongly read as *neither* fulfilled nor
rejected, so `rector-type-coverage` correctly stayed `withheld` — for the wrong reason. After the fix,
those three now correctly resolve to effectively-rejected (cascading from `composer`), so
`rector-type-coverage` correctly moves to `next` — but the maintainer running `continuous-refactoring`
directly read `rector-type-coverage`'s own node entry (`php-tooling-tree/rector.md`) plus `CONTEXT.md`'s
glossary, saw none of the four recommended parents carrying their own `out-of-scope/` entry, and (per
the letter of what's actually written) correctly flagged this as "the shared script's withhold
computation looks regressed" — closing report:

> `tooling_tree.py`'s fresh run put Rector: Type Coverage Set in `next` with `withheld` empty, but its
> own tree-doc entry explicitly gates it on four recommended parents ... all being *decided* first —
> none of the four are (all simply unfulfilled, none rejected)

The script was right; the glossary it was checked against was incomplete. Same shape of gap ticket 53
already closed for `resolved`-gate leaves' own documentation — never propagated to the `decided`/
`Recommended edge` glossary entry `_is_decided()` has silently relied on all along.

**Blocked by:** none. Documentation-only fix, no code change (`_is_decided()`/
`_undecided_recommended_parents()` already implement the rule correctly and are covered by ticket 60's
own new tests, indirectly — see Comments).

**Priority:** high — a maintainer or watched agent running the loop directly against a target with any
rejected node now has no documented way to trust `next`/`withheld` for anything downstream, and will
keep declining to act "since the shared script looks regressed," exactly the failure just observed.

**Status:** done — PR pending

- [x] `CONTEXT.md`'s `Recommended edge` entry states the transitive-rejection clause inline, in the same
  words/spirit as ADR-0016's own Decision section — a recommended parent counts as decided-rejected
  either directly (its own `out-of-scope/` entry) or transitively (one of its own required ancestors is
  itself rejected, the same closure a required edge already causes for proposability).
- [x] `php-tooling-tree.md`'s `Nodes` preamble (the "a rejection of a required parent closes every node
  beneath it" sentence) gets one added clause connecting the two ideas explicitly: a node closed this
  way also counts as *decided* (rejected) wherever another node reads it as a `recommended` parent —
  pointing at `CONTEXT.md`'s `Recommended edge` entry rather than restating it.
- [x] No code change — confirm via a fresh read that `_is_decided()`/`_undecided_recommended_parents()`
  already implement exactly the rule being documented (they do, per ticket 60's investigation).
- [x] `python3 -m unittest discover -s scripts -p 'test_*.py'` and `python3 scripts/validate_skills.py`
  stay green (pure prose change, no behavior to test beyond the existing suite).

## Comments

> **2026-09-12:** Filed immediately after ticket 60 merged, from a live `continuous-refactoring`
> closing report on `continuous-refactoring.de` that flagged the (correct) post-ticket-60 script output
> as a suspected regression, based on a documented `decided` definition that has been incomplete since
> ADR-0016 itself, predating both ticket 53 and ticket 60.

> **2026-09-12 (later):** Implemented on branch `tickets/61-decided-glossary-transitive-rejection`,
> branched off `main` (not stacked on ticket 60's still-open PR, per ADR-0049). Two one-sentence
> additions (`CONTEXT.md`, `php-tooling-tree.md`'s `Nodes` preamble), no code change. 307/307 tests
> green, validator unchanged (same 5 pre-existing advisories). Confirmed the underlying code needed no
> change: `_is_decided()` already treats a transitively-rejected recommended parent as decided,
> independent of ticket 60's diamond fix (verified directly on `main`, pre-ticket-60, using a linear
> chain — `phpstan-level-3` behind rejected `composer` already resolved correctly there; only the
> *diamond*-shaped parents ticket 60 touches were ever wrong).
