- The Track scheduler implements Safety Net blockade, Guardrails yield, and Housekeeping preemption
  (`skills/continuous-refactoring/references/track-scheduler.md`). While Safety Net `Open` is non-empty,
  Safety Net is selected and nothing else runs — even if no node is currently workable; what it waits on
  is reported. Guardrails with a workable `Open` node is selected ahead of Investigation; Guardrails with
  `Open` non-empty but nothing workable yields, its `Open` stays as it is, and the pass report lists
  every stalled node with its reason. Housekeeping preempts Guardrails for one pass when due
  (`overdue_ratio >= 1`), then Guardrails resumes afterwards. The one-time bootstrap exception advances
  past Guardrails' non-empty `Open` — it reads only whether each section *exists*, not whether its `Open`
  is empty. Four new advisory agent fixtures exercise these rules: `php-scheduler-safety-net-blockade`,
  `php-scheduler-guardrails-stalled`, `php-scheduler-housekeeping-preempts-guardrails`,
  `php-scheduler-bootstrap-guardrails-open`.
