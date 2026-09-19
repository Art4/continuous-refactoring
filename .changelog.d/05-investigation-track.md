- **Investigation** now has its own `bookkeeping.md` section (`## Investigation`, `Cadence`/`Last scan`
  only — no `Open`/`Out-of-scope`, a structural candidate's own state still lives on the issue tracker /
  `merge-requests.md` as before) and joins the Track scheduler's real competition
  (`skills/continuous-refactoring/references/track-scheduler.md`). Its `Cadence` is always the literal
  `continuous` — no fixed interval, always due, always eligible — which makes it the scheduler's
  permanent fallback: it only wins a pass the moment no other wired Track (Safety Net, Guardrails) is
  both due and eligible, consistent with the fixed tie-break order Safety Net > Guardrails > Housekeeping
  > Investigation. `structural-scan`'s own candidate-search behavior is unchanged — only *when* it gets
  proposed changes: gated behind Investigation Track selection (`skills/refactor-scan/references/
  investigation-track.md`) instead of proposed unconditionally every pass.
