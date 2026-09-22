# Writing the `## Housekeeping` section

Part of `refactor-learn/SKILL.md`'s closing call — the only thing this section ever gets written, no
early-call handling exists for it at all (contrast `safety-net-write.md`/`guardrails-write.md`, which
both handle a Merge/Rejection finding during the early call too) — same shape as
`investigation-write.md`'s own single-call scope. Applies only to `## Housekeeping`'s own `Cadence`/
`Last scan` fields; the sweep's own checklist content, issue, and merge request/close mechanics are the
Housekeeping Track's own process, entirely unrelated to this section
(`skills/continuous-housekeeping/references/housekeeping-track.md`).

## `Last scan` — written whenever `housekeeping-track.md`'s own process actually ran this pass

`skills/continuous-housekeeping/references/housekeeping-track.md` ran this pass (Housekeeping was the
Track step 1 selected, and its own process was actually reached — whether it resumed an in-progress
cycle, opened and delivered a fresh one, or found nothing registered to check) → write `## Housekeeping`'s
`Last scan` to today's date (`YYYY-MM-DD`), last, in the closing call's own
step ordering, same position `## Safety Net`'s/`## Guardrails`'/`## Investigation`'s own `Last scan`
write already occupies. **Section didn't exist yet** (first-ever scan for this target) → create it here:
`Cadence: 7 days`, `Last scan: <today>` — the same default `housekeeping-track.md`'s own *First-run cadence*
section applies, written here rather than left for a later hand-edit. `Cadence` is otherwise never
written by this call once the section exists — see *`Cadence` is read, not written, past first creation*,
below.

**The Track didn't run this pass** — Housekeeping wasn't the Track step 1 selected — don't touch
`## Housekeeping` at all.

**Which branch**: land this write via the ordinary dedicated bookkeeping branch/MR
(`refactor-learn/SKILL.md`'s own "Which branch" rule), the same as `## Safety Net`'s/`## Guardrails`'/
`## Investigation`'s own `Last scan` writes in their ordinary case. Deliberately not folded onto the
Housekeeping Track's own cycle branch (`chore/housekeeping-<date>`) the way a candidate's own fold-in
exception rides that candidate's branch — `refactor-learn`'s existing fold-in exception is scoped
specifically to a native-tracker candidate MR `refactor-implement` opened this same pass
(`refactor-learn/SKILL.md`'s own "Exception" paragraph); Housekeeping's own branch is opened directly by
`housekeeping-track.md` itself, on any tracker, and there isn't always one to fold onto at all (the
"nothing registered to check" and "zero code changes, issue closed directly" outcomes both leave no
Housekeeping branch open by the time this call runs) — one uniform path avoids a second, narrower
special case for the cases that do have a branch.

## `Cadence` is read, not written, past first creation — same discipline as `## Safety Net`'s/`## Guardrails`' own

Unlike `## Investigation`'s always-literal `continuous`, `## Housekeeping`'s `Cadence` is a real interval
(`refactoring-bookkeeping.md`'s *Cadence values*) — `7 days` unless hand-edited, or set via
`skills/continuous-housekeeping/references/housekeeping-cadence-interview.md`'s own optional, human-run
interview (`housekeeping-track.md`'s *First-run cadence* section) — but this write only ever sets it once,
on first creation. Every later write to this section touches `Last scan` alone; a human tuning `Cadence`
afterward edits the file directly, the same hand-editable discipline `## Safety Net`'s `90`/`## Guardrails`'
`60` already follow.

## Never writes `Open`, `Out-of-scope`, or anything else on this section's account

A Housekeeping cycle's own in-flight state was never tracked in `## Housekeeping` to begin with — it
stays on the issue tracker, exactly as it did before this section existed
(`housekeeping-track.md`'s own *Resuming an in-progress cycle* section). This write never adds, removes,
or reads a slug from `Open`/`Out-of-scope` (this section has neither, the same shape `## Investigation`
already has) and never writes anything on this section's account — a Housekeeping
cycle delivers maintenance work, not a tooling-tree node adoption.

## Old-schema repos

A `bookkeeping.md` with no `## Housekeeping` heading yet — including one still carrying the old, now-
retired top-level `Housekeeping cadence` field from before this Track existed — is simply a target whose
Housekeeping Track has never run under this scheme: this write creates the section fresh, exactly as the
first-ever-scan case above already describes, ignoring whatever the old field held (it's never read,
migrated, or removed by this write — same "old fields simply stop being read or written" rule
`refactoring-bookkeeping.md`'s own "Old-schema repos" section already applies to every other Track).
Independent of `## Safety Net`'s/`## Guardrails`'/`## Investigation`'s own presence or absence — a target
can have run any combination of the other three Tracks' first scans, with `## Housekeeping`'s own first
scan arriving on its own schedule regardless.
