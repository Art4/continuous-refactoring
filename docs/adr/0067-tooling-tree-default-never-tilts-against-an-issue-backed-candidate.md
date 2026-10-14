# The tooling-tree default ranking bias never tilts against an issue-backed candidate

> Superseded by [ADR-0073](0073-a-run-is-a-chain-of-decision-points.md): there is no Rank mode and no
> ranking of a tooling-tree node against a ticket. The Track is chosen first, in a fixed order; within
> Investigation the order follows the signals.

> Narrows [ADR-0055](0055-purpose-based-fulfilment-and-scheduled-tracks.md)'s Investigation Track:
> `structural-scan` (and a PHPStan baseline-shrink family) keep their own unchanged Fulfilment gates,
> but no longer inherit the ordinary tooling-tree node's ranking preference once ranked alongside an
> issue-backed candidate.

Observed live in `Art4/legacy-todo`: issue #268 (a real, already-filed structural candidate) lost
`refactor-prioritize`'s Rank mode three passes in a row against `structural-scan` — the Investigation
Track's own gate — each time with the same shape of reasoning: *"a proposable tooling-tree node is
the strong default recommendation"* (`refactor-prioritize/SKILL.md` step 3, quoted near-verbatim by
the ranking subagent's own recommendation each time), plus *"compounding leverage that a single
already-known candidate doesn't have."*

**First pass at a fix, corrected before merge.** The obvious-looking fix is to except `structural-scan`
by name, on the theory that it alone never resolves for good the way an ordinary tooling-tree node
does. That's too narrow, for two reasons surfaced while drafting this ADR:

- **The bias never does any discriminating work outside Investigation's own ranking anyway.** Track-
  scoped candidate intake (ADR-0065) means a Safety Net or Guardrails pass's ranking pool, on the rare
  occasion `refactor-prioritize` even ranks one (several nodes newly unblocked by the same scan;
  otherwise `Open`'s own top-to-bottom walk handles it, no ranking involved), is *always* made
  entirely of tooling-tree proposals — every one of them already satisfies "a proposable tooling-tree
  node," so the bias can't crown a winner among them; something else (the tree's own order, the four
  real factors) already has to. The only place a tooling-tree-shaped proposal and an issue-backed one
  are ever ranked side by side, today, is inside an Investigation pass. Naming `structural-scan`
  specifically describes *where* the defect happened to surface, not *what* actually causes it.
- **A PHPStan baseline-shrink gate has the identical exposure**, and ADR-0065 already places it in the
  same pool as a structural or externally-labeled candidate — *"every non-tooling-tree candidate —
  structural, PHPStan baseline-shrink, and externally-labeled — is now picked up only in an
  Investigation pass."* A baseline-shrink gate does eventually resolve (an empty baseline), unlike
  `structural-scan`, but "eventually" can span many passes while its baseline stays non-empty — for
  that whole stretch it would out-rank an issue-backed candidate by the exact same unexpiring "just
  proposable" reasoning, invisibly, since nothing about the original fix touched it.

The actual defect is simpler than either node's own lifecycle: **the default only ever makes sense
when every candidate in the pool is itself a tooling-tree proposal** (comparing tooling adoption
against more tooling adoption — "get the deterministic checks in place" genuinely does compound
faster than any other order there). The moment an issue-backed candidate joins the pool, "prefer the
tooling-tree one" stops being a comparison between two similar things and starts being a standing
excuse to never work the backlog — regardless of which specific gate is doing the crowding-out, and
regardless of whether that gate happens to terminate someday.

## Decision

**The tooling-tree default recommendation (`refactor-prioritize/SKILL.md` step 3) applies only to a
ranking pool made entirely of tooling-tree proposals.** The moment the pool also holds an issue-backed
candidate (step 3b: structural, PHPStan baseline-shrink, or externally-labeled), no default applies to
anyone in it — every proposal, gate-shaped or not, is ranked purely on the same four factors (Heat,
Leverage, Tooling pressure, Risk). A gate can still win — a genuinely hot, high-leverage,
tooling-flagged, low-risk fresh finding is a fair winner over a stale, low-leverage, already-known
issue — but on those merits, never on being tooling-tree-shaped or on having "just" become proposable.
Leverage, applied to a gate itself, is judged on what's already concretely known to deepen (a named
hot spot, an existing candidate's own module) — never on a future scan's own open-ended promise of
finding something better later.

No change to any node's own Fulfilment/gating mechanics, to Track scheduling, or to Select mode's own
exploration once a gate does win.

## Considered Options

- **Except `structural-scan` by name** (this ADR's own first draft). Rejected once the baseline-shrink
  exposure surfaced — it fixes the one incident observed, not the actual shared cause, and would need
  re-discovering and re-fixing the same way for baseline-shrink, and again for any future Investigation
  gate.
- **A cooldown: after N consecutive wins, force an issue-backed candidate through regardless of the
  four factors.** Rejected as the primary fix — it would paper over the actual defect (the reasoning
  itself doesn't degrade) with a counter that needs tuning and adds a new piece of state
  (`refactor-scan`/`refactor-learn` would need to track and persist a per-Track win streak) for a
  problem a correctly-scoped default already fixes without one.
- **Give issue-backed candidates an Age bonus after all**, narrowing the "no age here" exclusion
  instead of narrowing the tooling-tree default. Rejected — it treats the symptom (the candidate never
  accumulates any counterweight) rather than the cause (the counterweight it's up against never
  expires either); a candidate would need an ever-growing bonus to keep pace with a bias that itself
  never shrinks, a strange thing for "Age" to have to do. The chosen fix makes the comparison fair at
  its source instead.
- **Drop the default-recommendation bias entirely, for every pool.** Rejected — it does real, intended
  work for its actual case (several simultaneously-unblocked tooling-tree nodes with nothing else to
  break the tie); the defect is specific to a mixed pool, not to the mechanism itself.

## Consequences

- `skills/refactor-prioritize/SKILL.md` step 3's default-recommendation paragraph is rewritten around
  "pool composition" rather than naming `structural-scan`, so a future second Investigation-owned gate
  needs no matching update to also be covered.
- No README/docs sync needed — this ranking mechanism isn't described anywhere outside the skill
  itself.
