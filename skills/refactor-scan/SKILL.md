---
name: refactor-scan
description: Propose every currently-unblocked tooling-tree node from config.md/tree state, and detect (never act on) remembered issues or merge requests that have since closed or merged.
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

Read `docs/refactoring/config.md`'s `Pending candidates` field (`skills/continuous-refactoring/references/refactoring-config.md`). If it names an issue, a previous pass's `refactor-design` filed it but the pass was interrupted before `refactor-implement` produced a merge request for it. Propose exactly that issue and stop here — finishing pending work comes before proposing fresh work.

### 3. Detect closed/merged remembered state

Get the remembered set: every issue labeled `refactor:delivered` when `docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab), otherwise every entry in `docs/refactoring/merge-requests.md`. For each, check the external issue tracker/git: is the merge request still open, and is the issue still open?

(Whether `docs/agents/issue-tracker.md` names a native-label tracker only changes *where* a merge request's record lives — tracker labels vs. `docs/refactoring/merge-requests.md` — never *whether* `refactor-implement` opened a real one. Don't read "names no native-label tracker" as "no real merge request exists to reconcile" — a target with forge push access still has real ones, this step just needs a different way to check their status below.)

**No `gh`/`glab` (or other forge API/token) available** — common on a target with no CLI or credentials configured, real MRs opened by pushing directly rather than through the API. Fall back to git-only reconciliation instead of skipping this step:

- **Merged:** `git fetch origin <candidate-branch>` (if still present), then `git merge-base --is-ancestor <candidate-branch-or-its-last-known-sha> origin/<default-branch>` exits `0`.
- **Still open, unmerged:** the branch is still present (`git ls-remote --exit-code --heads origin <candidate-branch>` exits `0`) and the merge-base check above is not an ancestor. Without API access there's no reviewer-comment/review-state signal to check for "newer activity" — report it as "still open, no activity signal available without API access" rather than guessing at review state; never invent a resume-candidate from git state alone.
- **Closed without merge:** the branch is gone (`git ls-remote --exit-code --heads origin <candidate-branch>` exits `2`) and its last known SHA (from the ledger/issue) is not an ancestor of the default branch. No maintainer comment text is available this way — hand it to `refactor-learn` as a finding with no closing-comment signal; its own early-call rule ("otherwise ask the human what to do before deciding") already covers a finding with no structural reason attached, so this triggers the same path, just from git evidence instead of read comments.

- Merged → a finding: this candidate is delivered.
- Closed without merge → a finding: this candidate was declined: note whether the closing comments give a maintainer's structural reason (out-of-scope material) or not.
- **Still open, with reviewer activity (a review requesting changes, or a comment) newer than the candidate branch's last commit** → a resume-candidate, not a finding for `refactor-learn` (it doesn't fit any of `refactor-learn`'s existing outcomes — done, wontfix, or a reversed rejection — nobody has decided anything yet, the candidate just needs another look). Hand it forward the same way step 2 hands forward a `Pending candidates` entry: straight to `refactor-implement`, skipping `refactor-prioritize`/`refactor-design` — the candidate already has a design and an open merge request, only the fix loop applies. (`refactor-implement` step 1 already supports resuming an existing branch — "a returning pass, e.g. after a review finding sent this back" — this is the same shape, just discovered by a fresh pass instead of the same one.)
- **Still open, nothing changed** → no finding for this entry.

Also check every `docs/refactoring/out-of-scope/<node>.md` that names a `**Blocked by:** PHP >= X.Y` condition (`tooling_tree.py`'s `detect_nodes()` reports this directly when run; walking by hand, compare it against the target's current `composer.json` `require.php`/`config.platform.php`) — if the target's current PHP version now satisfies it, a finding: this rejection is reversed. A rejection with no `Blocked by:` field, or one whose condition still isn't met, is never a finding here.

Hand every finding to `refactor-learn` — this skill only notices; it does not mark anything `done`, `wontfix`, or write to `docs/refactoring/out-of-scope/` itself (removing a reversed entry is `refactor-learn`'s write, not this step's).

### 4. Propose tooling-tree nodes

Skipped if step 2 already proposed a pending candidate.

Run `python3 skills/refactor-scan/references/tooling_tree.py <target-repo>` and read the JSON's `next` field, **not** `roadmap` — `roadmap` simulates forward (it assumes each entry gets fulfilled to compute what would come after it, so entries past the first are a future lookahead, not real options today); `next` is already the real, currently-unblocked set, with rejected nodes (an existing `docs/refactoring/out-of-scope/<node>.md`) already excluded — no further trimming needed, take it as-is, however many entries it holds (never capped). Also read the JSON's `withheld` field: nodes that would otherwise be in `next` but stay held back because a recommended parent hasn't yet been decided (fulfilled or rejected) — each entry names which parent(s) it's waiting on. If `python3` isn't available or running it isn't permitted, dispatch a sub-agent with `skills/refactor-scan/references/tree-walk-prompt.md`'s prompt (`{N}=all`) instead — it walks the same tree docs by hand (reading `docs/refactoring/config.md`'s `Fulfilled nodes` first to skip re-deriving what's already cached, and skipping any node with an `out-of-scope` entry the same way the parser does) and returns the same two sets; with no sub-agent mechanism, run that prompt's steps yourself inline.

- **Ordinary tooling nodes** (`loop-config`, and language-specialization nodes from e.g. `skills/refactor-scan/references/php-tooling-tree.md`) — proposed by their **Name** (the tree doc's `**Name:**` field, never the raw slug); each is already fully specified in its tree doc.
- **`structural-scan`** — proposed once every node with a `resolved` edge into it is resolved (fulfilled, or explicitly rejected under `docs/refactoring/out-of-scope/`): `editorconfig` at the generic root, plus the active language specialization's own aggregation node (PHP: `php-structural-scan`), itself resolved once every one of *its* resolved-parents — the language tree's real leaves — is resolved (`skills/refactor-scan/references/tooling-tree.md`). Only `structural-scan` is ever proposed this way; `php-structural-scan` is pure plumbing, never itself a candidate. Proposing `structural-scan` is just naming it (by its Name) — no codebase walk happens here (that's `refactor-design`'s job, only for the node actually chosen).
- **No language tree recognized for this target**: `structural-scan` still has `editorconfig` — the generic-root leaf declared in `skills/refactor-scan/references/tooling-tree.md`'s own edge table — to wait on; it isn't immediately proposable purely because no language-specific tree applies.

## Output

Two things, handed onward by the orchestrator — state them plainly, no separate narrative summary:

- Which precondition stopped the pass, if one did (step 1) — then nothing below applies this pass.
- **Findings** (possibly empty) → `refactor-learn`.
- **A resume-candidate** (step 3's new case), if one was detected → straight to `refactor-implement`, same as a resumed `Pending candidates` — bypasses `refactor-prioritize`/`refactor-design` this pass.
- **Proposals**: the pending candidate alone, or every currently-unblocked node's Name (never slugs, never capped at some fixed count), or none → `refactor-prioritize`. The proposal set names **every** node currently unblocked (required parents fulfilled, not rejected, and — for a node with one or more recommended parents — every one of those already decided, fulfilled or rejected) — never a priority-truncated subset silently standing in for "the rest weren't ready yet." Alongside it, name every node the `withheld` set holds back and which parent(s) it's still waiting on (e.g. "Rector: Type Coverage Set — waiting on: PHP CS Fixer") — without this, a withheld node would just look like a scan gap instead of a decision pending on its recommended parent.

## Completion criterion

Findings (if any) are handed to `refactor-learn`, a resume-candidate (if any) is handed straight to `refactor-implement`, and proposals (if any) are handed to `refactor-prioritize` — or a precondition stopped the pass and the report says which. Never a node together with entries past `structural-scan` in the same list.
