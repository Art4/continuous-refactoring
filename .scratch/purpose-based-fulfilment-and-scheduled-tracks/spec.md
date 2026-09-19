# Purpose-based fulfilment and scheduled Tracks

**Status:** ready-for-agent

Full design rationale: [ADR-0055](../../docs/adr/0055-purpose-based-fulfilment-and-scheduled-tracks.md) and this same session's `CONTEXT.md` changes (**Track**, **Guardrails**, **Onboarding**, **Safety Net**, **Housekeeping**, **Fulfilment check**). This spec is the buildable *what*; the ADR is the *why*.

## Problem Statement

`refactor-scan` can propose adopting a tool (e.g. `php-cs-fixer`) even though the target project already has a real, working equivalent under a different name (e.g. Laravel Pint, which wraps PHP CS Fixer internally under its own config). This risks a redundant, possibly colliding second adoption — and it can slip through fully labeled `ready-for-agent` even when the candidate's own text flags the risk, because nothing in the pipeline is positioned to catch it before that point. More generally, every tooling-tree node's Fulfilment check is limited to a fixed, hardcoded list of tool names, so any node with more than one viable real-world implementation carries the same blind spot.

Separately, tooling adoption (Safety Net), signal-producing tooling (Guardrails), ongoing structural refactoring, and periodic maintenance (currently a fully separate `continuous-housekeeping` skill with its own cadence) compete for attention pass by pass with no shared, principled way to decide what gets worked on next.

## Solution

Fulfilment checks stop matching hardcoded tool names and instead ask, per node, "does this repo genuinely have something serving this node's stated Purpose" — recognized by an agent walking the tree, not a script matching package names.

The loop's work is organized into four scheduled Tracks — **Safety Net**, **Guardrails**, **Investigation**, **Housekeeping** — each with its own cadence, so the right kind of work gets picked automatically, in a fair and predictable order, including a one-time bootstrap sequence that shows real refactoring progress before piling on more tooling. `continuous-housekeeping` stops being a separate skill the user has to remember to run and becomes the fourth Track, scheduled the same way as the other three, while still triggerable on demand exactly as today.

## User Stories

1. As a target-repo maintainer, I want the loop to recognize Laravel Pint as satisfying `php-cs-fixer`'s purpose, so that it never proposes a redundant, possibly colliding second code-style tool.
2. As a target-repo maintainer, I want any tooling-tree node's Fulfilment check to recognize whichever real, working tool actually serves its stated Purpose, so that I'm never asked to adopt a tool I already have under a different name.
3. As a target-repo maintainer, I want the four kinds of loop work organized into separate, independently-scheduled Tracks, so that one kind of work never silently starves another.
4. As a target-repo maintainer, I want each Track to run on its own sensible cadence instead of every pass re-walking the entire tree, so that expensive re-checks don't happen more often than needed.
5. As a target-repo maintainer, right after my Safety Net foundation is first fully in place, I want to see one real piece of delivered refactoring work before being asked to adopt more tooling or sit through a maintenance sweep, so that the loop demonstrates value early.
6. As a target-repo maintainer, I want `continuous-housekeeping` to no longer be a skill I have to remember to invoke separately, so that maintenance sweeps happen on the same schedule as everything else the loop does.
7. As a target-repo maintainer, I still want to be able to force a specific Track on demand, so that I retain manual control when I want it.
8. As a target-repo maintainer, I want `bookkeeping.md` to show me, per Track, only what's still open or explicitly rejected — never a giant list of everything that's already fine — so that the file stays readable as the tree grows.
9. As a target-repo maintainer, I want a rejected node (out-of-scope) to keep working exactly as it does today — closing every node that required it, cascading correctly — so that nothing about the tree's existing gating semantics breaks.
10. As a target-repo maintainer, I want a Track that's never been scanned to be indistinguishable from "definitely due," so that a freshly onboarded repo's first pass naturally walks everything without special-casing.
11. As a target-repo maintainer, I want a Track's first scan to always record that it ran — even if it found nothing to do — so that a fully-compliant repo isn't rescanned every single pass forever.
12. As a target-repo maintainer, when multiple Tracks have open work at once, I want a predictable, fixed order for which gets worked first, so that I can anticipate what the loop will do next.
13. As a target-repo maintainer, I want the one-time Investigation-before-Guardrails-before-Housekeeping bootstrap sequence to happen exactly once per repo, so that later passes follow the steady-state priority order instead.
14. As a target-repo maintainer, I want `git`/`loop-config`'s own human interview to remain a separate, mandatory first step, so that the loop never guesses at my Create-mode/Focus-areas/Refactoring-goal preferences.
15. As a target-repo maintainer, when the loop genuinely can't tell whether two different tools both plausibly satisfy a node's purpose, I want it to flag the candidate for my input (`needs-info`) rather than silently guess, so that ambiguous collisions still reach a human.
16. As a target-repo maintainer, when I've adopted code-style tooling in a way no tool can detect (pure convention/code review), I want to record that as an ordinary rejection with my own stated reason, so that the loop stops proposing something I've already decided not to formalize.
17. As a target-repo maintainer on an already-onboarded repo with the old `bookkeeping.md` shape, I want the loop to transition to the new Track-based shape automatically on its next pass, so that upgrading the suite doesn't require manual repo surgery.
18. As a suite maintainer, I want the master list of recognized nodes per Track to remain the existing tooling-tree docs, so that adding a new node stays a single edit.
19. As a suite maintainer, I want `refactor-scan` to be told which Track to scan for a given pass rather than deciding on its own, so that the scheduling policy lives in one place.
20. As a suite maintainer, I want `refactor-learn`'s existing Open/Out-of-scope-writing rules extended symmetrically (merge → remove from Open; rejection → remove from Open and write `out-of-scope/`), so that the bookkeeping stays consistent with how rejections already work everywhere else in the suite.
21. As a suite maintainer, I want the suite-wide open-MR cap to apply across all Tracks combined, not per Track, so that the loop doesn't overwhelm a reviewer just because work is now split across four Tracks.

## Implementation Decisions

- **`continuous-refactoring` orchestrator**: gains a Track-selection step at the very start of each pass, replacing today's step-0 "housekeeping only if opted in" special case. Reads each Track's `Cadence`/`Last scan` (and `Open` non-emptiness, for Safety Net/Guardrails) from `bookkeeping.md`, computes the staleness ratio, applies the fixed tie-break/allocation order (Safety Net > Guardrails > Housekeeping > Investigation), and applies the one-time bootstrap exception. Hands the selected Track to `refactor-scan` as an input. A manual override (invoking a specific Track directly) bypasses selection but still respects "Open non-empty → work it, don't rescan" for Safety Net/Guardrails.

- **`refactor-scan`**: becomes Track-aware — its tooling-node-proposal step is scoped to the Track it's told to scan. For Safety Net/Guardrails, the tree-walk mechanism itself (which nodes are in scope, required/recommended/required-any semantics, cascading rejection) is unchanged; what's replaced is per-node: dependency-name matching is replaced by an agent judging each node's own Purpose statement against the actual repo. For Investigation, the existing structural-scan proposal logic is unchanged, just triggered by Track selection. Housekeeping's own orchestrator special-case is removed; its due-check/reconciliation/checklist/deliver steps run as this Track's own content, unchanged, invoked from Track selection instead of a standalone due-check.

- **`continuous-housekeeping` retired as a standalone entry point.** Its `references/` (cadence-interview, `template-file-format.md`) move under `continuous-refactoring`. Its process content is preserved verbatim as the Housekeeping Track's own content — only the trigger changes. Manual invocation stays available, generalized to the same Track-name-as-argument pattern the other three Tracks use.

- **`bookkeeping.md` schema**: existing top-level fields (`Create-mode`, `Focus areas`, `Refactoring goal`) unchanged. `Fulfilled nodes` and the single global `Pending candidates` are retired, replaced by four sections:
  - `Safety Net` / `Guardrails`: `Cadence`, `Last scan`, `Open` (`- <slug> (#issue)`), `Out-of-scope` (`- <slug>` + pointer to the unchanged `out-of-scope/<slug>.md`). Section absent = Track never run.
  - `Investigation`: `Cadence`/`Last scan` only, for scheduling; open/done/rejected state stays on the issue tracker / `merge-requests.md` as today.
  - `Housekeeping`: `Cadence`, `Last scan` only; swept content stays in `housekeeping-template.md`, unchanged.
  - A Track's `Last scan` is written the moment its scan completes, regardless of outcome — including an all-clear result with both lists empty.

- **`refactor-learn`**: its closing-call write logic (today: `Fulfilled nodes`, `out-of-scope/` on rejection) retargets to the relevant Track's `Open`/`Out-of-scope` section. Merge → remove from that Track's `Open`. Rejection → remove from `Open`, write `out-of-scope/<slug>.md` (format unchanged), add the pointer under `Out-of-scope`. The suite-wide open-MR cap stays one check across all Tracks combined, not duplicated per Track.

- **Scheduling algorithm**: `overdue_ratio(track) = (today − Last scan) / Cadence`; among due (`>= 1`) and eligible Tracks (Safety Net/Guardrails: `Open` empty; Investigation/Housekeeping: always eligible), pick the highest ratio. Ties, and effort allocation across Tracks simultaneously holding `Open` work, fall back to the fixed order Safety Net > Guardrails > Housekeeping > Investigation. Default cadences: Safety Net 90 days, Guardrails 60 days, Housekeeping 7 days (unchanged default), Investigation no fixed interval (always eligible, lowest tie-break priority).

- **One-time bootstrap exception**, tracked implicitly (no stored flag): the pass right after Safety Net's `Open` transitions from non-empty to empty runs Investigation next (one candidate, fully delivered: propose → design → implement → learn); the following pass runs Guardrails (one scan-and-clear cycle); the pass after that runs Housekeeping (one cycle) — each overriding ordinary staleness-ratio selection for exactly that one turn. Ordinary scheduling resumes permanently for that repo once Housekeeping's first turn completes.

- **Fulfilment-check execution**: for Safety Net/Guardrails nodes, an agent walking the tree during that Track's scan evaluates each node's Fulfilment check against its own Purpose statement, recognizing any real, working tool — not a fixed dependency-name list. Required/Recommended/Required-any edge semantics and cascading closure on a rejected required parent are unchanged. Node slugs are unchanged.

- **Out-of-scope reuse for agent-undetectable equivalents**: when no committed artifact exists at all for a node whose purpose the maintainer states is already served some other way, that's an ordinary `out-of-scope/<slug>.md` rejection with the stated reason — no new bookkeeping state. Scoped safely to nodes without required descendants.

- **`decision-gate.md`**: unchanged. Genuinely ambiguous agent judgement calls still route through the existing Flagged-candidate mechanism (`needs-info`).

- **No migration step**: repos on the old schema simply stop having old fields read/written; the first Track scan under the new model re-derives everything from a blank slate (no section = never run), the same mechanism a Track already uses whenever its own scope grows later.

## Testing Decisions

Seam: the fixture harness's existing advisory/local-only mechanism (`fixtures/harness/run.sh <fixture-type> <fixture-name> --opencode`) — the same posture `php-decision-gate-bypass`/`judge`/`lift` already use, checking behavior against a real agent run rather than deterministic script output. This is deliberate: the feature being tested replaces the deterministic-script ground truth those older tiers assumed.

Each new fixture: a seeded target-repo state (`project/`) plus an `expected/behavior.md` describing what the orchestrator/scan should do — the existing fixture directory shape.

New fixtures to add:

1. **Purpose-based recognition** — a target with `laravel/pint` installed and configured, no `friendsofphp/php-cs-fixer` anywhere: expect `php-cs-fixer` recognized fulfilled, never proposed.
2. **Track selection under simple staleness** — a `bookkeeping.md` with several Tracks' `Cadence`/`Last scan` at different staleness ratios, none with `Open` work: expect the most-overdue eligible Track selected.
3. **Open blocks rescan** — a Track with non-empty `Open` and a `Last scan` far past its cadence: expect the existing `Open` item worked, not a fresh rescan.
4. **First-run-ever recording** — a Track with no section at all, whose scan finds nothing: expect a section written afterward with `Last scan` set and both lists empty.
5. **One-time bootstrap sequence** — a `bookkeeping.md` where Safety Net's `Open` just transitioned to empty for the first time: expect Investigation selected next, not Guardrails; a second fixture (or a second pass in the same one) confirms Guardrails runs next after Investigation's one turn, not Investigation again.
6. **Rejection symmetry** — a Safety Net `Open` item closed as `wontfix`: expect it removed from `Open` with a corresponding `Out-of-scope` pointer and `out-of-scope/<slug>.md` written.
7. **Old-schema pass-through** — a `bookkeeping.md` still in the old shape (`Fulfilled nodes`, global `Pending candidates`): expect every Track treated as "never run" and the pass to proceed normally, without erroring on the unrecognized old fields.

Prior art: `fixtures/php/php-decision-gate-bypass` (seeded state + `expected/behavior.md` + advisory harness) is the direct template for all seven fixtures above.

What makes a good test here: assert on the *decision* reached (which Track ran, what got written to `bookkeeping.md`, what got proposed) — never on internal reasoning trace or prose wording.

## Out of Scope

- Retiring or rewriting `tooling_tree.py`/`scripts/test_tooling_tree.py`, and reworking the fixture harness's `tier2`/`tier3` precision-recall tiers that depend on them — ADR-0055 names this explicitly as a separate follow-up.
- Updating the remaining files still referencing the old term "Signal wave" (outside `CONTEXT.md`) to "Guardrails."
- Reconciling the Psalm/PHPStan mutual-exclusion housekeeping write (`psalm.md`) with the new agent-driven tree walk — flagged as likely redundant, not resolved.
- Renaming tooling-tree node slugs (e.g. `php-cs-fixer`) toward their Purpose — explicitly deferred during grilling.
- Extending Purpose-based recognition to Investigation's own candidate search — that Track was never fulfilment-check-driven to begin with, so it's unaffected.
- A third bookkeeping state for agent-undetectable equivalents ("Confirmed node") — explicitly dropped during grilling in favor of reusing `out-of-scope`.

## Further Notes

This spec is large enough that `/to-tickets` should split it along the seams already visible above: the `bookkeeping.md` schema change plus `refactor-learn`'s write-side retargeting is likely the most foundational/blocking ticket (everything else reads or writes the new shape); Track-aware `refactor-scan` plus Purpose-based fulfilment can follow; the orchestrator's scheduler plus the one-time bootstrap exception depends on both; `continuous-housekeeping`'s retirement/folding-in is comparatively self-contained and could run in parallel with the others.
