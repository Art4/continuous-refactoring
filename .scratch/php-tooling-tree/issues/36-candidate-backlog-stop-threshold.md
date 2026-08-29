# 36 — `refactor-scan`'s "five or more open `refactor:candidate` issues" backlog-stop may be the wrong number

**What to build:** Investigate whether `refactor-scan/SKILL.md` step 1's precondition — "Five or more open `refactor:candidate` issues already? Stop, propose nothing new" — should instead match `refactor-prioritize/SKILL.md` step 1's own in-flight threshold of **two** ("in-flight suite merge requests... Two or more already open? Stop").

**Why:** `docs/refactoring/config.md`'s `Pending candidates` field is documented (`skills/continuous-refactoring/references/refactoring-config.md`) as holding "at most one entry ... the suite tracks exactly one thing in flight at a time." If that invariant genuinely holds end to end, more than one `refactor:candidate` issue piling up unactioned should already be a process violation the same way more than one open merge request is — in which case `refactor-scan`'s stop threshold floating at five (rather than something like two, mirroring `refactor-prioritize`'s own in-flight check) looks like a number chosen generously rather than derived from the invariant it's meant to protect. Raised during a `/grill-me` session on ticket 33 (recommended-edge gating) — unrelated to that ticket's actual subject, so spun out here rather than folded into its ADR.

**Blocked by:** none.

**Priority:** low

**Status:** needs-triage

- [ ] Confirm whether `refactor:candidate` issues can legitimately pile up past one under normal operation (e.g. an interrupted pass leaving an issue filed but never delivered, across more than one such interruption) — if so, five may be a deliberately generous allowance for exactly that, not an oversight.
- [ ] If no legitimate path produces more than one or two, lower the threshold to match and document why in `refactor-scan/SKILL.md` (or a short ADR, if the reasoning is non-obvious enough to need one).
- [ ] If five is intentional, add a one-line note in `refactor-scan/SKILL.md` saying so, so this doesn't get re-raised as a bug later.

## Comments

> **2026-08-29:** Filed from a `/grill-me` session on ticket 33 after the user noticed the numeric
> mismatch against `refactor-prioritize`'s own in-flight-MR threshold of two. Not investigated further in
> that session — kept as its own ticket per the user's explicit choice, since it's a different mechanism
> (bookkeeping-invariant backlog gate vs. tooling-tree edge-gating semantics) that happens to collide only
> in the number "five" ticket 33 was separately lifting for a different reason (the `next_candidates()`
> proposal cap).
