---
name: refactor-learn
description: The suite's only writer of bookkeeping — acts on refactor-scan's reconciliation findings and refactor-implement's freshly opened merge request, records the ledger, ADRs, CONTEXT.md, and the last-run stamp.
---

# Refactor Learn

The only skill that writes suite bookkeeping: ledger, `config.md`, ADRs, `CONTEXT.md`, issue labels, out-of-scope entries. Every other lifecycle skill reads; only this one writes.

Called up to **twice** per pass: **early call** (only when scan had findings) and **closing call** (always).

**All writes go through a dedicated bookkeeping branch/MR** — never a direct commit. See `references/bookkeeping-branch.md` for branch-finding logic.

## Process

### Early call — findings only

For each finding from scan:
- **Merged** → mark `done`, close issue
- **Closed without merge** → if maintainer gave structural reason: mark `wontfix`, close issue, file `out-of-scope/<node>.md`. Otherwise ask human. If reason is PHP version, add `**Blocked by:** PHP >= X.Y`.
- **PHP-version reversal** → existing out-of-scope entry with `Blocked by:` now satisfied → remove that file.
- Drop from `merge-requests.md` if applicable.

A bookkeeping-only pass (no fresh candidate) is still complete.

### Closing call — always

Given a freshly opened MR (if any):
- Remember it: `refactor:delivered` label (GitHub/GitLab) or `merge-requests.md` entry
- Clear `Pending candidates` in `config.md`
- Label candidate `refactor:delivered` (not `done`, not `ready-for-human`)
- Record `Create-mode` if not set before

Then, using the bookkeeping branch:
- Record ADR for decisions future scans must not re-litigate
- Update `CONTEXT.md` with terms that crystallised
- Write `Fulfilled nodes` — overwrite completely when parser ran, additive on fallback
- Write `Skip streak` alongside — increment unchosen required nodes, drop chosen ones

**`loop-config` exception:** before it merges, writes land on `loop-config`'s own branch instead of a separate bookkeeping branch.

## Fallback

`/domain-modeling`: if installed, use for ADR/CONTEXT.md. Otherwise skip — ledger, label, and stamp writes run regardless.

## Completion criterion

**Early:** every finding resolved, ledger updated before prioritise runs, writes via bookkeeping MR.
**Closing:** MR remembered, `Pending candidates` cleared, `Fulfilled nodes` + `Skip streak` written, all via bookkeeping MR.
