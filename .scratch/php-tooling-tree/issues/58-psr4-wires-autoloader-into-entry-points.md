# 58 — `psr-4` wires the autoloader into the target's entry points, not just proves the mechanism

**What to build:** `psr-4`'s own MR scope currently proves the PSR-4 mechanism works (declare the
mapping, migrate exactly one file) but never touches how the target's own request-time code actually
loads classes — every entry point keeps accumulating manual `require_once` calls indefinitely, since
nothing ever wires `vendor/autoload.php` into the runtime loading path. Extend `psr-4`'s own
fulfilment check and MR scope to close that: once the mapping mechanism is proven, also wire
`vendor/autoload.php` into the target's **Composition root** (if one exists), or every **Entry point**
individually (if it doesn't) — two new `CONTEXT.md` terms this ticket introduces.

- **New fulfilment criterion (in addition to the existing "mapping declared and used" bar):** the
  target's Composition root (or, absent one, every detected Entry point) contains a
  `require`/`include` resolving to `vendor/autoload.php`. A target with no detectable entry points at
  all (e.g. a pure library) is vacuously fulfilled on this criterion — nothing to wire.
- **Entry point** (new node-independent detection primitive, `CONTEXT.md`): a `.php` file outside the
  psr-4-mapped namespace directory (and outside `vendor/`, test directories) that no other file in the
  target's own source tree `require`s or `include`s.
- **Composition root** (new term, `CONTEXT.md`): the single file, if any, more than half of the
  detected entry points directly require — recognized even when some entry points don't converge on
  it (those get wired individually alongside it, not treated as disqualifying the recognition).
- **MR scope addition:** wire the autoloader require into the composition root (or each non-converging
  entry point/every entry point when there's no composition root at all) — a `.php` insertion, no
  removal of any existing manual `require_once` line for not-yet-namespaced files. Explicitly **out of
  scope**: retiring existing manual requires, or actively tracking every file's own eventual PSR-4
  migration — that stays `structural-scan`'s own slow, incremental job, unchanged. Stated as expected
  hygiene, not a tracked goal: a future incremental per-file PSR-4 migration (whoever does it) should
  also drop that file's own now-redundant require line from wherever it was required.
- **Scope: stop-the-bleeding only.** This closes the #194 defect class going forward (a new class can
  never again go missing from a manual require list, because new code stops needing one) without
  re-litigating `psr-4`'s already-settled incremental, non-disruptive migration philosophy for existing
  files.
- **PHP-tree-specific**, not the generic root — the concrete detection/action (finding
  `vendor/autoload.php`, PHP's own require/include semantics) is Composer/PHP-specific, matching this
  suite's existing precedent for not attempting a generic-tree shape before a second language
  specialization exists to validate one against.

**Why:** Confirmed root cause of a real production incident already observed live on
`Art4/legacy-todo`: PR #194 added a new class (`Page.php`) but forgot to add it to `Bootstrap.php`'s
own manual `require_once` list — invisible to 126 green PHPUnit tests (loaded via Composer's PSR-4
autoloader in test bootstrap) and full static analysis, only caught by a human reviewer manually
clicking through a live instance. That gap directly motivated building a whole new E2E HTTP test suite
(issue #197 → PR #199) as a compensating, after-the-fact detection control — this ticket fixes the
underlying habit instead, so the defect class becomes structurally harder to reintroduce, not just
easier to catch.

**Blocked by:** none.

**Priority:** medium — no target repo is currently mid-incident on this, but it's the direct root
cause of one that already happened.

**Status:** done

- [x] `tooling_tree.py`: new detection helpers — `_psr4_mapped_dirs`, `_entry_point_candidates`
  (require/include graph over `.php` files outside the mapped directory, `vendor/`, test directories,
  and known repo-root tooling-config scripts like `rector.php`/`.php-cs-fixer.php` — found and fixed a
  real false-positive during implementation: those scripts have a `.php` extension and nothing
  requires them either, so without the exclusion they'd wrongly need wiring too), `_require_targets`
  (fixed a real bug found via the new tests: the captured require-target string starts with `/`, which
  makes pathlib treat it as absolute and silently discard the base directory unless stripped first),
  `_detect_entry_points` (composition-root detection excludes any target resolving into `vendor/` —
  found and fixed a second real bug: a single entry point requiring `vendor/autoload.php` directly was
  otherwise misidentified as its own composition root), `_autoloader_wired`.
- [x] `psr-4`'s own fulfilment check in `detect_nodes()`: ANDs the new autoloader-wired criterion onto
  the existing declared-and-used bar; `detect_nodes()`'s own `details` dict exposes both criteria
  separately (`mechanism_verified`, `autoloader_wired`).
- [x] `psr-4.md`: Fulfilment check and MR scope rewritten to the expanded bar; new "Autoloader wiring:
  stop the bleeding, not a full migration" section states the scope explicitly, including the
  future-migration hygiene expectation. Drive-by fix: corrected a stale "thirteenth leaf" reference to
  the current "eleven" leaves.
- [x] `CONTEXT.md`: two new entries — **Entry point**, **Composition root**.
- [x] New ADR (0042).
- [x] Tests: `Psr4AutoloaderWiringTests` (8 new tests, one added after `/code-review`'s Spec axis
  flagged the gap) — entry-point detection, composition-root recognition including the straggler case
  *and* the exact-tie case (2 of 4 — confirms the threshold is a strict majority, not "at least half"),
  the autoloader-wired criterion (fulfilled/unfulfilled/vacuously-fulfilled), tooling-config-script
  exclusion, test-directory exclusion. Existing `PsrFourGateTests` (declared-and-used bar) unchanged
  and still green — none of its fixtures have any entry point outside the mapped directory, so all
  stay vacuously fulfilled on the new criterion too. Full suite green (283 tests).
- [x] `.changelog.d/` fragment.
- [x] Fixture fallout: checked every `fixtures/php/*` project — none currently declare any real
  application entry point outside their mapped namespace directory (only tooling-config scripts,
  already excluded), so none were affected; all 8 `fixtures/harness/run.sh roadmap` runs pass
  unchanged, no `expected/roadmap.json` regeneration needed this time.

## Comments

> **2026-09-09:** Filed after a `/grill-with-docs` session (German — `grilling` + `domain-modeling`),
> growing directly out of the `Art4/legacy-todo` reviewer-loop findings log's PR #194 incident and the
> user's own direct request to fix the underlying habit rather than only detect it after the fact.
> Settled across two rounds: (1) scope is stop-the-bleeding only, not a full manual-require retirement
> — matches `psr-4`'s own already-settled incremental philosophy; (2) the wiring lives in `psr-4`'s own
> node (not `composer`'s — wiring in the autoloader before any of the target's own code is namespaced
> doesn't yet solve anything); (3) two new terms, **Entry point** and **Composition root**, needed
> since nothing in this suite's vocabulary distinguished them before; (4) entry-point search is scoped
> to outside the psr-4-mapped directory, reusing an already-computed fact rather than a second
> directory-scoping rule; (5) a composition root is recognized even with some non-converging entry
> points (stragglers get wired individually alongside it); (6) future incremental per-file migrations
> should drop their own now-redundant require line as hygiene, stated but not tracked; (7) PHP-tree-
> specific, no generic-root shape. User confirmed the full design ("ja, passt").
>
> `CONTEXT.md` text as actually committed (two corrections made after this ticket was first filed,
> both caught during implementation/review, not part of the original grilling session): "script"
> dropped from Entry point's `_Avoid_` list (it collides with legitimate uses of the word elsewhere in
> skill prose, caught by `scripts/validate_skills.py`); the specific `Art4/legacy-todo` repo name
> dropped from Composition root's own text (CONTEXT.md is this suite's own generic glossary, never
> implementation detail tied to one target — described the same gap generically instead).
>
> **Entry point**:
> A PHP file the runtime (webserver or CLI) executes directly — never `require`d or `include`d by
> another file in the target's own source tree. `psr-4`'s autoloader-wiring step targets every entry
> point directly when the target has no single **Composition root**.
> _Avoid_: front controller
>
> **Composition root**:
> The one file, if any, the target's own **Entry point**s mostly delegate to for wiring the application
> together — the single place a target's own manual class-loading historically accumulates. Not every
> target has one, and recognizing one doesn't require unanimous delegation: an entry point that doesn't
> delegate to it still gets wired directly, on top of the root rather than in place of it. The kind of
> gap `psr-4`'s wiring step exists to close lives exactly here: a class missing from this one file's own
> manual require list, invisible to every autoloader-based test.
> _Avoid_: bootstrap file (a file literally named `bootstrap.php` isn't necessarily filling this role),
> application root
