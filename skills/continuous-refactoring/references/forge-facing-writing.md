# Writing for the target repo's own forge

Applies to any text a lifecycle skill posts onto the **target** repo's own forge — an issue comment, a
closing note, a human-readable `out-of-scope/<node>.md` entry, a merge request's description or body.
The reader has never seen the `continuous-refactoring` suite's own repo and can't open its files.

Two leak patterns share one cause — this suite's skill files talk to the *acting agent*, and that
citation style leaks straight into forge-facing prose unless something switches audience first:

- **This suite's own file paths.** Don't cite a path under this repo's own skill or ADR directories as
  the reason for something. State the rule or finding itself, in plain words, instead of pointing at
  where it's written down.
- **This suite's own controlled vocabulary.** Don't use a `CONTEXT.md` term scoped to this suite's own
  bookkeeping — candidate, finding, tooling-tree node, gate, flagged candidate, pending candidate,
  resume-candidate, fulfilled node, and the like — as if the reader already knows it. Describe the
  actual thing instead.

Neither applies to a genuine external fact: a real tool or feature name (a tooling-tree node's own
Name, e.g. "PHPStan Level 0"), a target-repo file or line, the actual behavior or finding itself. Those
stay exactly as concrete as they already are — this is a redirect, not a ban on saying things. Say
everything relevant; only the citation or the borrowed label gets restated in plain language.

**Self-check before posting:** read the draft back as that stranger would. Does a sentence lean on a
path or a label that only means something inside this suite? Rewrite that sentence from the rule or
finding itself, not from where — or in what words — this suite happens to keep it.

**Example.**

- Not this: "Per the suite's foundational rule (`skills/continuous-refactoring/references/foundational-refactoring-rules.md`), this candidate is closed as `wontfix`."
- This instead: "Closing this — the fix would start persisting data the app currently drops, which is a behavior change, not a structural one."
