---
name: refactor-implement
description: Execute a designed refactor plan test-first, slice by slice, at the agreed seam — review the result, then open the merge request. Part of the continuous refactoring loop.
---

# Refactor Implement

Execute a **plan** (from `refactor-design`) as a series of vertical slices, red → green, at the agreed **seam** — then review the diff and open the merge request. This skill carries what used to be `refactor-review`'s own pass step: the review happens here, before the merge request goes up, not as a separate later step.

Use `/tdd` if installed as the reference for what a good test is and the rules of the red → green loop; otherwise the loop rules and test-quality guidance in `## Fallback` below govern.

Every slice honors the foundational refactoring rules: behavior-preserving only, deterministic tools do the moves they can (code style through the formatter with the repo's ruleset, Rector-reported issues fixed by Rector — never hand-applied by the agent), and the work lives on the refactor's own branch unless the human or the plan says otherwise.

## Process

### 1. Branch, then confirm the seams

Before anything else: create the branch the plan names (or check it out if it already exists — a returning pass, e.g. after a review finding sent this back). No skill before this one creates it; it's this step's job.

Then, for a structural candidate: list the seams the plan names and confirm them with the user. **No test is written at an unconfirmed seam.** Testing at the wrong seam is how refactors produce tests that break under refactoring.

A tooling-tree node's plan has no seam to confirm — its scope is a config/dependency change (see the tree doc's MR scope), not code. Skip straight to making that change; there's no red → green cycle for it, only its Fulfilment check (step 3).

**`loop-config` exception — this node itself:** `refactor-design` couldn't write `Pending issue` (`docs/refactoring/config.md` didn't exist yet). When you create the file here, set `Pending issue` to this candidate's issue yourself. Leave `Last run` and `Create-mode` out (or clearly unset) — don't invent placeholder values for them; per `skills/continuous-refactoring/references/refactoring-config.md` those are `refactor-learn`'s fields, and `refactor-learn` fills them in its own follow-up commit (see its `## Process`).

### 2. One slice at a time

Skipped for a tooling-tree node (step 1 already made its one change directly). For a structural candidate: each slice: write the failing test first (red), then only enough code to pass it (green). One seam, one test, one minimal implementation per cycle. Don't anticipate future slices or add speculative features.

### 3. Verify the loop on completion

For a structural candidate, when the plan's slices are done:

- Run the full test suite — the surviving tests from the plan plus the new seam tests must be green.
- Run the fulfilled tooling (PHPStan, Rector, style) over the touched files — the refactor must not regress mechanical quality.

For a tooling-tree node, there's no test suite standing in judgement — the node's own **Fulfilment check** from the tree doc is the acceptance check. Run or confirm exactly what it specifies (a file exists with the right shape, a command exits clean, whatever the doc says) and treat that as this step's verification.

### 4. Review the diff

Delegate to the `mattpocock/skills` implement skill (`setup-matt-pocock-skills`, `README.md`) if installed — it already embeds review; use it as-is rather than re-deriving a review pass. Otherwise run the two-axis review below.

- **Standards axis** — does the diff conform to this repo's documented standards and the fulfilled tooling?
- **Spec axis** — does it faithfully implement the plan on the candidate issue: requirements missing or partial, behaviour that wasn't asked for (scope creep), requirements that look implemented but wrong?

Findings on either axis send the work back to step 2 (structural) or step 1 (tooling-tree change) — implement, don't hand this off to a separate skill. Report the two axes separately; don't merge or rerank findings across them — one line per finding (file, issue, fix), no prose explanation beyond that.

### 5. Open the merge request

Once review is clean: push the branch and open the merge request (create-mode per `docs/refactoring/config.md`, per the orchestrator's `## Opening a merge request` section). Wait for CI if the target repo runs it; a red CI is a review finding like any other — back to step 2/1.

The candidate branch stays checked out after this — nothing here switches back to the default branch. `refactor-learn`'s bookkeeping writes go out on their own separate bookkeeping branch/MR, never on this one (the `loop-config`-in-flight case is the one exception, which `refactor-learn` handles).

## Output

The opened merge request → `refactor-learn`.

## Fallback

- **`/tdd`**: if installed, use its discipline as the reference for what a good test is and the rules of the loop. Otherwise run the loop by its inline rules. **Rules of the loop:** *red before green* — write the failing test first, then only enough code to pass it, without anticipating future slices or adding speculative features; *one slice at a time* — one seam, one test, one minimal implementation per cycle; *refactoring is not part of the loop* — it belongs to step 4 (review), so no refactoring inside the red → green cycle. **What makes a test worth keeping:** it verifies **behaviour through public interfaces**, not implementation details — the code can change entirely and the test still passes, so it survives the refactor. It must never be **tautological** (the assertion recomputes the expected value the way the code does, so it passes by construction and can never disagree with the code) nor **implementation-coupled** (mocks internal collaborators, tests private methods, or verifies through a side channel).
- **`mattpocock/skills` implement skill**: if installed (per `setup-matt-pocock-skills`), it already embeds the review this step performs — no separate two-axis pass needed. Otherwise run step 4's two axes by these inline rules — this carries the contract `refactor-review` used to own.

  **Standards-axis rules.** Review the diff against the repo's documented coding standards (see `docs/agents/domain.md`, any `CODING_STANDARDS.md`/`CONTRIBUTING.md`). On top of documented standards, carry the Fowler **smell set** below — the fixed set of smells that applies even when the repo documents nothing. Two rules bind it:
  - **The repo overrides.** A documented repo standard always wins; where it endorses something the tooling would flag, suppress the smell.
  - **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation — and, like any standard here, skip anything tooling already enforces.

  Each smell reads *what it is* → *how to fix*; match it against the diff:

  - **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
  - **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
  - **Feature Envy** — a method that reaches into another object's data more than its own. → move the method onto the data it envies.
  - **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
  - **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
  - **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
  - **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
  - **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
  - **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
  - **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
  - **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real target direct.
  - **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

## Completion criterion

The branch exists with the work on it, review is clean on both axes, and a merge request is open (CI green, where the target runs it). For a structural candidate: every slice in the plan is implemented red → green, the full suite is green, and the fulfilled tooling is clean on the touched files. For a tooling-tree node: the change described in its MR scope is made, and its Fulfilment check passes.
