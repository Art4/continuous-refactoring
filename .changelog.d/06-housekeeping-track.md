- The standalone `continuous-housekeeping` skill is retired. Its process — due-check, reconciliation
  against fulfilled nodes, checklist assembly from `housekeeping-template.md`, quality gate, deliver —
  is unchanged, but now runs as the **Housekeeping Track**'s own content
  (`skills/continuous-refactoring/references/housekeeping-track.md`), triggered by the shared Track
  scheduler (`skills/continuous-refactoring/references/track-scheduler.md`) instead of its own standalone
  due-check. `bookkeeping.md` gains a `## Housekeeping` section (`Cadence`, `Last scan` only — no
  `Open`/`Out-of-scope`; swept content stays in `housekeeping-template.md`, unchanged) — a hybrid of
  Investigation's shape and Safety Net's/Guardrails' own: `Cadence` defaults to `7` (days, unchanged from
  today's default) and is hand-editable, unlike Investigation's permanent `continuous`, but there's no
  in-flight `Open` list, unlike Safety Net/Guardrails. Manual invocation of the Housekeeping Track
  directly stays possible, generalized to the same Track-name-as-argument pattern Safety Net, Guardrails,
  and Investigation already use — one shared invocation surface across all four Tracks now, replacing the
  old skill's own separate `/continuous-housekeeping` entry point. No standalone `continuous-housekeeping`
  skill remains; its `references/` (cadence interview, `housekeeping-template.md`'s own format doc) moved
  under `continuous-refactoring`.
