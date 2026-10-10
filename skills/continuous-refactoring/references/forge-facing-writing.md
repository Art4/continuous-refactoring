# Reference: writing for the target's tracker and forge

Applies to every text the suite leaves in the target: a ticket's title and text, a comment, a closing
note, a rejection's reason, a merge request's description. Its reader has never seen the skill suite and
cannot open its files.

Write each sentence from the thing itself:

- **State the rule or the finding in plain words**, where the suite's own texts would cite one of their
  files.
- **Describe the actual thing**, where the suite's own texts would use one of their terms — candidate,
  node, Track, Safety Net, fulfilled, decision point: "PHPStan is not set up yet".
- **Keep every external fact as concrete as it is**: a tool's or feature's real name ("PHPStan Level 0"),
  a file and line of the target, the behaviour observed, the number of a ticket or merge request.

**Before posting,** read the draft as that stranger: a sentence that leans on a path or a term only the
suite knows is rewritten from the rule or finding it stands for.

Example — "Closing this: the fix would start storing data the application drops today, which changes
behaviour instead of structure." The function, the parameter and the target's file paths stay in the text;
they live in the target, where the reader can open them.
