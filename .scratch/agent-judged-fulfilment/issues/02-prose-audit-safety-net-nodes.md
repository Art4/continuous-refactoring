# 02: Prose audit — Safety Net nodes

Spec: `agent-judged-fulfilment`.

**What to build:** Before any detection code is removed, the Fulfilment-check prose of every Safety Net node must carry everything the parser's detection currently knows. For each node in the Safety Net scope (the generic root nodes and the PHP nodes up to and including the resolved leaves of the safety-net aggregation node), compare the parser's heuristics with the prose in the node's tree doc and move every rule the parser applies but the prose lacks into the prose. Typical candidates: tools installed only ephemerally in a CI job, verified autoloading and entry-point wiring, equivalence and co-presence rules between Psalm and PHPStan, config-file naming variants, Rector set naming. Rules found to be deliberately dropped are recorded with the reason. No runtime behavior changes; the parser is untouched.

**Blocked by:** 01 (Stop-conditions become recognition-only gate nodes) — the same tree docs are edited there.

**Status:** ready-for-agent

- [ ] Every Safety Net node's tree doc is audited; the ticket's Comments list each node as "prose extended" (with what was added) or "already covered".
- [ ] Every heuristic the parser applies to a Safety Net node is either stated in that node's prose or listed in Comments as intentionally dropped, with a reason.
- [ ] The evidence procedure the scan uses for autoloading and unwired entry points is described in prose well enough that an agent without the script can follow it.
- [ ] The manual tree-walk fallback can evaluate every Safety Net node from the prose alone, without reading parser code.
- [ ] The validation checks the repo already runs on skill and tree docs still pass.
