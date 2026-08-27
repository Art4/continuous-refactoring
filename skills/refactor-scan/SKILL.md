---
name: refactor-scan
description: Propose up to five tooling-tree nodes from config.md/tree state, and detect (never act on) remembered issues or merge requests that have since closed or merged. Part of the continuous refactoring loop.
---

# Refactor Scan

**Detect, never write.** This skill proposes what could be worked on next and notices what has already resolved itself since the last pass — it never files an issue and never decides an outcome. `refactor-design` files issues for what gets chosen; `refactor-learn` acts on what this skill detects.

## Process

### 1. Check preconditions

Before anything else, in order:

- **No git repository?** Stop the pass immediately, report it, propose nothing — git is the suite's only hard requirement.
- **Five or more open `refactor:candidate` issues already?** Stop, propose nothing new — let existing work clear first. This is now a rarer stop than it used to be: since `refactor-design` files at most one issue per pass, this only fires when older issues from interrupted passes are still piling up.

Only past both does a pass propose anything.

### 2. Resume pending work first

Read `docs/refactoring/config.md`'s `Pending issue` field (`skills/continuous-refactoring/references/refactoring-config.md`). If it names an issue, a previous pass's `refactor-design` filed it but the pass was interrupted before `refactor-implement` produced a merge request for it. Propose exactly that issue and stop here — don't also walk the tree this pass. Finishing pending work comes before proposing fresh work.

### 3. Detect closed/merged remembered state

Get the remembered set: every issue labeled `refactor:delivered` when the target's issue tracker natively supports labels (GitHub, GitLab), otherwise every entry in `docs/refactoring/merge-requests.md`. For each, check the external issue tracker/git: is the merge request still open, and is the issue still open?

- Merged → a finding: this candidate is delivered.
- Closed without merge → a finding: this candidate was declined: note whether the closing comments give a maintainer's structural reason (out-of-scope material) or not.
- **Still open, nothing changed** → no finding for this entry.

Hand every finding to `refactor-learn` — this skill only notices; it does not mark anything `done`, `wontfix`, or write to `docs/refactoring/out-of-scope/` itself.

### 4. Propose tooling-tree nodes

Skipped if step 2 already proposed a pending issue.

Run `python3 scripts/lib/tooling_tree.py <target-repo> --steps 5` and read the JSON's `next` field, **not** `roadmap` — `roadmap` simulates forward (it assumes each entry gets fulfilled to compute what would come after it, so entries past the first are a future lookahead, not real options today); `next` is already the real, currently-unblocked set — no further trimming needed, take it as-is (up to five entries):

- **Ordinary tooling nodes** (`loop-config`, and language-specialization nodes from e.g. `docs/php-tooling-tree.md`) — proposed by name; each is already fully specified in its tree doc.
- **`structural-scan`** — proposed once every leaf of the active language tree is resolved (fulfilled, or explicitly rejected under `docs/refactoring/out-of-scope/`). Proposing it is just naming it — no codebase walk happens here (that's `refactor-design`'s job, only for the node actually chosen).
- **No language tree recognized for this target**: `structural-scan`'s gate has no leaves to wait on, so it's immediately proposable on its own.

## Output

Two things, handed onward by the orchestrator — state them plainly, no separate narrative summary:

- Which precondition stopped the pass, if one did (step 1) — then nothing below applies this pass.
- **Findings** (possibly empty) → `refactor-learn`.
- **Proposals**: the pending issue alone, or up to five node names, or none → `refactor-prioritize`.

## Completion criterion

Findings (if any) are handed to `refactor-learn` and proposals (if any) are handed to `refactor-prioritize` — or a precondition stopped the pass and the report says which. Never a node together with entries past `structural-scan` in the same list.
