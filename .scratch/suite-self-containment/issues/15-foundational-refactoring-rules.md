# 15 — Record the foundational refactoring rules & strategies

**What to build:** The suite's refactoring ground rules, written down so every pass and every MR follows them:

- **No breaking changes.** A refactor preserves observable behavior; behavior change is not a refactor — it routes to the normal feature/bug path. The loop never ships a breaking change under the refactor label.
- **Strangler Fig for wide migrations.** Large/legacy migrations replace the old piece by piece, keeping old and new working side by side until the swap is complete — never a big-bang rewrite.
- **Kent Beck's technique vocabulary.** The small, behavior-preserving transformations (extract method/class, move method, rename, introduce parameter object, replace conditional with polymorphism, …) are the standard moves; a plan decomposes into them.

The ruleset is written where the suite's skills can reference it and is binding in `refactor-design` and `refactor-implement`.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Written ruleset exists and is referenced by `refactor-design` and `refactor-implement`
- [ ] "No breaking changes" is binding — behavior-preserving is the definition of a refactor; behavior change routes to the normal feature/bug path
- [ ] Strangler Fig is documented as the strategy for wide/legacy migrations
- [ ] Kent Beck techniques are listed as the standard move vocabulary for plans