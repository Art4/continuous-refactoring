# 01 — A run's own review step is skipped on small diffs

Type: task
Status: open
Blocked by: —

**What was seen**

- In a Driver session of about twenty rounds, several runs ended with a report like "the review ran as a self-check of
  a small diff, no subagent" or "review skipped, the diff is one line". The diffs were a config line, tool output
  only, or a docblock. The Driver's own second review of the merge request still ran every time, and found a wrong
  description in three of them.
- The run's review step says nothing about when it may be shortened. The runs decided it themselves, each in its own
  words, and one said so in the report while another only implied it.
- No harm came of it in this session. The question is whether the skill wants the run's review to be skipped,
  shortened or always the full step, because the Driver's review follows anyway.

**Open**

- Does a run keep its full review where the Driver reviews afterwards, or is a lighter form allowed for a diff of
  tool output alone or of a single config line?
- If a lighter form is allowed: where it is written (the run's review step), what qualifies, and what the report
  says (the Status line names that the review was shortened and why).
- If not: whether the run's report names a skipped review as a deviation.

## Comments
