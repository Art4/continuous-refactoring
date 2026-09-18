# 02: Guardrails Track

**What to build:** The same mechanism ticket 01 built for the Safety Net Track, applied to the
Guardrails node subset (the nodes gated on the Safety Net closing) — its own `Guardrails` section in
`bookkeeping.md` (`Cadence` default 60 days, `Last scan`, `Open`, `Out-of-scope`), scanned and written
back through the same agent-judged-Purpose and `refactor-learn` mechanics ticket 01 already established,
proving the approach generalizes to a second node set without new plumbing.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Guardrails nodes are recognized via agent judgement against their own Purpose statement, the same
      way Safety Net nodes are.
- [ ] `bookkeeping.md` gains a `Guardrails` section (`Cadence`, `Last scan`, `Open`, `Out-of-scope`),
      independent of the `Safety Net` section.
- [ ] Guardrails nodes are only ever proposed once the Safety Net has closed (existing gating semantics
      unchanged).
- [ ] Merge/rejection write-back for Guardrails behaves identically to the Safety Net Track's own —
      reusing ticket 01's mechanism, not a reimplementation.
