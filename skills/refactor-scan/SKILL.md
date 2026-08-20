---
name: refactor-scan
description: Find refactoring candidates in the codebase and file them on the issue tracker as `refactor:candidate` issues. Part of the continuous refactoring loop.
---

# Refactor Scan

Find **candidates** — places where refactoring would pay off — and file them on the issue tracker so they enter the **backlog**. Scanning is what makes the loop *continuous*: every pass re-looks and catches what the last one missed.

Read the project's domain glossary (`CONTEXT.md`) and ADRs in the areas you touch first, so candidate descriptions use the project's own language.

## Process

### 1. Scope before you scan

Decide *where* to look before you look:

- If the user named a direction — a module, a subsystem, a pain point — take it and skip the inference below.
- Otherwise walk back a good stretch of the commit history (`git log --oneline`) to find the **hot spots** — files and areas that keep coming up — and let those paths pull your attention first. If changes are scattered with no clear hot spot, widen the net.

### 2. Walk the codebase

Explore organically and note where you experience friction. Look for:

- **Shallow modules** — interface nearly as complex as the implementation. Apply the **deletion test**: would deleting it concentrate complexity, or just move it? A "concentrates" is the signal you want.
- Missing **locality** — pure functions extracted for testability, but the real bugs hide in how they're called.
- Tightly-coupled modules leaking across their **seams**.
- Untested parts, or parts hard to test through their current interface.
- **Tooling pressure** — places the baseline tools (PHPStan, Rector, style) keep flagging.

Use the `/codebase-design` vocabulary (module, interface, depth, seam, leverage, locality) in every candidate description — don't drift into "component," "service," or "API."

### 3. File candidates

For each candidate, create an issue on the issue tracker (see `docs/agents/issue-tracker.md`) with the label **`refactor:candidate`** and a body that names:

- **Where** — module or files involved
- **Problem** — the friction, in the project's domain language
- **Signal** — which of the friction signals above it came from

Keep each candidate a single coherent refactoring — not a grab-bag. If a scan turns up an outright bug, route it to the normal bug path, not the refactor backlog.

### 4. Report

Summarise: how many candidates filed, where, and the top 2-3 you'd look at first (and why). Then stop — prioritising is `refactor-prioritize`'s job.

## Fallback

- **`/codebase-design`**: if installed, use its vocabulary. Otherwise, the vocabulary is fully inline in section 2 above — module, interface, depth, seam, leverage, locality — use those terms and don't drift into "component", "service", or "API".

## Completion criterion

Every genuine candidate found during the walk is filed as a `refactor:candidate` issue with Where / Problem / Signal, and the report lists the top candidates.