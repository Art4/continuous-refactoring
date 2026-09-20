- A selected node-based Track is now worked one `Open` node per pass, top to bottom
  (`skills/refactor-scan/references/track-open-processing.md`): the topmost workable node is picked up,
  its Fulfilment check is re-run right before its issue is created — a node fulfilled by hand since the
  scan leaves `Open` with no merge request and the pass moves on — and non-workable nodes are collected
  with a reason for the pass report. Track nodes are no longer pre-filed as issues at proposal time
  (amending ADR-0047's pre-filing decision for them): the issue is created only when the node is
  actually worked, and Rank mode no longer chooses among Track nodes. Three new advisory agent fixtures
  cover the pick-up re-check (`php-track-open-hand-adopted`), the top-to-bottom order with a blocked
  node in between (`php-track-open-blocked-in-between`), and a priority-labeled issue waiting behind the
  top of `Open` (`php-track-open-priority-vs-top`).
