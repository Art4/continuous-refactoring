---
name: refactor-scan
description: Propose every currently-unblocked tooling-tree node from config.md/tree state, and detect (never act on) remembered issues or merge requests that have since closed or merged.
---

# Refactor Scan

**Detect, never write.** Proposes what could be worked on next and notices what has resolved itself. Never files issues, never decides outcomes.

## Process

### 1. Preconditions

- **No git?** Stop immediately.
- **5+ open `refactor:candidate` issues?** Stop — let existing work clear.

### 2. Resume pending work

Read `docs/refactoring/config.md`'s `Pending candidates`. If it names an issue, propose exactly that and stop.

### 3. Detect closed/merged state

Check every remembered `refactor:delivered` issue (or `docs/refactoring/merge-requests.md` entry) against the external tracker/git:
- Merged → finding
- Closed without merge → finding
- Still open with reviewer activity newer than last commit → **resume-candidate** → straight to `refactor-implement`
- Still open, nothing changed → nothing

No `gh`/`glab`? Fall back to git-only: `git merge-base --is-ancestor` for merged, `git ls-remote` for branch presence. See `references/scan-fallback.md`.

### 4. Propose nodes

Run `python3 skills/refactor-scan/references/tooling_tree.py <target-repo>` and read `next` (currently unblocked), `withheld` (waiting on recommended parents). No python3? Use `skills/refactor-scan/references/tree-walk-prompt.md` with `{N}=all`.

Propose by **Name** (never slug). `structural-scan` is proposed when all resolved parents are resolved.

## Output

- Precondition stop → nothing else applies
- **Findings** → `refactor-learn`
- **Resume-candidate** → `refactor-implement`
- **Proposals** (every unblocked node) + **withheld** (waiting nodes) → `refactor-prioritize`

## Completion criterion

Findings handed off, resume-candidate (if any) forwarded, proposals (if any) handed to prioritise — or a precondition stopped the pass.
