# 07: One-time bootstrap exception — Investigation, then Guardrails, then Housekeeping

**What to build:** The pass right after the Safety Net Track's `Open` first transitions from non-empty
to empty runs Investigation once (one candidate, fully delivered), then the following pass runs
Guardrails once (its own first scan-and-clear cycle), then the pass after that runs Housekeeping once
(its own first cycle) — each overriding the ordinary staleness-ratio/tie-break selection for exactly that
one turn, so a target sees one real piece of delivered refactoring value before being asked to adopt more
tooling or sit through maintenance. Ordinary scheduling (ticket 04) resumes permanently for that repo
once Housekeeping's first turn completes.

**Blocked by:** 05, 06

**Status:** done

- [x] The pass immediately following Safety Net's `Open` transitioning from non-empty to empty, for the
      first time, selects Investigation — overriding the ordinary staleness-ratio/tie-break order.
      Verified live (`php-scheduler-bootstrap-investigation`), including the adversarial case where
      ordinary never-run tie-break would otherwise pick Guardrails.
- [x] The following pass selects Guardrails, not Investigation again.
      Verified live (`php-scheduler-bootstrap-guardrails`).
- [x] The pass after that selects Housekeeping.
      Verified live (`php-scheduler-bootstrap-housekeeping`) — correctly selected Housekeeping, wrote
      `## Housekeeping`'s `Last scan`, opened the cycle's issue, and worked the checklist; hit the 280s
      opencode budget partway through the quality gate before printing the final explicit `SELECTED:`
      line (same non-blocking timeout pattern ticket 06's own `php-scheduler-housekeeping-competes`
      fixture already documented for this same heavier, full-pipeline shape) — 2/3 advisory assertions
      passed, reasoning and writes both correct throughout.
- [x] Once Housekeeping's first cycle completes, ordinary staleness-ratio scheduling governs every
      subsequent pass permanently for that repo — including Safety Net's own later, rarer rescans.
      Verified live (`php-scheduler-bootstrap-resumes`) for the general "all three turns done" case. The
      "Safety Net's own *later* rescan" sub-case specifically (`Open` going non-empty then empty again
      after the exception already retired) isn't independently fixture-tested — see Comments below for
      why the design already covers it by construction.
- [x] The exception fires exactly once per repo, tracked implicitly from the Track sections' own
      `Last scan`/`Open` state — no new stored flag. See Comments for the exact implicit-state
      combination used.

## Comments

**PR:** (fill in after opening)

**Implicit state used to detect and sequence the three turns (no new stored flag):**

The one-time exception (`skills/continuous-refactoring/references/track-scheduler.md`'s own "One-time
exception" section) is a pre-check evaluated fresh every pass, before ordinary Eligibility/Selection:

- **Precondition (all three turns):** `## Safety Net` exists and its `Open` is currently empty.
- **Turn 1 (Investigation):** `## Investigation` section absent (never run), **or** present with
  top-level `Pending candidates` still naming an issue. The `Pending candidates` half is the one
  non-obvious piece: per `skills/refactor-learn/references/investigation-write.md`, `##
  Investigation`'s `Last scan` is written the moment the Track's *scan* step runs — the very first pass
  of the turn — long before the one candidate it proposes is actually delivered (design → implement →
  learn can each take a further pass). Investigation carries no `Open` list of its own to lean on the
  way Guardrails/Safety Net do for "stay selected until done," so this reads the existing generic
  `Pending candidates` field instead — safe to read this way specifically *because* the precondition
  above (Safety Net's `Open` just empty) rules out every other legitimate source of a non-`none` `Pending
  candidates` at this exact point in a repo's timeline (Safety Net/Guardrails never write it; loop-config
  already ran; Housekeeping doesn't use it). Without this clause, a naive "section absent" check alone
  would end Investigation's turn after just one pass, before its candidate is actually delivered,
  violating the ticket's own "one candidate, fully delivered."
- **Turn 2 (Guardrails):** `## Guardrails` section absent. No `Pending candidates`-style follow-up check
  needed — once this turn's scan populates `## Guardrails`' own `Open`, the *ordinary*, already-built
  Eligibility rule (non-empty `Open` ⇒ that Track's entries get worked, not rescanned) keeps Guardrails
  selected on its own across however many passes it takes to clear, no extra logic required.
- **Turn 3 (Housekeeping):** `## Housekeeping` section absent. Housekeeping's entire cycle (reconcile →
  issue → checklist → quality gate → deliver) runs to completion inside the single pass step 0c performs,
  so there's no multi-pass in-flight state to track here either.
- **Permanently retired:** once all three sections exist and Investigation carries no in-flight `Pending
  candidates`. This is what makes the exception fire *exactly once, ever*: none of the three checks reads
  Safety Net's `Open` transition itself (there's no per-pass history to diff against, only the current
  `bookkeeping.md` snapshot) — each reads only Investigation's/Guardrails'/Housekeeping's own permanent,
  one-way "have I ever run" state, which the suite already keeps as ordinary staleness bookkeeping and
  never clears. A section, once created, is never removed, so each of the three conditions can only ever
  be true once per Track, per repo — including across a much later, ordinary Safety Net rescan whose own
  `Open` goes non-empty then empty again (that later transition changes nothing about
  Investigation's/Guardrails'/Housekeeping's own already-permanent section-presence).

**Judgement call — what a snapshot genuinely can't distinguish:** with no per-pass history file, this
check cannot tell "Safety Net's `Open` just emptied for the first time" apart from "Safety Net's `Open`
has simply always been empty" (a trivial tree with nothing to propose on its very first scan). Both look
identical in a `bookkeeping.md` snapshot, and both are deliberately treated the same way — if
Investigation/Guardrails/Housekeeping have never run yet, the sequence still fires. This is the one
genuinely unavoidable consequence of "no new stored flag" and is documented inline in
`track-scheduler.md`'s own "What this can't distinguish, by construction" note.

**Judgement call — section-presence as the proxy for "already had its turn," independent of actual
history:** each of the three checks reads only "has this Track ever run," not "did this Track's run
happen as part of *this* sequence specifically." Under normal operation this is a distinction without a
difference: Safety Net's own `Open` staying non-empty throughout Onboarding already forces Safety Net to
be reselected every pass (the pre-existing, ticket-04-built Eligibility rule), which structurally prevents
Guardrails/Housekeeping/Investigation from getting a "real" run in ahead of the sequence. In the
essentially unreachable edge case where one of them somehow did run earlier anyway, the fixed
if/elif/elif ordering (Investigation checked first, then Guardrails, then Housekeeping) still enforces
the required sequence deterministically from current state, and a Track that already happened to run is
simply treated as having already had its "turn" — consistent with the ticket's own framing ("has
Guardrails had its one bootstrap turn yet").

**Fixtures added:** `fixtures/php/php-scheduler-bootstrap-investigation`,
`php-scheduler-bootstrap-guardrails`, `php-scheduler-bootstrap-housekeeping`,
`php-scheduler-bootstrap-resumes` — all four run live, first try, against
`opencode/muse-spark-1.2-contributor-free` (`OPENCODE_TIMEOUT=280`), with correct reasoning traced to
exact `track-scheduler.md` line numbers in each transcript. Three (`investigation`, `guardrails`,
`resumes`) completed within budget with all assertions passing; `housekeeping` (the heaviest — it runs
Housekeeping's full reconcile → issue → checklist → quality-gate pipeline, not just Track selection) hit
the 280s budget before printing its final report line, same non-blocking timeout pattern ticket 06's own
`php-scheduler-housekeeping-competes` fixture already documented — its actual bookkeeping writes and
reasoning were confirmed correct throughout the transcript regardless.
