# 01: Safety Net Track end-to-end — Purpose-based fulfilment, Open/Out-of-scope bookkeeping

**What to build:** A full Safety Net Track pass, end to end, on a real target repo. `refactor-scan`'s
tree-walk for Safety Net nodes judges each node's Fulfilment check against its own Purpose statement via
an agent, recognizing any real, working tool that serves it — not a hardcoded dependency-name list.
Concretely: a target already running Laravel Pint (no `friendsofphp/php-cs-fixer` dependency at all)
reads the `php-cs-fixer` node as fulfilled and never has it proposed. `bookkeeping.md` gains a
`Safety Net` section (`Cadence`, `Last scan`, `Open`, `Out-of-scope`), replacing the old
`Fulfilled nodes` cache and global `Pending candidates` field for this Track's own nodes.
`refactor-learn` writes into it: removes an entry from `Open` once its delivering MR merges; on
rejection, removes it from `Open` and writes both the matching `out-of-scope/<slug>.md` (format
unchanged) and a pointer entry under `Out-of-scope`. For this ticket, the orchestrator runs the Safety
Net Track whenever its `Open` is empty and it has either never run or its cadence (default 90 days) has
elapsed — Safety Net is the only Track wired up here, so no cross-Track competition is needed yet (that
lands in ticket 04).

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] A target repo with Laravel Pint installed and configured, no PHP CS Fixer dependency anywhere, is
      recognized as fulfilling `php-cs-fixer`'s Purpose; it is never proposed as a candidate.
- [ ] `bookkeeping.md` gains a `Safety Net` section (`Cadence`, `Last scan`, `Open`, `Out-of-scope`); the
      old `Fulfilled nodes`/global `Pending candidates` fields are no longer written for Safety Net
      nodes.
- [ ] An `Open` item merged via its delivering MR is removed from `Open`.
- [ ] An `Open` item rejected (`wontfix`) is removed from `Open`, with both `out-of-scope/<slug>.md` and
      a pointer entry under `Out-of-scope` written.
- [ ] A repo whose Safety Net Track has no section yet is treated as "never run"; its first scan writes
      `Last scan` even when it finds nothing missing (both `Open` and `Out-of-scope` stay empty).
- [ ] A repo still carrying the old `bookkeeping.md` shape runs a normal pass without erroring on the
      unrecognized old fields.
- [ ] Required/Recommended/Required-any edge semantics and cascading closure on a rejected required
      parent behave exactly as they do today.
