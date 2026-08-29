---
name: refactor-design
description: Turn the chosen node into a concrete refactoring plan, filing it as an issue — search the codebase first when the node is structural-scan.
---

# Refactor Design

Turn the **node** `refactor-prioritize` chose into a **plan** concrete enough to implement, and file it as the issue that carries that plan — this skill is where a node first becomes an issue, not `refactor-scan`. The `/grilling` loop sharpens a structural design; `/domain-modeling` keeps the domain model current as decisions land.

## Process

### 1. Check whether it's already fully specified

An ordinary **tooling tree** node (`skills/refactor-scan/references/tooling-tree.md`, or a language specialization's tree) is fully specified by definition — its Tool, Purpose, Fulfilment check, and MR scope are already written in the tree doc. Skip straight to step 5 and file/write the plan from that spec — no codebase search, no grilling, nothing to ground beyond the doc itself.

The **`structural-scan`** node is not pre-specified — it names an open gate, not a candidate. Continue to step 2 to find one.

### 2. Find a structural candidate

This is the codebase walk that used to be `refactor-scan`'s — it only runs here, for the node actually chosen, not speculatively on every pass.

Decide *where* to look before you look:

- If the user named a direction — a module, a subsystem, a hot spot they already feel — take it and skip the inference below.
- Otherwise walk back a good stretch of the commit history (`git log --oneline`) to find the **hot spots** — files and areas that keep coming up — and let those paths pull your attention first. If changes are scattered with no clear hot spot, widen the net.

Then explore organically and note where you experience friction. Look for:

- **Shallow modules** — little **depth**: interface nearly as complex as the implementation. Apply the **deletion test**: would deleting it concentrate complexity, or just move it? A "concentrates" is the signal you want.
- Missing **locality** — pure functions extracted for testability, but the real bugs hide in how they're called.
- Low **leverage** — a lot of interface surface buying little behaviour behind it.
- Tightly-coupled modules leaking across their **seams**.
- Untested parts, or parts hard to test through their current interface.
- **Tooling pressure** — places the fulfilled tooling (PHPStan, Rector, style) keeps flagging.

Use the `/codebase-design` vocabulary (module, interface, depth, seam, leverage, locality) in the candidate description — don't drift into "component," "service," or "API."

If more than one genuine friction spot turns up, **pick the single strongest one** — same factors `refactor-prioritize` uses (heat, leverage, tooling pressure, risk) — and set the rest aside for a future pass's walk. One `structural-scan` selection produces exactly one candidate; the loop being continuous is what catches the others later, not filing them all now.

### 3. Ground in the candidate

Read the code the candidate names (and, for a resumed structural candidate, the issue if step 2 already ran in an earlier interrupted pass). Read `CONTEXT.md` and the ADRs in the area. Understand *why* it's a candidate (the friction) before proposing anything.

### 4. Grill toward the seam

Structural candidates only — skip for a tooling-tree node. Run `/grilling` on the candidate. The decision tree hangs off these branches:

- **The deepened module** — what does the module become, and what is its one job? What disappears behind it?
- **The seam** — where is the public boundary, and what is it tested through?
- **The interface** — what does the interface expose, and does it stay deep (implementation complexity > interface complexity)?
- **Locality** — what moves together, and what must *not* spread?
- **Tests that survive** — which existing tests stay, which are rewritten, which new ones appear at the seam?

Side effects happen inline as decisions crystallise (per `/domain-modeling`):

- Naming a module after a concept not in `CONTEXT.md`? Add the term.
- User rejects a design with a load-bearing reason a future scan should not re-suggest? Offer an ADR.

### 5. File the issue and write the plan

**A tooling-tree node:** before filing, check whether an issue titled exactly `Tooling tree: <Name>` (the node's **Name** from the tree doc, e.g. `Tooling tree: PHPStan Level 0` — never its slug) is already open — if so, that's the issue; don't file a second one (it means a prior pass got this far and was interrupted before `refactor-implement` finished). Otherwise create one titled that way, label **`refactor:candidate`**, and quote its Tool / Purpose / Fulfilment check / MR scope from the tree doc verbatim — that scope *is* the slice ordering, and *is* the plan.

**A structural candidate:** create an issue labelled **`refactor:candidate`** naming Where (module/files), Problem (the friction, in the project's domain language), and Signal (which friction signal from step 2 it came from). Then capture the plan on that issue: the deepened module, the seam and interface, the surviving tests, and the ordering of slices (see `refactor-implement`).

Either way: set `docs/refactoring/config.md`'s `Pending issue` field to this issue (`skills/continuous-refactoring/references/refactoring-config.md`) — the marker that lets a future `refactor-scan` resume this exact work instead of proposing something fresh if the pass stops here. `refactor-learn` clears it once a merge request exists.

**`loop-config` exception:** if the chosen node *is* `loop-config` itself, `docs/refactoring/config.md` doesn't exist yet — there's nowhere to write `Pending issue` at this step. Skip the write here; `refactor-implement` records it directly when it creates the file (its own `## Fallback`-adjacent step, not a grilling or domain-modeling concern).

The plan follows the foundational refactoring rules: behavior-preserving only, decomposed into the Kent Beck technique vocabulary, Strangler Fig for wide migrations, deterministic tool moves where a tool can do it — never hand-applied by the agent — and delivered on its own branch unless the human or the plan says otherwise.

## Output

The filed issue, carrying the plan → `refactor-implement`.

## Fallback

- **`/codebase-design`**: if installed, use its vocabulary for step 2. Otherwise skip it — the full vocabulary (module, interface, depth, seam, leverage, locality) is already inline in step 2 above; use those terms and don't drift into "component", "service", or "API".
- **`/grilling`**: if installed, use it. Otherwise the grilling loop mechanics (design tree, frontier, rounds) are inlined at `skills/refactor-design/references/grilling-fallback.md`.
- **`/domain-modeling`**: if installed, use its discipline. Otherwise the same reference file inlines the side effects this step performs — they're already inline in section 4 above too, and run regardless of whether this skill is installed.

## Completion criterion

The candidate has an issue (newly filed, or a resumed one) with a written plan on it, and `config.md`'s `Pending issue` names it. For a structural candidate: module, seam, interface, surviving tests, slice order — and the design survives the grilling (no open frontier). For a tooling tree node: the tree doc's Tool / Purpose / Fulfilment check / MR scope, copied onto the issue.
