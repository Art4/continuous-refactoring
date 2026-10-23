# 02: A proposal with an open question is filed, with the question on its ticket

**Status:** open — direction agreed 2026-10-23

## Observation

Same loop as 01. In round 5 a scan proposed a Secret Detection Stage with an open question (local
scanner or decline). The autonomous run left it unfiled and carried the question into its closing
report. In a subagent that report reaches only the driving agent's context, not the tracker. The Stage
had no ticket and no rejection, so it was not **known**: rounds 6 and 7 scanned it again and raised the
same question. It ended only after the human answered in the conversation mid-loop and round 8 filed and
closed #81 as the rejection. To bridge the gap, the driving agent added state lines ("Secret Detection is
rejected") to each run's prompt.

## The gap

`references/filing-a-ticket.md`, step 2: "A proposal with an open question is filed once a human answered
it; an autonomous run leaves it unfiled and carries the question into the closing report." The question
lives nowhere on the tracker, against the suite's rule that the tracker is its state.

## Direction

The autonomous run files the ticket and posts the question on it as an `Open question` comment
(`design-point.md`, *Open questions*). The ticket is **waiting** like any other, the Stage is known, the
next run skips it and goes on; an answer picks it up. Reverses "filed once a human answered it".

Interactive runs: open — either ask in the conversation as today, or file with the question when the
human leaves it open.

## Done when

- `filing-a-ticket.md` step 2 says it; the note "A proposal neither filed nor declined is not stored
  anywhere" reads true against it.
- `docs/playbooks/run.md`, `docs/FAQ.md`, CONTEXT.md read true; ADR if the reversal meets the bar; a
  changelog fragment exists.
