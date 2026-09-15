Fixed a bug that could silently bypass the pre-implementation decision gate (ADR-0050): a
pre-existing `ready-for-agent` label on an externally-filed issue was never cleared when
`refactor-design` flagged a decision meeting the ADR bar, so `refactor-scan`'s resume checks read it
as already confirmed and routed straight to `refactor-implement` without a human ever seeing the
flagged question. `refactor-design` now actively manages both `ready-for-agent` and `needs-info` in
both directions for every candidate it plans (not only the three decision-gate-eligible types) —
adding `needs-info` and removing a stale `ready-for-agent` when flagging, and setting `ready-for-agent`
itself as the last step of an ordinary plan. `refactor-scan` reads both labels together, which also
fixes a related gap: a fully-designed tooling-tree-node issue (whose plan lives in the issue body, not
a comment) rediscovered outside the orchestrator's own same-pass hand-off is now recognized correctly
instead of looking like a fresh, undesigned candidate.
