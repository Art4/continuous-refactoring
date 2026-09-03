---
name: continuous-refactoring
description: Run one pass of the continuous refactoring loop — propose, prioritise, design, implement, learn. Use to keep a codebase under continuous refactoring, on demand or via your own recurring trigger.
disable-model-invocation: true
---

# Continuous Refactoring

One **loop pass**: does only the work due since the last pass, then records what it learned so the next pass starts from state, not from zero.

This skill is a thin data pipe: it calls each lifecycle skill in order and carries that skill's output forward as the next skill's input. It decides nothing a lifecycle skill could decide — `refactor-scan` detects, `refactor-prioritize`/`refactor-design` decide, `refactor-implement` executes, `refactor-learn` writes.

A completed candidate is delivered as a **merge request** remembered in the target repo. Git is the only hard requirement — missing tools enter the language **tooling tree** as small candidates instead of gating the loop. A **required edge** gates a child until every required parent is fulfilled; a **recommended edge** only advises — the child stays proposable even when the recommended parent was rejected.

Run this on demand, or via your own recurring trigger — the loop has no schedule of its own.

## Loop state

State lives in the target repo, not the conversation. Every lifecycle skill reads it directly; each writes only the field its own step produces (`refactor-design` files backlog issues and sets `Pending candidates`; `refactor-implement` sets `Create-mode` while delivering `loop-config`) — `refactor-learn` writes everything else, and is the suite's only *dedicated* bookkeeping writer:

- **Config** — the Refactoring Notes' `config.md`: focus areas, merge-request create-mode (decided once, during `loop-config`'s own interview — see `## Opening a merge request`), `Pending candidates`, `Fulfilled nodes` cache, `Skip streak` (`skills/continuous-refactoring/references/refactoring-config.md`).
- **Remembered MRs** — every issue labeled `refactor:delivered`, when `docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab); otherwise the Refactoring Notes' `merge-requests.md`, a committed ledger with the same facts.
- **Backlog** — `refactor:*` issues on the tracker named by `docs/agents/issue-tracker.md` — scaffolded once, during `loop-config`'s own interview (`skills/continuous-refactoring/references/loop-config-interview.md`); every place that needs "does the tracker support native labels" reads this file rather than re-deriving it from `gh`/`glab`.
- **Learned rejections** — the Refactoring Notes' `out-of-scope/` entries.

The Refactoring Notes' `config.md` isn't scaffolded here — it's `loop-config`, a tooling-tree node like any other except one thing: `refactor-scan` proposes it, but `refactor-design` runs a human interview instead of copying the tree doc's generic spec, and `refactor-implement` creates the file with `Create-mode` already set from that interview, not left for `refactor-learn` to fill in later.

## The pass

Each step runs the named lifecycle skill and carries its output to the next. Stop between steps where the skill itself stops for user input.

Prefer dispatching each step to a fresh subagent: hand it this pass's carried-forward input, bring back only its stated `## Output`. That keeps a skill's own reasoning inside its own context instead of leaking into the orchestrator's. No subagent mechanism available → run each step inline instead, same order.

1. **Scan.** Run `/refactor-scan` — checks preconditions (git, backlog size) and resumes `Pending candidates` before proposing anything fresh.
   - No git repository → pass ends now, nothing else runs (not even step 6).
   - Backlog full → skip to step 5 with scan's findings, no new candidate.
   - Resume-candidate (an open MR with reviewer activity newer than its last commit) → skip straight to step 5 with it; steps 2–4 don't run.
   - Otherwise → **findings** (possibly empty) go to step 2, **proposals** (every unblocked node's Name, never slugs) go to step 3.

2. **Learn, early call — only if step 1 found something.** Run `/refactor-learn` on the findings before prioritising: step 3 reads the ledger, and a finding this pass just resolved (an MR merged or closed) must land there first. No findings → skip this call entirely.

3. **Prioritise.** Run `/refactor-prioritize` on scan's proposals against the now-current ledger. Stops the pass (skip to step 5) if two suite MRs are already open, or every proposal is already in flight. Otherwise hands forward one chosen node with its rationale.

4. **Design.** Run `/refactor-design` on the chosen node — files it as an issue (its first time becoming one) and writes the plan onto it. Carries the filed issue/plan to step 5.

5. **Implement.** Run `/refactor-implement` — one candidate, one branch, created here. Reviews its own diff (standards + spec) until clean, looping back to its own earlier steps on findings, before opening the merge request. Carries the opened MR to step 6.

6. **Learn, closing call — always**, even when nothing past step 3 ran (a pass that only did step 2 is still complete). Run `/refactor-learn` with the freshly opened MR, if any. Records it in the ledger with `refactor:delivered`, clears `Pending candidates`, captures ADR/`CONTEXT.md` updates, writes `Fulfilled nodes` last.

## Opening a merge request

Followed by `refactor-implement` when it opens the reviewable, and by `refactor-learn` for its bookkeeping MR. Full rules — create-mode (decided once, via `loop-config`'s own interview), stacking, description, outlook — in `skills/continuous-refactoring/references/opening-a-merge-request.md`.

## Fallback

The suite must keep working in a target repo with none of the global skills installed. Each lifecycle skill's own `## Fallback` covers its step: **crash-safe** (skip the global skill with a note — the step's core is already inline) or **self-sufficient** (the fallback inlines the part of the global skill the step uses). The orchestrator engages no global skill itself.

## Closing report

Wherever the pass ends, close with exactly two lines to the human — a lifecycle skill's own `## Output` is handoff data for the *next skill*, separate from this. Name any tooling-tree node by its Name, never its slug.

- **Status:** one line, what happened this pass.
- **Next:** one line, what the human can or should do now.

Examples: "Status: no git repository found — the loop can't run here. Next: initialize git, then rerun." / "Status: 2 merge requests already open (links). Next: review/merge one; nothing else to do until then." / "Status: delivered PHPStan Level 0 — merge request #12 open. Next: review and merge; the following pass proposes PHPStan Level 1 once this lands." / "Status: Refactoring Config prepared on local branch `refactor/loop-config` — no forge/remote here, so nothing was pushed. Next: commit it yourself, or push it and open the merge request once you have forge access."

## Completion criterion

One full pass completed and loop state updated: `refactor-learn` ran at least once, `Fulfilled nodes` is written, and the pass's outcome is recorded — a delivered candidate sits `refactor:delivered` with its MR remembered, the issue closed, nothing was actionable and that's reported, or (no forge/remote available) the candidate sits prepared on its own branch, handed to the human, per `opening-a-merge-request.md`.
