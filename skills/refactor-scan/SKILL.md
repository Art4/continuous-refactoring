---
name: refactor-scan
description: Find refactoring candidates in the codebase and file them on the issue tracker as `refactor:candidate` issues. Part of the continuous refactoring loop.
---

# Refactor Scan

Find **candidates** — places where refactoring would pay off — and file them on the issue tracker so they enter the **backlog**. Scanning is what makes the loop *continuous*: every pass re-looks and catches what the last one missed.

Read the project's domain glossary (`CONTEXT.md`) and ADRs in the areas you touch first, so candidate descriptions use the project's own language.

## Process

### 1. Check preconditions

Before anything else, in order:

- **No git repository?** Stop the pass immediately, report it, and file nothing — git is the suite's only hard requirement (ADR-0005, ADR-0008).
- **`docs/refactoring/config.md` missing?** Check the open backlog first (see `docs/agents/issue-tracker.md`) for an issue titled `Tooling tree: loop-config`. Found one → report it and stop; it hasn't been merged, rejected, or otherwise resolved yet, so don't file a second one. None found → file exactly that one candidate (the `loop-config` node — see `docs/tooling-tree.md`, and step 4 for the issue shape) and stop. Either way, nothing else runs this pass.
- **Five or more open `refactor:candidate` issues already?** Stop without filing anything new; let `refactor-prioritize` work through the existing backlog first.

Only past all three does a pass actually scan.

### 2. Check the tooling tree

Run `python3 scripts/lib/tooling_tree.py <target-repo> --steps 1` and read the next proposed node:

- **A tooling node** (from `docs/php-tooling-tree.md`, or a future language specialization's tree): same duplicate check as above — an open issue titled `Tooling tree: <node>` already? Report it and stop; the tree only ever proposes this node again because it's still unresolved, not because a fresh candidate is due. None found → file exactly that one candidate — see step 4 — and stop there. Deterministic tools settle before agent-driven scanning starts (ADR-0008); don't also walk the codebase this pass.
- **`structural-scan`**: every node of the active language tree is resolved — fulfilled, or explicitly rejected under `docs/refactoring/out-of-scope/`. Continue to step 3.
- **No language tree recognized for this target**: proceed straight to step 3 — nothing to wait on.

### 3. Scope and walk the codebase

Reached only once step 2 opens the gate.

Decide *where* to look before you look:

- If the user named a direction — a module, a subsystem, a pain point — take it and skip the inference below.
- Otherwise walk back a good stretch of the commit history (`git log --oneline`) to find the **hot spots** — files and areas that keep coming up — and let those paths pull your attention first. If changes are scattered with no clear hot spot, widen the net.

Then explore organically and note where you experience friction. Look for:

- **Shallow modules** — little **depth**: interface nearly as complex as the implementation. Apply the **deletion test**: would deleting it concentrate complexity, or just move it? A "concentrates" is the signal you want.
- Missing **locality** — pure functions extracted for testability, but the real bugs hide in how they're called.
- Low **leverage** — a lot of interface surface buying little behaviour behind it.
- Tightly-coupled modules leaking across their **seams**.
- Untested parts, or parts hard to test through their current interface.
- **Tooling pressure** — places the fulfilled tooling (PHPStan, Rector, style) keeps flagging.

Use the `/codebase-design` vocabulary (module, interface, depth, seam, leverage, locality) in every candidate description — don't drift into "component," "service," or "API."

### 4. File candidates

**A tooling-tree node** (from step 1 or step 2): create one issue on the issue tracker (see `docs/agents/issue-tracker.md`) titled exactly `Tooling tree: <node>` (e.g. `Tooling tree: loop-config`) with the label **`refactor:candidate`**, naming the node and quoting its Tool / Purpose / Fulfilment check / MR scope from the tree doc. One node, one issue — that's the pass's entire output. Keep the title stable: steps 1 and 2 search for it on later passes to avoid filing a duplicate while this one is still open.

**A structural candidate** (from step 3): create an issue with the label **`refactor:candidate`** and a body that names:

- **Where** — module or files involved
- **Problem** — the friction, in the project's domain language
- **Signal** — which of the friction signals above it came from

Keep each candidate a single coherent refactoring — not a grab-bag. If a scan turns up an outright bug, route it to the normal bug path, not the refactor backlog.

### 5. Report

Summarise what happened this pass: which precondition stopped it, a tooling-tree node already pending (name the open issue), which single tooling-tree node was newly filed, or how many structural candidates were filed and the top 2-3 you'd look at first (and why). Then stop — prioritising is `refactor-prioritize`'s job.

## Fallback

- **`/codebase-design`**: if installed, use its vocabulary. Otherwise skip it — the full vocabulary (module, interface, depth, seam, leverage, locality) is already inline in step 3 above; use those terms and don't drift into "component", "service", or "API".

## Completion criterion

Exactly one of these happened, and the report says which: (a) a precondition stopped the pass with nothing filed, (b) a tooling-tree node was already pending and nothing new was filed, (c) exactly one tooling-tree node was filed as a `refactor:candidate` issue, or (d) every genuine structural candidate found during the walk is filed as a `refactor:candidate` issue with Where / Problem / Signal, with the top candidates listed. Never two nodes, and never a node together with structural candidates, in the same pass.
