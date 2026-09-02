# Review Axes Reference

Two-axis review for the diff, run before opening the merge request.

## Standards axis

Does the diff conform to the repo's documented coding standards and the fulfilled tooling?

On top of documented standards, carry the Fowler smell baseline — fixed set of smells that applies even when the repo documents nothing:
- **The repo overrides.** Documented standard always wins.
- **Always a judgement call.** Each smell is a labelled heuristic, never a hard violation. Skip anything tooling enforces.

Smells: Mysterious Name, Duplicated Code, Feature Envy, Data Clumps, Primitive Obsession, Repeated Switches, Shotgun Surgery, Divergent Change, Speculative Generality, Message Chains, Middle Man, Refused Bequest.

Each: *what it is* → *how to fix*. See `review-fallback.md` for full descriptions.

## Spec axis

Does the diff faithfully implement the plan on the candidate issue:
- Requirements missing or partial
- Behaviour that wasn't asked for (scope creep)
- Requirements that look implemented but wrong

Quote the spec line for each finding.

## Rules

- Report findings per axis separately — never merge or rerank across axes.
- One line per finding: file, issue, fix. No prose beyond that.
- Findings send work back to implementation — don't hand off to a separate skill.
