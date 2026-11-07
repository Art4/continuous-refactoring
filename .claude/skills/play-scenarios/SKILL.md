---
name: play-scenarios
description: Play the suite's scenarios against this checkout — those a branch's changes cover, a named list, or all — each by a fresh player and judged by a fresh judge.
disable-model-invocation: true
---

# Play the scenarios

The scenarios live in `docs/agents/evals/`; its `README.md`, *Playing one*, is the contract this skill carries
out. Every play is **blind**: a player sees the scenario's *Situation* and *Call*, never its *Expected* list; a
judge sees the list and the player's record, never the conversation that changed the skill.

## 1. Pick

- **A list is named** ("r7 r8", "all") → those scenarios.
- **Otherwise** → the branch: `git diff --name-only main...HEAD -- skills/`, the scenarios whose `Covers:` line
  names one of those files, and of them each whose *Expected* lines bear on the behaviour the diff moves. Name the
  ones left out, each with its reason, for the pull request.

Then a **play** per what the scenario's opening line and *Situation* say: one per variant, per case, per call, or
the number of times it names. Note `git rev-parse --short HEAD`, and whether `git status --porcelain -- skills/`
shows changes the commit does not hold.

A scenario played *live, in a real session* (d9) needs a fresh top-level session with the suite installed, which a
subagent is not: list it as **for the human**, with its calls, and play it no further.

Make a folder for this playing in the scratchpad. Each play gets a short name (`r7-a`, `d5-b`); write its brief
— the scenario's title, how it is played, *Situation* and *Call*, and for a variant "This play is variant <X>." —
to `<name>.brief.md`, and its *Expected* list to `<name>.expected.md`. The player writes its record to
`<name>.md`, so the records stay out of this conversation.

The variants or cases of one scenario may go to **one player**, played one after another, each in a section of its
own: it reads the skill once. Plays of different scenarios never share a player; one would no longer be blind.

*Done when* every play is listed: name, scenario, variant or step, walk-through or live.

## 2. Play

One fresh subagent per play, or per scenario where its variants share a player. Start them together, or one
after another when the human wants to watch the cost: each subagent's usage shows when it returns. Hand each the
brief below, filled in, and nothing else.

- **Walk-through:** the state is told; nothing is written.
- **Live:** before the player starts, copy the fixture the *Situation* names into a new folder in the scratchpad,
  make the changes it lists there, `git init`, commit. The player works in that folder for real.

```
You are playing a test of a skill of the continuous-refactoring suite. The skills are at
<repo>/skills/; start with <the skill the call invokes>/SKILL.md and read whatever it sends you to.
Read only the skills, the fixtures and your play's folder: docs/agents/ holds the answers.
<Walk-through: There is no real forge or target: the brief is all there is, and every search,
listing or command returns what it implies. A subagent the skill starts, you play yourself, its steps
in a section of their own. You may run the parser
skills/continuous-refactoring-run/references/tooling_tree.py read-only on a fixture under
<repo>/fixtures/ to see the tree; pass seeds by process substitution. Write no file anywhere.>
<Live: Work in <folder> as the target, for real. Change nothing outside it.>

Say step by step what you do: which step and reference you follow, which skill, tool and subagent you
call, each decision point's findings, options and recommendation, and every write. End with the
closing lines the skill asks for, then a list of every place where the skill text was unclear or
contradictory for you. Write all of it to <folder>/<name>.md, and return only "done".

Your brief is <folder>/<name>.brief.md.
```

*Done when* every play has returned its record.

## 3. Judge

A fresh subagent per play, started as its player returns; one judge may take several records, judging each on
its own, since it reads only them and the lists:

```
You judge one play of a test. The expected lines are <folder>/<name>.expected.md; the player's record
is <folder>/<name>.md. Judge each line that applies to this play by the record alone: it holds when
the record shows it; a line the record does not show fails as "not shown". <Live: the play's folder is <folder>; read it to check what was
written.> Do not play the scenario yourself.

Write, per line, holds or fails with the sentence of the record it rests on, to <folder>/<name>.verdict.md.
Return only the result: pass, or the lines that failed, quoted, each with one sentence of what the record
shows instead; then the record's unclear places, one line each.
```

*Done when* every play has a verdict.

## 4. Report

To the human, in one message:

- Per scenario: pass, or each failed line quoted with what the record showed instead. Read the verdict file where a
  result leaves the cause open. A fail is a finding about the skill text, unless the record shows the scenario left the player a
  fact it needed: then it is a finding about the scenario.
- The unclear places the players named, grouped where several named the same.
- The plays for the human.
- Per scenario the proposed line for its `## Results`: `<date>, on <commit>[ with <what the branch changes>]:
  pass, every line[, every variant], as <a walk-through | live>.`, or the failed lines in place of "pass".

Change no skill file and no scenario's *Expected*. On the human's go, append the proposed lines to the
scenarios' `## Results`.

*Done when* the human has the message, and the lines they accepted are appended.
