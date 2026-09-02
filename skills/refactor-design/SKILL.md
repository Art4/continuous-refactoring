---
name: refactor-design
description: Turn the chosen node into a concrete refactoring plan, filing it as an issue — search the codebase first when the node is structural-scan.
---

# Refactor Design

Turn the **node** `refactor-prioritize` chose into a **plan** concrete enough to implement, and file it as the issue that carries that plan — this is where a node first becomes an issue, not `refactor-scan`. `/grilling` sharpens a structural design; `/domain-modeling` keeps the domain model current as decisions land.

## Process

### 1. Check whether it's already fully specified

An ordinary **tooling tree** node (`skills/refactor-scan/references/tooling-tree.md`, or a language specialization's tree) is fully specified by definition — Tool, Purpose, Fulfilment check, MR scope are already written in the tree doc. Skip straight to step 5 and file/write the plan from that spec — no codebase search, no grilling.

**`loop-config` exception:** not fully specified by the tree doc alone — its MR scope names a human interview, not a fixed spec. Run `skills/continuous-refactoring/references/loop-config-interview.md` in full (explore, ask, summarize, record) before filing anything; skip step 5's usual "carry the tree doc's spec over precisely" move for this node only — file the interview's recorded decisions instead (step 5). Steps 2–4 (structural-candidate search, grilling) still don't apply — this stays a tooling-tree node in every other way.

The **`structural-scan`** node names an open gate, not a candidate. Continue to step 2 to find one.

### 2. Find a structural candidate

Only runs here, for the node actually chosen — not speculatively on every pass.

Decide *where* to look before you look: the user named a direction (module, subsystem, hot spot) → take it. Otherwise walk back a good stretch of `git log --oneline` for **hot spots** — files/areas that keep coming up — and let those pull your attention first; scattered with no clear hot spot → widen the net.

Explore organically, note friction. Look for:

- **Shallow modules** — little **depth**: interface nearly as complex as the implementation. Deletion test: would deleting it concentrate complexity, or just move it? "Concentrates" is the signal.
- Missing **locality** — pure functions extracted for testability, but the real bugs hide in how they're called.
- Low **leverage** — a lot of interface surface buying little behaviour.
- Tightly-coupled modules leaking across their **seams**.
- Untested parts, or parts hard to test through their current interface.
- **Tooling pressure** — places the fulfilled tooling (PHPStan, Rector, style) keeps flagging.

Use `/codebase-design` vocabulary (module, interface, depth, seam, leverage, locality) in the candidate description — not "component," "service," "API."

More than one genuine friction spot → pick the single strongest (same factors as `refactor-prioritize`: heat, leverage, tooling pressure, risk), set the rest aside for a future pass. One selection, one candidate.

### 3. Ground in the candidate

Read the code the candidate names (and, for a resumed candidate, the issue). Read `CONTEXT.md` and the ADRs in the area. Understand *why* it's a candidate before proposing anything.

### 4. Grill toward the seam

Structural candidates only — skip for a tooling-tree node. Run `/grilling` on the candidate, along these branches:

- **The deepened module** — what does it become, what is its one job, what disappears behind it?
- **The seam** — where's the public boundary, tested through what?
- **The interface** — what does it expose, does it stay deep (implementation complexity > interface complexity)?
- **Locality** — what moves together, what must *not* spread?
- **Tests that survive** — which stay, which are rewritten, which new ones appear at the seam?

Side effects happen inline as decisions crystallise (per `/domain-modeling`): naming a module after a concept not in `CONTEXT.md` → add the term. User rejects a design with a load-bearing reason a future scan shouldn't re-suggest → offer an ADR.

### 5. File the issue and write the plan

**Tooling-tree node:** check first whether an issue titled exactly `Tooling tree: <Name>` (never the slug) is already open — that's the issue, don't file a second one (a prior pass got this far and was interrupted). Otherwise file one titled that way, label **`refactor:candidate`**, body = the tree doc's content directly (Purpose, Fulfilment check, MR scope carried over precisely — they're load-bearing, that scope *is* the plan) — never introduced as a quotation or naming the tree doc's file path; it reads as its own plan. Skip `Name:` (already the title); skip `Tool` when `none`.

**Structural candidate:** file an issue labelled **`refactor:candidate`** naming Where (module/files), Problem (the friction, in the project's domain language), Signal (which step-2 friction signal). Capture the plan on that issue: deepened module, seam and interface, surviving tests, slice ordering (see `refactor-implement`).

Either way: set the Refactoring Notes' `config.md`'s `Pending candidates` to this issue (`skills/continuous-refactoring/references/refactoring-config.md`) — lets a future `refactor-scan` resume this exact work if the pass stops here. `refactor-learn` clears it once a merge request exists.

**`loop-config` exception:** chosen node *is* `loop-config` → two differences from an ordinary node's filing. The issue body isn't the tree doc's generic spec — it's the interview's recorded decisions (tracker, create-mode, Refactoring Notes location, each with its one-line rationale) plus the resulting MR scope (create `config.md` with `Create-mode` set; also create `docs/agents/issue-tracker.md` when the interview chose a local tracker). And `config.md` doesn't exist yet, so no `Pending candidates` to write here either — `refactor-implement` records it directly when it creates the file.

The plan follows the foundational refactoring rules (ADR-0004): behavior-preserving, Kent Beck technique vocabulary, Strangler Fig for wide migrations, deterministic tools over hand-applied moves, own branch unless said otherwise.

## Output

The filed issue, carrying the plan → `refactor-implement`.

## Fallback

- **`/codebase-design`**: installed → use its vocabulary for step 2. Otherwise the full vocabulary is already inline in step 2 above.
- **`/grilling`**: installed → use it. Otherwise mechanics (design tree, frontier, rounds) inlined at `skills/refactor-design/references/grilling-fallback.md`.
- **`/domain-modeling`**: installed → use its discipline. Otherwise the same reference file inlines these side effects — already inline in section 4 too, and run regardless of whether this skill is installed.

## Completion criterion

The candidate has an issue (newly filed, or resumed) with a written plan, and `config.md`'s `Pending candidates` names it. Structural: module, seam, interface, surviving tests, slice order — design survives grilling (no open frontier). Tooling tree node: the tree doc's Purpose/Fulfilment check/MR scope, carried onto the issue as its own plan (`loop-config`: the interview's recorded decisions instead — see step 5's exception).
