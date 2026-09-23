# The retired `Fulfilled nodes` bookkeeping field is removed from the schema, not merely ignored

> Continues [ADR-0056](0056-agent-judged-fulfilment.md), which retired `Fulfilled nodes`: no skill
> reads or writes it. This ADR finishes the job — the field is no longer part of the documented
> schema, and no fixture, harness check or doc carries it.

ADR-0056 left the field in place as tolerated residue: the schema doc kept a retired-field section,
the fixtures carried it in ~24 `bookkeeping.md` files, and the harness asserted that old content
stayed "untouched". Every one of those was upkeep for a compatibility promise nobody needed — all
known targets are maintained by the suite's owner and can drop the block by hand.

Decision: delete the field from `refactoring-bookkeeping.md`, the fixtures and the harness. The parser
(`tooling_tree.py`) is deliberately unchanged in behaviour — it already ends every list at any
`**Field:**` line, so a leftover `**Fulfilled nodes:**` block in an old file is still skipped, without
the field being named anywhere. The `old-schema` fixtures stay, now covering the global `Pending
candidates` field and the absence of Track sections.
