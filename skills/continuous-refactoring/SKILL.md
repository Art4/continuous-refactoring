---
name: continuous-refactoring
description: Run one pass of the continuous refactoring loop — propose, prioritise, design, implement, learn. Use to keep a codebase under continuous refactoring, on demand or via your own recurring trigger.
disable-model-invocation: true
---

# Continuous Refactoring

The **loop pass** — the stateful, repeatable sequence that keeps a project under continuous refactoring. Each pass does only the work due since the last pass, then records what it learned so the next pass starts from state, not from zero.

This skill is a thin data pipe: it calls each lifecycle skill in order and carries that skill's output forward as the next skill's input. It does not read shared state itself and does not decide anything a lifecycle skill could decide — `refactor-scan` detects, `refactor-prioritize` and `refactor-design` decide, `refactor-implement` executes, `refactor-learn` writes. If you're tracing a bug in the loop, look in the lifecycle skill responsible for that decision, not here.

A completed candidate is delivered as a **merge request** remembered in the target repo; later passes react to that state. Git is the only hard requirement — missing tools enter the language's **tooling tree** as small candidates instead of gating the loop. A **required edge** gates a child until every required parent is fulfilled; a **recommended edge** only advises — the child stays proposable even when the recommended parent was rejected.

Run this on demand whenever you're asked, or via whatever recurring trigger you've set up outside the suite — the loop has no stored schedule of its own; it does the same one pass regardless of how often it's invoked.

## Loop state

State lives in the target repo, not in the conversation — every lifecycle skill may read these directly; only `refactor-learn` writes them:

- **Config** — `docs/refactoring/config.md`: last-run date, focus areas, merge-request create-mode, and the `Pending issue` marker (`skills/continuous-refactoring/references/refactoring-config.md`)
- **Remembered merge requests** — which suite merge requests are open. When the target's issue tracker natively supports labels (GitHub, GitLab): every issue labeled `refactor:delivered` — its merge request, base branch, and (from the issue's title) tooling-tree node come straight from the tracker, no file. Otherwise: `docs/refactoring/merge-requests.md`, a committed ledger holding the same facts (URL, candidate issue, tooling-tree node if any, base branch)
- **Backlog** — `refactor:*` issues on the issue tracker (see `docs/agents/issue-tracker.md`)
- **Learned rejections** — `docs/refactoring/out-of-scope/` entries from prior passes

`docs/refactoring/config.md` is not scaffolded here directly: it's `loop-config`, an ordinary tooling-tree node like any other — `refactor-scan` proposes it, `refactor-design` files it, `refactor-implement` creates the file, same path as any other node.

## The pass

Each numbered step runs the named lifecycle skill and carries its output to the next step. Stop between steps where the skill itself stops for user input.

1. **Scan.** Run `/refactor-scan`. It checks its own preconditions first — git, backlog size — and resumes any `Pending issue` before proposing anything fresh. Two outcomes end the pass here, before anything else runs: no git repository (nothing else runs, not even step 5), or the backlog is already full (skip to step 5 with whatever findings scan reported, no new candidate this pass). Every other outcome carries scan's **findings** (closed/merged issues or MRs, possibly empty) into step 2 and **proposals** (the resumed pending issue, or up to five node names) into step 3.

2. **Learn, early call — findings only.** If step 1 produced any findings, run `/refactor-learn` on them now, before prioritising — it resolves each one (`done` / `wontfix` + out-of-scope entry) and updates the ledger immediately. This can't wait until step 5: step 3 reads the ledger to decide whether two merge requests are already open, and a finding scan just made (a remembered one merged or closed) has to be reflected there first, or step 3 would count a slot as occupied that this pass itself just freed. Skip this call entirely when step 1 had no findings — it is not a bookkeeping-only pass by itself, just an early half of one.

3. **Prioritise.** Run `/refactor-prioritize` on scan's proposals, against the now-current ledger. It stops the pass here (skip to step 5) if two suite merge requests are already open, or if every proposal is already in flight. Otherwise it hands one chosen node forward with its rationale.

4. **Design.** Run `/refactor-design` on the chosen node. It files the node as an issue (the point at which a node first becomes one) and writes the plan onto it. If the candidate is tiny and the user wants to skip ahead, that's their call — flag it, don't block. Carries the filed issue/plan into step 5.

5. **Implement.** Run `/refactor-implement`. One candidate, one branch; slices stay on that branch, and the branch only exists once this step creates it. It reviews its own diff along both axes (the check that used to be `refactor-review`'s own step) until clean — the change it describes matches what the plan asked for — before opening the merge request, looping back to its own earlier steps on findings rather than handing off to another skill. Carries the opened merge request into step 6.

6. **Learn, closing call.** Run `/refactor-learn` with the freshly opened merge request (if step 5 ran) — this call always happens, even when nothing past step 3 did (a pass that only did step 2's early reconciliation is still a complete pass). It records the merge request in the ledger with the `refactor:delivered` label, clears `Pending issue`, captures ADRs/`CONTEXT.md` updates, and stamps `Last run`, unconditionally, last. `refactor-learn` is the only skill that writes any of the state listed above — across both calls in a pass, never more than twice.

## Opening a merge request

Followed by `refactor-implement` when it opens the reviewable; the create-mode decision itself is recorded into `docs/refactoring/config.md` by `refactor-learn`.

- Read the target repo's `AGENTS.md` / `CLAUDE.md` first. If either names a mode, follow it.
- Neither does → propose `autonomous` for this merge request; `refactor-learn` records the chosen mode — `autonomous`, `ask-each-time`, or `human-opens` — the first time it's decided. `refactor-learn` follows this same policy for its own bookkeeping merge request (see its `## Process`).
- Skills always say **merge request**; conversation with the human uses the forge's native word (pull request on GitHub, merge request on GitLab).

While fewer than two suite merge requests are open, a pass may deliver one more. Stack it (base = the open branch) only when the new candidate is a tooling-tree child of what is in flight or the design depends on it; otherwise branch parallel off the default branch. After the parent merges, the next pass retargets or rebases the child.

The description opens in plain language, one or two sentences, for a human who doesn't know the suite's vocabulary: what this unlocks for the project, not what tree node it fulfils. Then the plain facts: link the candidate, what changed, which tests survive, what CI proves.

For a tooling-tree candidate, close with an outlook: re-run `python3 skills/refactor-scan/references/tooling_tree.py <target-repo> --steps 1` against the now-changed working tree and name whatever node it reports next, quoting that node's Purpose from the tree doc in one line. If `python3` isn't available or running it isn't permitted, dispatch a sub-agent with `skills/refactor-scan/references/tree-walk-prompt.md`'s prompt (`{N}=1`) instead; with no sub-agent mechanism, run that prompt's steps yourself inline. A structural candidate carries no outlook — there's no single "next child" a deepening unlocks the way a tree node does. No type enum — outlook is settled, a type enum is a separate, still-undecided question.

## Fallback

The suite must keep working in a target repo with none of the global skills installed. Each lifecycle skill self-contains its own step: its own `## Fallback` section means "use the global skill if installed, else the inline fallback". Two fallback depths apply: **crash-safe** means skip the global skill with a note — the step's core is already inline; **self-sufficient** means the fallback inlines the part of the global skill the step uses. The orchestrator engages no global skill itself — that one reference now lives in `refactor-learn`, which owns the learn step — every fallback lives in the lifecycle skill that uses it: `refactor-design`, `refactor-implement`, and `refactor-learn` each carry their own, per their `## Fallback` sections.

The authoritative inventory of every global reference and its fallback type lives in `docs/agents/skill-references.md` and is enforced by the Tier 1 validator (`scripts/validate_skills.py`) — that ledger, not this section, is the one place naming which global skill backs which step.

## Completion criterion

One full pass completed and the loop state updated — `refactor-learn` ran at least once (even a bookkeeping-only pass), `Last run` is stamped, and the pass's own outcome is recorded: the delivered candidate sits `refactor:delivered` with its merge request remembered, or the issue closed, or nothing was actionable this pass and that's reported.
