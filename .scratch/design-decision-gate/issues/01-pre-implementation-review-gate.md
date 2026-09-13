# 1 — Pre-implementation review gate for ADR-shaped design decisions

**What to build:** Extend `refactor-design` so that when grounding/grilling a candidate (or an
equivalent fixed-spec check for a tooling-tree node / baseline-shrink group) surfaces a decision
meeting the `/domain-modeling` ADR criteria (hard to reverse, surprising without context, a real
trade-off) — but doesn't rise to a full breaking change — it still writes the plan as usual, with
its own proposed default, but also flags that specific decision as an open question in the issue
comment, and deliberately withholds the `ready-for-agent` label. `continuous-refactoring/SKILL.md`'s
orchestrator gains a check before step 5 (Implement): only continue to it this same pass when the
candidate is either unflagged, or flagged and already carrying `ready-for-agent` — a flagged,
still-unconfirmed candidate found again by a later pass is skipped, not treated as blocking; scan
looks for a different candidate instead, same as any other in-flight one.

Separately: if grounding/grilling instead discovers a genuine breaking change is required,
`refactor-design` decides nothing and writes nothing itself (respects the suite's existing "only
`refactor-learn` writes bookkeeping/labels/`out-of-scope`" rule) — it hands this forward as a new
kind of **Finding**, consumed by the closing `refactor-learn` call, which applies the
already-existing rejection machinery (closing comment + `wontfix` + `out-of-scope`/closing note),
same as a load-bearing MR-review rejection today.

**Why:** In every `Create-mode`, design and implementation already run unattended, back to back, in
the same pass today — a human is only ever consulted afterward (reviewing the plan or the finished
MR), regardless of how the MR itself gets opened. For a decision that's hard to reverse, or that
would actually require a breaking change, "correct me later" already happened too late — the code is
written. Asking first, as an ordinary issue comment, costs little and avoids shipping something that
needs to be unwound. Also closes a real gap found while grilling this: `docs/adr/0004`'s "no breaking
changes" ground rule is currently pure prose — no skill step anywhere operationalizes what actually
happens when this is discovered mid-design.

**Blocked by:** none.

**Priority:** medium.

**Status:** ready-for-agent

Settled via `/grill-with-docs` (`grilling` + `domain-modeling`, three rounds plus follow-ups):

- [x] **No new mode toggle.** The gate doesn't key off `Create-mode` (`autonomous`/`ask-each-time`/
  `human-opens`) — that field only governs how the *finished MR* gets opened, after implementation
  already happened. The gap this closes (design → implementation with nobody watching) exists
  identically in every `Create-mode`, so the new behavior applies unconditionally.
- [x] **Conditional, not universal.** Only a candidate `refactor-design` actually flagged gets the
  pass-gap + label requirement. An ordinary candidate keeps flowing straight through design →
  implement in the same pass, unchanged — a loop pass may still create several candidate issues, pick
  one, spec it, and implement+MR it in one go, same as today.
- [x] **Two separate cases, two separate mechanisms.**
  - ADR-shaped, non-breaking decision → plan is written with a proposed default (per the existing
    "decide first, human can push back" principle) **plus** an explicit open question in the issue
    comment; `ready-for-agent` stays absent until a human adds it.
  - Genuine breaking change → not `refactor-design`'s call to act on. Modeled as a new **Finding**
    origin (today Findings only ever come from `refactor-scan`; see Glossary below) handed to the
    closing `refactor-learn` call, which already owns issue-closing/labeling/`out-of-scope` writes.
    Deliberately *not* special-cased as a direct write from `refactor-design` — that would poke a hole
    in the suite's existing single-bookkeeping-writer rule for the sake of one case.
  - Applies to any design flow that can surface either case, not only structural/externally-labeled
    candidates that go through `/grilling` — e.g. a PHPStan baseline-shrink fix that turns out not to
    be behavior-preserving hits the breaking-change path the same way.
- [x] **A later pass encountering a flagged, still-unconfirmed candidate skips it** and looks for a
  different candidate to work this pass, rather than ending the pass early — consistent with the
  "conditional, not universal" decision above: a waiting candidate must not throttle the rest of the
  backlog.
- [x] **Label:** reuse the existing `ready-for-agent` triage label (`docs/agents/triage-labels.md`,
  "fully specified, ready for an AFK agent") rather than a new dedicated one — the meaning already
  fits, and keeping it generic lets some other mechanism besides this suite's own `refactor-implement`
  pick the candidate up once cleared.
- [x] **No ADR, no new glossary term yet** — deliberately deferred to actual implementation of this
  ticket, not written speculatively ahead of it.
- [x] **Glossary impact to make during implementation:** `CONTEXT.md`'s **Findings** entry currently
  reads "Scan only notices; it never decides the outcome itself" — implicitly scoping Findings to
  `refactor-scan`. This ticket adds a second origin (`refactor-design`, for the breaking-change case)
  and needs a wording update to match.

**Parked, not part of this ticket:** whether `refactor-learn` is better named/conceived as a
"bookkeeping" skill rather than a "learn" one — raised while discussing where the breaking-change
write should live, genuinely separate from this ticket's scope. Noted for later, not decided here.

## Comments

> **2026-09-13:** Filed after a `/grill-with-docs` session (German — `grilling` + `domain-modeling`).
> Started from a much narrower framing (post `/grilling`'s own questions into the issue) that the user
> corrected early on — the real ask is a pre-implementation review gate for ADR-shaped/breaking-change
> decisions, not a `/grilling`-transcript-posting mechanic. Covered: mode-toggle scope, universal vs.
> conditional gating, detection criteria (reusing the ADR three-factor test, splitting the breaking-
> change case out separately), what today's (nonexistent) breaking-change handling actually is, the
> Finding-based routing for that case respecting the single-bookkeeping-writer rule, label reuse, and
> deliberately deferring the ADR/glossary work to implementation time. User confirmed shared
> understanding ("Passt"). Ready to implement.
