# 01: An answer to an open question is recognised by its content, not its author

**Status:** done — PR #193

## Observation

A Guardrails loop on webtrees-assistent (2026-10-23, 15 rounds, !67–!76): one agent started each run
in a subagent (`/continuous-refactoring Track guardrails, do it yourself`), reviewed and merged its merge
request, and started the next. Agent comments and the human's replies came from the same GitLab account
(Art4). Replies such as "Choice: 1", "Decision: Option 2" and "Decision: out-of-scope" could not be told
apart by author; the driving agent checked them by timestamp and by where they fell between runs, and the
run in round 11 named the doubt itself. In round 10 a run reported #73 as workable while its
`StaticAccess` question was still open.

## The gap

`references/design-point.md`, *Open questions*: "Any newer comment ends the wait." The rule never asks
who wrote the comment — so mechanically it works with one shared account. The risk is the other way:
any comment an agent posts after the question — a driving agent's notice, a review comment, a run's
own note that is neither a plan nor a question — ends the wait and is read as the answer.

One account for agent and human is likely the common case: agents work with the human's token.

## Direction

- An answer is a newer comment that is none of the suite's own forms (`Plan`, `Open question`, the fixed
  notes the suite posts) — recognised by content, never by author.
- `docs/known-limitations.md`: an agent commenting on a waiting ticket counts as an answer; an agent that
  drives runs leaves waiting tickets alone.
- `CONTEXT.md` / worklist state **waiting** read true against it.

## Done when

- *Open questions* and the worklist's **waiting** state say what counts as an answer.
- known-limitations, FAQ ("I answered an open question on a ticket — what happens now?") and CONTEXT.md
  read true; a changelog fragment exists.
