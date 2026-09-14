# Posting the Outlook comment

`refactor-implement` step 5's own instruction, run once the MR is open, tooling-tree candidate only —
moved off the MR description and onto the candidate's own issue
(`docs/adr/0051-refactor-learn-requires-a-genuine-event.md`'s sibling decision,
`docs/adr/0052-grilling-decision-trail-separate-from-decision-gate.md`; see also
`skills/continuous-refactoring/references/opening-a-merge-request.md`'s own note).

Post one plain-sentence comment on the *candidate issue* (never the MR description) naming the next
node's **Name** and working its Purpose into the same sentence (e.g. "next up: Composer — dependency
management for the Composer-stack track") — a later reader of the (by-then-closed) issue sees what
this unlocked without digging through scan output. Nothing about how that was determined belongs in
it — no shell command, no file path, no `Purpose:`-labelled field. To find it: re-run `python3
skills/refactor-scan/references/tooling_tree.py <target-repo> --steps 1 --unblocked-by
<landed-node-slug>` against the now-changed working tree and look up the returned `roadmap` entry's
slug's Name in the tree doc. No `python3`, or not permitted → dispatch a sub-agent with
`skills/refactor-scan/references/tree-walk-prompt.md`'s prompt (`{N}=1`) instead; no sub-agent
mechanism → run that prompt's steps yourself inline. The sub-agent/inline fallback covers the sentence
only — it has no equivalent for the diagram below, so a comment posted that way carries the sentence
alone.

When the same call's `unblocked_by` key holds **two or more** entries, append a Mermaid `flowchart`
below the sentence in the same comment, fanning out from the landed node: one node per
`unblocked_by` entry, labelled by its **Name** (looked up the same way as the sentence's own node);
one edge per entry from the landed node's Name, labelled by that entry's `type`
(`required`/`recommended`/`required-any`). Fewer than two entries → no diagram, sentence only — a
one-box fan-out repeats what the sentence already said.

Structural candidates carry no Outlook at all, diagram included — there's no single next child a
deepening unlocks the way a tree node does.

Follow `skills/continuous-refactoring/references/forge-facing-writing.md` like any other forge-facing
text.
