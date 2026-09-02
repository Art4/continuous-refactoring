---
name: refactor-implement
description: Execute a designed refactor plan test-first, slice by slice, at the agreed seam — review the result, then open the merge request.
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

**`loop-config` exception — this node itself:** `refactor-design` couldn't write `Pending candidates` (the Refactoring Notes' `config.md` didn't exist yet). When you create the file here, set `Pending candidates` to this candidate's issue, and set `Create-mode` (and `Focus areas`, only if the candidate issue's recorded decisions name one) from the plan `refactor-design` filed — the interview already decided these, don't leave them unset or invent placeholders. Leave `Fulfilled nodes` out (or clearly unset) — per `skills/continuous-refactoring/references/refactoring-config.md` that field is still `refactor-learn`'s, filled in its own follow-up commit. If the candidate issue's recorded decisions named a local tracker, also create `docs/agents/issue-tracker.md` here, from `skills/continuous-refactoring/references/local-issue-tracker-template.md`. Also write the `Refactoring Notes:` line from the interview's storage-location decision into whichever of `AGENTS.md`/`CLAUDE.md` the interview's Explore step found — never create the other one instead — per `skills/continuous-refactoring/references/loop-config-interview.md`'s `## Record`. All of it in the same merge request as `config.md`, this node's only MR.

### 2. One slice at a time

Skipped for a tooling-tree node (step 1 already made its one change directly). For a structural candidate: before this pass's first test, ensure the target has a test-layout convention on record — `tests/README.md`, if the active language specialization defines one (PHP: `skills/refactor-scan/references/php-tooling-tree/phpunit.md`'s *Test layout*). Missing entirely (even on a target where the test runner was adopted before this convention existed)? Create it with that default. Already there? Read it fresh — never assume the default still matches, a human may have adapted it — and follow it to decide which folder each new test belongs in, creating a documented-but-not-yet-existing folder (and its config entry) only once a test actually needs it, one at a time. No language convention applies? Place tests by your own judgment as before.

Then, each slice: write the failing test first (red), then only enough code to pass it (green). One seam, one test, one minimal implementation per cycle. Don't anticipate future slices or add speculative features.

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

Once review is clean: push the branch and open the merge request (create-mode per the Refactoring Notes' `config.md`, per the orchestrator's `## Opening a merge request` section). Include `Closes #<candidate-issue-number>` in the merge request body **only when this merge request is understood to satisfy the candidate issue's Fulfilment check on its own** — the common case, one node/one issue/one merge request. A node may take more than one merge request to fulfil (e.g. PHPStan-level shrinking work before the next level can be raised); don't add `Closes` to an intermediate merge request in that case — `refactor-learn`'s own early-call behavior (closing the issue once it sees the candidate merged) is the designed fallback, not a gap to work around here.

Wait for CI if the target repo runs it — confirm via the forge's actual CI status (e.g. `gh pr checks` or equivalent), not a local dry-run of the same verification commands from step 3: the CI environment (container image, PHP version, network) can disagree with a local run in ways only the real CI surfaces. A red CI is a review finding like any other — back to step 2/1.

The candidate branch stays checked out after this — nothing here switches back to the default branch. `refactor-learn`'s bookkeeping writes go out on their own separate bookkeeping branch/MR, never on this one (the `loop-config`-in-flight case is the one exception, which `refactor-learn` handles).

## Output

The opened merge request → `refactor-learn`.

## Fallback

- **`/tdd`**: if installed, use its discipline as the reference for what a good test is and the rules of the loop. Otherwise the loop rules and test-quality criteria are inlined at `skills/refactor-implement/references/review-fallback.md`.
- **`mattpocock/skills` implement skill**: if installed (per `setup-matt-pocock-skills`), it already embeds the review this step performs — no separate two-axis pass needed. Otherwise run step 4's two axes by the standards-axis rules (repo standards plus a fixed Fowler smell set) inlined at the same `skills/refactor-implement/references/review-fallback.md` — this carries the contract `refactor-review` used to own.

## Completion criterion

The branch exists with the work on it, review is clean on both axes, and a merge request is open (CI green, where the target runs it). For a structural candidate: every slice in the plan is implemented red → green, the full suite is green, and the fulfilled tooling is clean on the touched files. For a tooling-tree node: the change described in its MR scope is made, and its Fulfilment check passes.
