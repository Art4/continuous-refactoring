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

**Status:** needs-triage

Open design questions (none of these were resolved during ticket 34's grilling — this ticket only records
that the idea was raised, not a design):

- [ ] **Breaks the tree's monotonic assumption.** Every other node's `fulfilled` flag only ever needs to
  flip false→true in practice (`detect_nodes()` is stateless/recomputed each scan, but nothing currently
  *depends* on a previously-fulfilled node becoming unfulfilled again). A node whose fulfilment is
  time-based would flip true→false on a schedule. Does this interact badly with anything downstream —
  most importantly `structural-scan`'s resolved-gate, which assumes leaves settle and stay settled?
  Should `housekeeping` feed `structural-scan` at all, or stay a deliberately separate, parallel track
  that never gates structural work?
  **Update 2026-08-30:** this claim is no longer quite accurate — [ticket 35](35-php-upgrade-recommendation-node.md)'s
  new `php-minimal-version` node is a second, already-decided precedent for a fulfilment check that can
  flip back to false, settled via its own `/grill-me` session. The two cases differ in *why* they flip:
  `php-minimal-version` is **fact-driven** (a relative comparison against a moving target — a tool's
  minimum version or a CI job's tested PHP version changing), not **time-driven** like `housekeeping`'s
  7-day timer. Worth considering both shapes together in this ticket's own grilling session, especially
  the `structural-scan` interaction question above — `php-minimal-version` isn't one of `structural-scan`'s
  resolved-leaves, so it hasn't had to answer that question yet, but `housekeeping` might.
- [ ] Is "required parent: `composer`" right, or does re-proposing every 7 days need a different kind of
  edge entirely (none of `required`/`recommended`/`resolved` currently express "gate, but also re-trigger
  on a timer")?
- [ ] Does bundling composer-audit/test-runner-if-missing/composer-update/CI-wiring into *one* recurring
  MR make sense, or should each remain (or become) its own independently-recurring check?
- [ ] How does `docs/refactoring/config.md` record the last-housekeeping date — new field, format,
  who/what writes it (presumably `refactor-learn`, matching its "only writer" role)?
- [ ] Is this PHP-tree-specific, or does it belong in the generic root (`tooling-tree.md`) since none of
  its bundled concerns (well, `composer audit` aside) are inherently PHP-specific? If generic, this likely
  needs its own ADR, not just a `php-tooling-tree.md` node entry — recurring nodes would be a rule change
  to the tree model itself, the same weight as ADR-0016's recommended-edge change.
- [ ] **Psalm baseline shrink — does it actually belong in `housekeeping`, or does it want ticket 51's
  own mechanism instead?** `psalm-baseline.xml` findings are structurally similar to PHPStan's
  baseline entries (a suppressed-but-real finding, groupable by root cause, fixable a few at a time) —
  arguably wants the same `refactor-scan` step 4b / `refactor-design` treatment ticket 51 built, not a
  bundled once-a-week MR that would either dump too many fixes in one recurring pass or under-address
  a real security-relevant backlog (SQL injection/XSS findings) by only touching it every 7 days.
  Decide during this ticket's own grilling rather than assuming the bundle shape fits.

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
