# Reporting progress to the human

Rules for whoever runs a pass in the human's own conversation — `refactor-loop` for the three loop Tracks, `continuous-housekeeping` for Housekeeping. The reader is watching the conversation live and has to be able to tell what the pass is doing and what it just changed in their repo, without opening anything.

**Before each step: one sentence** saying what starts (and, when a subagent runs it, that it does). **After each step: one sentence** with the result — what was found, what was chosen and why in a few words, what came back. Two sentences at most, plain words, no slugs: name a tooling-tree node by its Name.

**Every write to the target is reported on its own, as it happens** — an issue created, a comment or label on an issue, a branch pushed, a merge request opened, an `out-of-scope/` entry. Name the thing and where it lives (number, branch, link). Say "merge request" or the forge's own word (pull request on GitHub), per `opening-a-merge-request.md`.

**A step that doesn't run** gets one sentence naming why, when the reason is a choice the pass made (e.g. resuming an open candidate skips ranking and design). A step that stops the pass early is reported at once — that rule already lives in the caller.

**Only the caller reports.** A subagent has no channel to the human. It lists the writes it made in its `## Output`, and the caller turns that list into the sentence after the step. The caller never guesses at a write the output doesn't name.

**The closing report stays two lines** (Status / Next) and doesn't repeat the per-step sentences; it summarises the outcome, they narrate the way there.

Examples of the sentence after a step: "Scan: 4 nodes are ready to propose, nothing has merged or closed since the last pass." · "Ranked: PHPStan Level 1 comes first — it unlocks Level 2 and the baseline is already clean." · "Design: added the plan to issue #12; it waits for your answer on the open question." · "Implementation: pushed `refactor/phpstan-level-1` and opened merge request #34; CI is running."
