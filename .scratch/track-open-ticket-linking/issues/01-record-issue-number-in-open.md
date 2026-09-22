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

Consequence, observed live against a real target repo (`moodle-sync`): `## Safety Net`'s `Open` held 6
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

**Status:** needs-triage.

**Parked, not part of this ticket:** whether `refactor-scan`'s own `Open` walk should short-circuit
using a recorded number instead of re-deriving fulfilment/workability from scratch (a performance
follow-on) — this ticket only closes the write-side gap that makes the number available in the first
place.

## Comments

> **2026-09-22:** Filed after a live design-review conversation (German) cross-checking
> `docs/refactoring/merge-requests.md`'s continued necessity — confirmed still required for both this
> repo and `moodle-sync`, per ADR-0012's local-Markdown-tracker fallback (neither uses a native-label
> tracker) — and a concrete `moodle-sync` observation: a `refactor-scan` pass needed a subagent to scan
> all 6 `## Safety Net` `Open` entries because none carried a `(#<issue>)` link, even though one
> (`rector-php-set`) already had a filed, planned ticket (`#08`).
