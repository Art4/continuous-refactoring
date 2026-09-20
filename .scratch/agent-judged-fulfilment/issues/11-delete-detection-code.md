# 11: Delete the detection code

Spec: `agent-judged-fulfilment`.

**What to build:** The contract step of the expand–contract sequence. With no caller left, the parser's detection functions and their helper predicates, the default that ran detection when no seed was given, and the tests that exercised them are removed. What remains is the graph logic, the PHP-floor precheck and version-reversal findings, and the outlook view. Documentation that still describes the parser as a detector is corrected, and the earlier decision that shipped the parser with detection is marked as replaced by the new ADR.

**Blocked by:** 10 (Drift check and a detection-free test suite).

**Status:** ready-for-agent

- [ ] Every detection function and helper predicate is removed, along with the tests that only exercised them; shared helpers used by the PHP-floor logic stay.
- [ ] The script no longer runs detection when no seed is given: scan passes require the seed, other passes derive state from the bookkeeping.
- [ ] No skill, reference, harness script or documentation still refers to a removed function, output field or detection behavior.
- [ ] The earlier decision record is marked as replaced by the new ADR and the new ADR reads consistently with the final state.
- [ ] The full deterministic test suite and the static validation tiers pass in CI.
