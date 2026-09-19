# 06: A Track scan fills `Open`; `refactor-learn` maintains it

Spec: `agent-judged-fulfilment`.

**What to build:** A scan of a Safety Net or Guardrails Track evaluates every node of the Track's scope by agent judgement (all Fulfilment checks, including the gate nodes), hands that fulfilled set to the script, and records every unresolved node of the scope into the Track's `Open` in the script's order, blocked nodes included. A completed scan still records `Last scan`, even when everything is already resolved. Afterwards `Open` is kept up to date: a merged candidate leaves `Open`; a rejection leaves `Open`, writes the recorded rejection and the `Out-of-scope` pointer as today, and every node closed by the rejected ancestor (as reported by the script) also leaves `Open`, with no new files. Reversing a rejection makes the next scan bring those nodes back. The manual fallback follows the same steps by hand.

**Blocked by:** 02 (Prose audit — Safety Net nodes), 03 (Prose audit — Guardrails nodes and gates), 04 (`Open` as the complete backlog), 05 (Script reduced to graph logic).

**Status:** ready-for-agent

- [ ] A scan of a Track writes `Open` containing every unresolved scope node in the script's order (blocked ones included), leaves `Out-of-scope` as recorded, and writes `Last scan`.
- [ ] A scan that finds every scope node resolved writes `Last scan` and an empty `Open`.
- [ ] Merge of a Track candidate removes its entry from `Open`.
- [ ] Rejection removes the entry, writes the recorded rejection and the `Out-of-scope` pointer, and removes every node closed by that rejection without writing further files.
- [ ] After a rejection is reversed, the next scan re-adds the reopened nodes to `Open`.
- [ ] Bookkeeping in the old shape or with an old-meaning `Open` is not migrated and does not cause an error; a Track override forces an immediate scan that corrects it.
- [ ] Advisory agent fixtures cover: populating `Open` with blocked nodes in order, the rejection cascade and its reversal, and old-shape pass-through. The manual fallback's prose describes the same steps.
