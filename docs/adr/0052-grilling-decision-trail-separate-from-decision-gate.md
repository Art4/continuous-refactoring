# Grilling decisions get a visible trail, kept separate from the decision gate

`/grilling` rounds that settle live, with a human present, previously left no trace on the candidate
issue — only the final plan (`refactor-design` step 5) survived; the reasoning behind a consequential
choice, even one meeting the ADR bar, was gone the moment the conversation ended unless it happened to
also trip the decision gate (`decision-gate.md`), which only fires for *unattended* passes and exists
to block, not to document. A later reader of the issue had no way to tell "we considered X and chose Y
because Z" from "nobody thought about X at all". Settled via a `/grill-with-docs` session
(`.scratch/refactor-learn-precondition/issues/01-refactor-learn-precondition-and-design-trail.md`).

## Considered Options

- **Fold this into the decision gate itself** — one mechanism, triggered by the same ADR-bar test,
  covering both the blocking (unattended) and non-blocking (attended) cases. Rejected: the decision
  gate is a control-flow mechanism (it can halt `refactor-implement` from running this pass); this is
  a documentation mechanism (it never blocks anything — the answer already exists, reached live).
  Merging them would make the decision gate's blocking behaviour depend on session attendance in a way
  that's harder to read at the call site than two small, single-purpose mechanisms.
- **Post every grilling question**, not just ADR-bar ones. Rejected — most rounds settle mechanical
  detail (naming, file layout) nobody will later wonder about; posting all of it turns the issue into
  a transcript, working against the same "plain, relevant facts" audience rule
  (`forge-facing-writing.md`) the rest of the suite already holds itself to.
- **Post as the questions are asked, before an answer exists** (live-streaming the interview onto the
  issue). Rejected — an unanswered question made visible on a public issue invites third-party
  comments on something still being actively negotiated with the human in the same conversation.
- **Fold the record into the same comment as the plan** (step 5), as a leading section. Rejected —
  keeps the plan comment a pure specification; a reader wanting "what was decided and why" and a
  reader wanting "what to build" are usually two different reads, and combining them means every future
  plan template carries an optional section that's absent most of the time.

## Decision

`refactor-design`'s grilling step (`structural-candidate.md` step 4 — structural and
externally-labeled candidates only; PHPStan baseline-shrink planning has no `/grilling` round to draw
from) gains a new **Decision trail**: once grilling's frontier is empty, for every question that met
the same three-factor ADR bar the decision gate already uses (hard to reverse, surprising without
context, a real trade-off) — regardless of whether it was ultimately resolved live or deferred to the
decision gate — post one bundled issue comment naming the question and the answer reached, before
step 5 writes the plan. Zero qualifying questions this session → no comment at all.

This is deliberately independent of the decision gate: the gate still applies exactly as before
(`decision-gate.md`, unchanged), for the narrower unattended/breaking-change cases where a live answer
isn't available and progress genuinely needs to pause. The trail applies alongside it, to the (large)
majority of sessions where a human is present, questions get answered on the spot, and nothing was
ever going to block — but the reasoning is still worth keeping.

## Consequences

- `structural-candidate.md` step 4 gains the Decision trail instruction, posted as its own comment
  distinct from the plan comment `refactor-design` step 5 writes, and distinct from a decision-gate
  flagged-question comment (which still uses its own existing shape: proposed default, explicit open
  question, `ready-for-agent` withheld).
- `refactor-design/SKILL.md` and `structural-candidate.md` both gain a one-line pointer clarifying the
  Decision trail and the decision gate are separate, so a future reader doesn't try to merge them.
- `CONTEXT.md` gains a **Decision trail** entry, distinguished from both **Plan** and **Flagged
  candidate**.
- Every Decision trail comment follows `forge-facing-writing.md` like any other forge-facing text —
  no suite-internal jargon or file citations.
