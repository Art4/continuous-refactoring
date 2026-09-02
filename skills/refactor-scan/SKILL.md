---
name: refactor-scan
description: Propose every currently-unblocked tooling-tree node from config.md/tree state, and detect (never act on) remembered issues or merge requests that have since closed or merged.
---

# Refactor Scan

**Detect, never write.** Proposes what could be worked on next and notices what has already resolved itself since the last pass — never files an issue, never decides an outcome. `refactor-design` files issues for what gets chosen; `refactor-learn` acts on what this skill detects.

## Process

### 1. Check preconditions

- No git repository → stop the pass, report it, propose nothing.
- Five or more open `refactor:candidate` issues → stop, propose nothing new; let existing work clear first.

### 2. Resume pending work first

Read the Refactoring Notes' `config.md`'s `Pending candidates` field (`skills/continuous-refactoring/references/refactoring-config.md`). If it names an issue, a prior pass's `refactor-design` filed it but was interrupted before a merge request followed. Propose exactly that issue and stop — finishing pending work comes before proposing fresh work.

### 3. Detect closed/merged remembered state

Get the remembered set — every issue labeled `refactor:delivered` when `docs/agents/issue-tracker.md` names a native-label tracker (GitHub, GitLab), otherwise every entry in the Refactoring Notes' `merge-requests.md`. For each, check the external tracker/git: is the MR still open, is the issue still open?

No `gh`/`glab` (or other forge API/token) available → fall back to git-only reconciliation instead of skipping this step (never attempt to install `gh`/`glab` here either — treat their absence as exactly this fallback's trigger): `skills/refactor-scan/references/git-only-reconciliation.md`.

- **Merged** → a finding: delivered.
- **Closed without merge** → a finding: declined — note whether closing comments give a maintainer's structural reason (out-of-scope material) or not.
- **Still open, with reviewer activity (a review or comment) newer than the branch's last commit** → a **resume-candidate**, not a finding — nobody has decided anything yet, it just needs another look. Hand it forward the same way step 2 hands forward a `Pending candidates` entry: straight to `refactor-implement`, skipping `refactor-prioritize`/`refactor-design` (it already has a design and an open MR; only the fix loop applies — `refactor-implement` step 1 already supports resuming an existing branch).
- **Still open, nothing changed** → no finding.

Also check every entry in the Refactoring Notes' `out-of-scope/<node>.md` naming a `**Blocked by:** PHP >= X.Y` condition (`tooling_tree.py`'s `detect_nodes()` reports this directly when run; by hand, compare against the target's current `composer.json` `require.php`/`config.platform.php`) — if the target's current PHP version now satisfies it, a finding: this rejection is reversed. No `Blocked by:` field, or condition still unmet → never a finding.

Hand every finding to `refactor-learn` — this skill only notices; it never marks anything `done`/`wontfix` and never writes to the Refactoring Notes' `out-of-scope/` itself.

### 4. Propose tooling-tree nodes

Skip if step 2 already proposed a pending candidate.

Run `python3 skills/refactor-scan/references/tooling_tree.py <target-repo>` and read the JSON's `next` field — the real, currently-unblocked set, rejected nodes (an existing entry in the Refactoring Notes' `out-of-scope/<node>.md`) already excluded, take as-is however many entries it holds. **Not** `roadmap` (a forward simulation, not real options today). Also read `withheld`: nodes that would otherwise be in `next` but wait on an undecided recommended parent — each entry names which parent(s). No `python3`, or not permitted → dispatch a sub-agent with `skills/refactor-scan/references/tree-walk-prompt.md`'s prompt (`{N}=all`) — it walks the same tree docs by hand (reads the Refactoring Notes' `config.md`'s `Fulfilled nodes` first to skip re-deriving cached state, skips any node with an out-of-scope entry); no sub-agent mechanism → run its steps yourself inline.

- **Ordinary tooling nodes** (`loop-config`, and language-specialization nodes, e.g. `skills/refactor-scan/references/php-tooling-tree.md`) — proposed by their **Name** (never the raw slug); each is already fully specified in its tree doc.
- **`structural-scan`** — proposed once every node with a `resolved` edge into it is resolved (fulfilled, or explicitly rejected under the Refactoring Notes' `out-of-scope/`): `editorconfig` at the generic root, plus the active language specialization's own aggregation node (PHP: `php-structural-scan`), itself resolved once every one of its own resolved-parents is resolved (`skills/refactor-scan/references/tooling-tree.md`). Only `structural-scan` is ever proposed this way — `php-structural-scan` is pure plumbing, never a candidate. Proposing it is just naming it; the codebase walk happens in `refactor-design`, only for the node actually chosen.
- **No language tree recognized**: `structural-scan` still waits on `editorconfig`, the generic-root leaf — not immediately proposable just because no language-specific tree applies.

## Output

Handed onward by the orchestrator, plainly:

- Which precondition stopped the pass, if one did — nothing below applies this pass.
- **Findings** (possibly empty) → `refactor-learn`.
- **A resume-candidate**, if one was detected → straight to `refactor-implement`, bypassing `refactor-prioritize`/`refactor-design`.
- **Proposals** — the pending candidate alone, or every currently-unblocked node's Name (never slugs, never capped), or none → `refactor-prioritize`. Every node currently unblocked (required parents fulfilled, not rejected, every recommended parent already decided) — never a priority-truncated subset. Alongside it, name every `withheld` node and which parent(s) it's waiting on (e.g. "Rector: Type Coverage Set — waiting on: PHP CS Fixer").

## Completion criterion

Findings (if any) handed to `refactor-learn`, a resume-candidate (if any) handed straight to `refactor-implement`, proposals (if any) handed to `refactor-prioritize` — or a precondition stopped the pass and the report says which. Never a node together with entries past `structural-scan` in the same list.
