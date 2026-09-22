# 1 — Fix: Track `Open` list never gets the filed issue number written back

**What to build:** `refactor-learn`'s early call gains a fourth write case in
`skills/refactor-learn/references/safety-net-write.md` and
`skills/refactor-learn/references/guardrails-write.md`, alongside the existing three (Merge,
Fulfilled at pick-up, Rejection): once `refactor-design` files the candidate issue for the one node
`refactor-scan`'s `Open` walk (`skills/refactor-scan/references/track-open-processing.md`) picked to
work this pass, that node's `Open` entry is rewritten from `- <slug>` to `- <slug> (#<issue>)` — the
format `guardrails-track.md`'s "Filling `Open`" section already documents as the target shape
(`- <slug> (#<issue>)`, "`- none` when empty"), but that no write rule currently produces once the
scan's initial bare-slug fill is done.

**Why:** `guardrails-track.md`/`safety-net-track.md` correctly state a node's slug is added to `Open`
bare, with no issue, when the scan first fills the backlog ("No candidate issue is created at this
point... not pre-filed during the scan") — no ticket exists yet for the nodes not being worked this
pass. But for the *one* node the walk does hand to `refactor-design`, a ticket now exists, and nothing
ever writes its number back into `Open`. Checked both write-side files
(`skills/refactor-learn/references/safety-net-write.md`,
`skills/refactor-learn/references/guardrails-write.md`) end to end — each defines exactly three write
cases for `Open` (Merge → remove, Fulfilled at pick-up → remove, Rejection → remove + `Out-of-scope`
pointer) plus a redundant "Fresh MR doesn't itself remove" note. None of them adds the number.

Consequence, observed live against a real target repo: `## Safety Net`'s `Open` held 6
bare slugs, none linked to a ticket. `refactor-scan`'s next walk had to re-derive, per entry, whether a
candidate issue already existed at all — required by workability check 2 ("the node's own candidate
issue, *if already filed*, does not carry `needs-info`",
`skills/refactor-scan/references/track-open-processing.md`) — by searching the ticket directory rather
than reading a link off the `Open` line itself. One of the 6 nodes had in fact just been filed and
planned (issue already existed, plan already written, `ready-for-agent`) — undiscoverable from
`bookkeeping.md` alone.

**Blocked by:** none.

**Priority:** medium — doesn't produce a wrong outcome (workability re-derivation still lands on the
right answer), but forces avoidable rediscovery work every pass an `Open` list has more than one entry,
and defeats the point of the `(#<issue>)` shape the docs already claim exists.

**Status:** done — PR #119.

**Parked, not part of this ticket:** whether `refactor-scan`'s own `Open` walk should short-circuit
using a recorded number instead of re-deriving fulfilment/workability from scratch (a performance
follow-on) — this ticket only closes the write-side gap that makes the number available in the first
place.

## Comments

> **2026-09-22:** Filed after a live design-review conversation (German) cross-checking
> `docs/refactoring/merge-requests.md`'s continued necessity — confirmed still required for both this
> repo and a real target repo checked live, per ADR-0012's local-Markdown-tracker fallback (neither
> uses a native-label tracker) — and a concrete observation there: a `refactor-scan` pass needed a
> subagent to scan
> all 6 `## Safety Net` `Open` entries because none carried a `(#<issue>)` link, even though one
> (`rector-php-set`) already had a filed, planned ticket (`#08`).

> **2026-09-22 (grilling):** Settled via `/grilling` (5 questions, one round each plus a
> confirmation): **Q1 — bundle in a second, independently found bug**:
> `refactor-design/SKILL.md` step 5 is entirely blind to the Safety Net/Guardrails split and sets
> `Pending candidates` for *every* freshly-filed non-native-tracker tooling-tree node, contradicting
> `safety-net-write.md`/`guardrails-write.md`'s "never touches `Pending candidates`" — and risking a
> double-resume (`refactor-scan/SKILL.md` step 2's own `Pending candidates` resume racing the Track's
> `Open`-based one) if a pass is interrupted before that field is cleared. Fixed together, same code
> path. **Q2/Q5 — where the write happens**: not `refactor-design` (would require it to learn about
> Tracks), not a `Pending candidates`-vs-`Open` reconciliation (reopens the double-resume risk) —
> `refactor-scan`'s `Open` walk hands its pick to `refactor-design` marked **self-tracking**, the same
> generic marker a structural/baseline-shrink candidate already carries; design skips
> `Pending candidates` without ever learning why. `refactor-learn`'s closing call, already
> Track-aware, performs the actual `(#<issue>)` write, authorized by a new fourth precondition case
> (the `Open` walk having picked a node this pass) — covers the observed case where `refactor-design`
> ran but `refactor-implement` hadn't yet opened a merge request this same pass. **Q3 — scope
> narrowed**: `refactor-design`'s existing title-based lookup (`Tooling tree: <Name>`) already
> prevents duplicate filing independent of any `Open` link — this ticket is a discoverability/
> bookkeeping-accuracy fix, not a correctness one. **Q4 — new ADR**: yes.

> **2026-09-22 (implement):** [ADR-0060](/docs/adr/0060-track-open-entries-record-their-issue-number.md)
> added (amends ADR-0051, ADR-0055). Changed: `refactor-design/SKILL.md` (widened the existing
> structural/baseline-shrink `Pending candidates`-skip into a generic "handed forward already marked
> self-tracking" case, no Track vocabulary added), `track-open-processing.md` (marks the hand-off
> self-tracking; documents its own `## Output` as the closing call's new trigger),
> `refactor-learn/SKILL.md` (fourth closing-call precondition case), `safety-net-write.md`/
> `guardrails-write.md` (new "Issue filed for the picked `Open` entry → record its number" section
> each; corrected the now-true "never touches `Pending candidates`" claim to explain *why* — design
> skips the write, not just that nothing removes it), `refactoring-bookkeeping.md` (`Pending
> candidates` field doc), `CONTEXT.md` (new **Self-tracking** entry), `docs/playbooks/tracks.md`
> (documents the annotation for human readers). New `.changelog.d/119-track-open-issue-linking.md`
> fragment.
