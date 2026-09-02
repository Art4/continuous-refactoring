# Design Process Reference

Details for structural candidates: codebase walk, grilling, issue filing.

## Structural candidate walk

Walk the commit history (`git log --oneline`) to find hot spots — files that keep coming up. Then explore where you feel friction:

- **Shallow modules** — interface nearly as complex as implementation. Apply deletion test: would deleting it concentrate complexity?
- **Missing locality** — pure functions extracted for testability, but real bugs hide in how they're called.
- **Low leverage** — lots of interface surface, little behaviour behind it.
- **Tightly-coupled modules** leaking across seams.
- **Tooling pressure** — fulfilled tooling keeps flagging things.

Pick the **single strongest** one. Use `codebase-design` vocabulary (module, interface, depth, seam, leverage, locality).

## Grilling toward the seam

Branches to resolve:
1. **The deepened module** — what it becomes, its one job, what disappears behind it.
2. **The seam** — public boundary, tested through what.
3. **The interface** — what it exposes, stays deep (implementation complexity > interface complexity).
4. **Locality** — what moves together, what must not spread.
5. **Tests that survive** — which stay, rewritten, new.

Side effects: add new terms to `CONTEXT.md`, offer ADR when user rejects with a load-bearing reason.

## Issue filing rules

**Tooling-tree node:**
- Title: `Tooling tree: <Name>` (never slug)
- Check if issue already exists first — don't file twice
- Label: `refactor:candidate`
- Body: Purpose, Fulfilment check, MR scope from tree doc (as own plan, not quoted)

**Structural candidate:**
- Label: `refactor:candidate`
- Body: Where (module/files), Problem (friction in domain language), Signal (which friction type)
- Plan: deepened module, seam, interface, surviving tests, slice order

Set `docs/refactoring/config.md`'s `Pending candidates` to this issue.

**`loop-config` exception:** Config file doesn't exist yet — skip `Pending candidates` write; `refactor-implement` handles it.
