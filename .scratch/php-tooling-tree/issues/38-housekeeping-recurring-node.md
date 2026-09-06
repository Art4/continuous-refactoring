# 38 — Recurring `housekeeping` node (periodic maintenance sweep)

**What to build:** A new tooling-tree node with a fundamentally different lifecycle from every existing
node: it re-proposes itself periodically instead of staying fulfilled forever once done.

- `housekeeping` — required parent: `composer`.
- Re-proposed whenever the last housekeeping pass is more than 7 days ago. The date of the last pass is
  recorded in `docs/refactoring/config.md`.
- Bundles several periodic maintenance concerns into one recurring MR: the `composer audit` call,
  `test-runner-if-missing`, a `composer update` run, (per ticket 34's own grilling) a check that
  adopted dev tools are actually wired into CI, and (per the `Art4/legacy-todo` reviewer-loop run,
  2026-09-05) working down Psalm's own `psalm-baseline.xml` — see *Why* below.

**Why:** Came up while grilling ticket 34 as a considered alternative to that ticket's CI-gating
self-wiring fix — a broader, recurring mechanism that would keep catching "adopted but not enforced/not
current" gaps on an ongoing basis, rather than a one-time fulfilment-check tightening. Deliberately parked
as its own ticket rather than decided or designed there: it introduces a genuinely new pattern the tree
has never had before (see *Open design questions* below), and conflating it with ticket 34's narrower,
already-well-understood fix would have blocked that ticket on a much bigger, unresolved design.

`composer update` in particular is not modeled anywhere in the tree today — there is no existing node for
"dependencies are kept reasonably current" (only `composer-audit`'s narrower "no *known* vulnerable
dependency" check).

**Psalm baseline shrink, added 2026-09-05:** ticket 51/ADR-0033 built a baseline-shrink mechanism for
PHPStan's level chain (`refactor-scan` step 4b, `refactor-design`'s `phpstan-baseline-shrink.md`) —
deliberately scoped PHPStan-only, Psalm's own suppression format (`psalm-baseline.xml`) left for a
separate future ticket. Confirmed live on `Art4/legacy-todo`: `psalm-taint-analysis`'s own Fulfilment
check never required an empty baseline to begin with (unlike PHPStan's level nodes), so once adopted
it stays "fulfilled" forever regardless of how many findings sit in `psalm-baseline.xml` — 25 real,
tracked tainted-data findings landed there (PR #151) with nothing in the suite ever proposing to work
them down. Parking the idea here rather than as its own ticket, since it's the same shape of concern
this ticket already exists to hold ("adopted but not actually being kept current/complete" — same
family as `composer update`) — worth deciding during this ticket's own grilling whether it's a
`housekeeping` MR concern, or turns out to want the exact ticket-51 mechanism transplanted onto
Psalm's own format instead (a `refactor-scan`/`refactor-design` change, not a recurring node) once
this ticket actually gets designed.

**Blocked by:** none, but this is the least-designed of the three ideas that came out of ticket 34's
grilling and needs its own dedicated `/grill-me` session from a much earlier stage than usual — likely
starting from "should this be a tree node at all, or a different mechanism entirely" rather than assuming
the shape sketched above.

**Priority:** low — no discovered bug motivates urgency (contrast with ticket 37's structural-scan gap);
this is a proposed enhancement, not a fix.

**Status:** done

**Settled design** (superseding every sketch above — the shape here is what actually got built):

- **Not a tooling-tree node.** A new, standalone skill, `continuous-housekeeping` — structurally a peer
  of `continuous-refactoring` itself, not a step inside it and not something `refactor-scan`/
  `refactor-prioritize` ever touch. Resolves the "breaks the tree's monotonic assumption" question
  outright: it was never part of `next_candidates()`/`roadmap()` to begin with.
- **Cadence:** configurable per target, default weekly (not the originally-guessed 7 days) — decided
  once via the skill's own tiny setup interview, recorded as a new `Housekeeping cadence` field in
  `bookkeeping.md`.
- **No stored "last run" date.** Due-ness comes from searching the tracker for the most recent
  `Housekeeping — <date>`-titled issue and comparing its age to the cadence — tracker-agnostic, via the
  same `docs/agents/issue-tracker.md` abstraction every other skill in the suite already uses.
- **Generic mechanism, PHP-specific content, cleanly separated by layer.** The skill itself is entirely
  generic. What gets checked each cycle is contributed by individual tooling-tree nodes: a node's own
  doc may name an optional `Housekeeping` field (documented once, generically, in `CONTEXT.md`'s
  **Tooling tree** entry). When that node's own delivering MR lands, it also appends its `Housekeeping`
  line to the Refactoring Notes' new `housekeeping-template.md`, creating the file fresh if needed.
  `continuous-housekeeping` never walks the tree itself — it just reads whatever's accumulated.
- **Contributed so far:** `composer` (composer update), `composer-audit` (review the audit report for
  anything CI's own point-in-time gate can't catch after the fact), `phpstan-deprecation-rules` (re-check
  for newly-surfaced deprecations after a dependency bump), `php-minimal-version` (a newer PHP
  patch/minor of the same declared line — deliberately distinct from that node's own Fulfilment check,
  which only asks whether the floor is *correct*, not *current*). One exception: if `php-minimal-version`
  is already fulfilled on the very first scan (no delivering MR of its own ever runs), `loop-config`'s
  own first MR contributes the line instead.
- **One issue per due cycle**, cumulative checklist — not independently-recurring per-concern items.
- **Psalm baseline shrink stays out of this ticket entirely** — a security-relevant backlog deserves
  ticket 51's own continuous, pass-by-pass treatment transplanted onto Psalm's format, not a once-a-cycle
  sweep; left for its own, separate ticket.
- **ADR-0037** records this decision.

Open design questions from before grilling (kept for the record; each resolved below):

- [x] **Breaks the tree's monotonic assumption?** Moot — not a tree node at all, never part of
  `next_candidates()`/`roadmap()`, so nothing about `structural-scan`'s resolved-gate is affected.
- [x] "Required parent: `composer`" edge type — moot, no tree edges at all; a standalone skill needs none.
- [x] Bundling into one recurring MR vs. independently-recurring checks — one issue per due cycle, whose
  checklist accumulates from however many nodes have contributed, confirmed during grilling.
- [x] How the last-housekeeping date is recorded — it isn't. Due-ness is derived from tracker history
  (most recent `Housekeeping — <date>` issue) each time, no stored date field.
- [x] PHP-tree-specific or generic root? Both, cleanly separated: the skill/cadence/interview/template-file
  mechanism is generic; only the individual node contributions (composer, composer-audit,
  phpstan-deprecation-rules, php-minimal-version) are PHP-specific. ADR-0037 written, matching the
  anticipated ADR-0016-weight change.
- [x] Psalm baseline shrink — confirmed out of scope for this ticket; wants ticket 51's own mechanism on
  Psalm's format instead, as its own separate ticket.

## Comments

> **2026-08-30:** Filed as a follow-up from ticket 34's `/grill-me` session (in German), parked
> deliberately rather than designed — see `.scratch/php-tooling-tree/issues/34-ci-quality-job-wiring.md`'s
> comments for the grilling transcript context this idea was raised in.

> **2026-09-05:** Added Psalm baseline-shrink as a bundled concern, per the user's explicit request,
> after ticket 51 (PHPStan-only baseline-shrink mechanism) shipped and the same gap was confirmed live
> for Psalm on `Art4/legacy-todo` (PR #151, 25 tainted-data findings landed with no mechanism to work
> them down — `psalm-taint-analysis`'s own Fulfilment check never required an empty baseline to begin
> with). Not designed here either — same "parked, not decided" status as everything else in this
> ticket; flagged as a real open question whether it even fits the `housekeeping` bundle shape at all,
> or wants ticket 51's own mechanism transplanted onto Psalm's format instead.

> **2026-09-06:** Grilled (`/grill-me`, German, five rounds) starting from "should this be a tree node
> at all" as anticipated. Settled on a standalone `continuous-housekeeping` skill, informed by a
> real-world reference example the user shared (a working housekeeping skill + issue template from
> their own practice) — used purely as anonymized structural inspiration, no identifying detail from it
> carried into this ticket, the ADR, or the implementation. Key departures from the reference material
> during grilling: cadence made configurable (default weekly, not a fixed interval), tracker-agnostic
> (the reference was GitLab-specific), and the checklist itself made dynamic — individual tooling-tree
> nodes contribute their own `Housekeeping` line to an accumulating template file as part of their own
> delivering MR, rather than a fixed bundle hardcoded into the skill. Implemented on branch
> `tickets/38-continuous-housekeeping`: new skill (`skills/continuous-housekeeping/`, `SKILL.md` +
> `cadence-interview.md` + `template-file-format.md`), `Housekeeping` fields added to `composer`,
> `composer-audit`, `phpstan-deprecation-rules`, and `php-minimal-version` (plus the `loop-config`
> exception for the latter), new `Housekeeping cadence` bookkeeping field, `CONTEXT.md` vocabulary
> additions, README updates (including an incidental fix to a pre-existing, unrelated inaccuracy — the
> main loop was wrongly described as having a stored cadence), ADR-0037. No `tooling_tree.py` changes —
> pure documentation/skill content, no new detection logic. 257/257 tests pass (unchanged, no new
> Python logic); validator clean (same 5 pre-existing warnings, after fixing several
> self-inflicted glossary-avoid-term violations in the new skill's own prose).

> **2026-09-06 (review):** User caught a real gap before merge, live against `Art4/legacy-todo` itself:
> the delivering-MR-only contribution path means a node fulfilled *before* a target adopts
> `continuous-housekeeping` never reaches the template file at all — `composer`/`composer-audit`/
> `phpstan-deprecation-rules` on that exact repo were all fulfilled long before this skill existed, so
> none of their `Housekeeping` lines would ever have appeared. Fixed by adding a second contribution
> path: `continuous-housekeeping` itself reconciles `housekeeping-template.md` against `bookkeeping.md`'s
> `Fulfilled nodes` cache every cycle (not just once), appending any node's `Housekeeping` line not yet
> present. Cheap — the field is already being read for the cadence check — and no tree-walk of its own;
> it only reads a cache another skill already maintains. `SKILL.md`, `template-file-format.md`,
> `CONTEXT.md`, and ADR-0037 all updated on the same branch/PR before merge.
