- The Housekeeping Track's reconciliation now sweeps via agent judgement
  (`skills/continuous-refactoring/references/housekeeping-track.md`): each cycle it checks only the
  nodes that carry a `Housekeeping` field, judges each one's Fulfilment check against its Purpose, and
  appends any missing checklist line — so a tool adopted by hand, Guardrails tools included, gets its
  line even when no delivering merge request ever existed. The `Fulfilled nodes` bookkeeping field is
  retired: no skill reads or writes it any more, and a `bookkeeping.md` that still carries the old field
  is left untouched and ignored. Covered by two new advisory agent fixtures:
  `php-housekeeping-hand-adopted-guardrails` and `php-housekeeping-old-schema`.
