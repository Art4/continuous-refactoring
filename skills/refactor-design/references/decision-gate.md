# The pre-implementation decision gate

Applies inside any design flow that can turn up a decision worth pausing over before step 5
(`refactor-design/SKILL.md`) — grounding/grilling a structural or externally-labeled candidate
(`structural-candidate.md` step 4), or planning a PHPStan baseline-shrink fix
(`phpstan-baseline-shrink.md` step 3). Check for either of the two cases below before writing
anything else.

## A decision meeting the `/domain-modeling` ADR bar

Hard to reverse, surprising without context, a real trade-off between genuine alternatives — the
same three-factor test that decides whether to offer an ADR — while the candidate itself still stays
behavior-preserving. The loop runs unattended; don't stop and wait for a live answer. Instead:

- Write the plan exactly as usual, choosing a default the same way any other design decision gets
  made.
- Also write, in the same (or an additional) issue comment, the specific question this decision
  raises and the default chosen — plain enough that a human can confirm it as written, or override
  it, by commenting, removing `needs-info`, and adding `ready-for-agent`
  (`docs/agents/triage-labels.md`) once satisfied. This lands on the target repo's own issue —
  `../../continuous-refactoring/references/forge-facing-writing.md`.
- **Actively manage both labels — don't just withhold one.** Add `needs-info`: the visible signal
  that this issue is waiting on a human, not merely unprocessed. This is what makes the candidate a
  **flagged candidate**: designed, but not yet cleared to implement. And remove `ready-for-agent` if
  the issue already carries one — an externally-labeled candidate can arrive pre-labeled by whoever
  filed it, believing it was already fully specified; that earlier assessment predates this question
  and is now stale. When removing a pre-existing label, say so plainly in the same comment (e.g.
  "this issue already carried `ready-for-agent`; removed pending the question above") — a label
  disappearing without explanation is exactly the kind of silent, surprising action this suite avoids
  elsewhere (`forge-facing-writing.md`).

The issue stays open, `refactor:candidate` unchanged — only its triage labels, and whether
`refactor-implement` may run against it this pass. `refactor-loop`
(`../../refactor-loop/SKILL.md` step 5) skips implementation for a flagged candidate still
missing `ready-for-agent`. How a later pass treats it meanwhile depends on the tracker
(`refactor-scan/SKILL.md` steps 2 and 3b): a native-label tracker can always rediscover it later, so
scan looks for other work instead of waiting on it; a git-only tracker has no such rediscovery, so the
pass stops there rather than risk losing track of it. A native-label tracker also checks the issue for a
human's own answer each time it's rediscovered — see "A flagged candidate's human answer arrives" below.

## A flagged candidate's human answer arrives

`refactor-scan` (`refactor-scan/SKILL.md` steps 2 and 3b) hands a flagged candidate back here, instead
of skipping it silently, when its issue's most recent comment is newer than this skill's own flagging
comment and its author is a human, not the suite's own bot account — someone answered. Read that
comment and judge it exactly the way grilling already judges a live answer:

- **Plainly confirms the default as written, raises no new question** → self-confirm: remove
  `needs-info`, add `ready-for-agent`, and post a short comment naming that this proceeds on the
  confirmation above (date it, so a later reader sees why the labels moved without re-reading the whole
  thread). The candidate is `ready-for-agent` from here on, same as any other confirmed plan.
- **Anything else** — a stated alternative, a further question, or not a plain yes — stays flagged.
  Check whether the suite's own most recent comment is already newer than this human comment; if so, a
  nudge was already posted for it, so say nothing further this pass. Otherwise post exactly one nudge
  comment: name plainly that a plain confirmation needs the label swap to take effect, or that a
  different choice needs to be spelled out concretely enough to replan against. Never apply a stated
  alternative automatically — only a plain "yes" self-confirms; a human still has to either restate
  their answer as a plain confirmation or swap the labels themselves once satisfied.

This is the return trip of this same page's "actively manage both labels" discipline above — the human
transcribing a settled answer into the two labels was always mechanical once the answer was plain; this
just means the suite does that transcription instead of leaving it for the human to remember to do. It
never lets the suite decide the actual trade-off — that still requires the human's own words on the
issue.

## A genuine breaking change

The fix can't be made without changing observable behavior — the foundational rule
(`../../continuous-refactoring/references/foundational-refactoring-rules.md`) that a refactor never
ships one. This isn't `refactor-design`'s call to act on: don't write a plan, don't comment on the
issue, don't touch any label — only `refactor-learn` writes bookkeeping/labels/`out-of-scope`
(`refactor-learn/SKILL.md`'s own stated boundary). Hand it forward instead as a **finding** — a short
statement of what was found and why it needs a behavior change — to this same pass's closing
`refactor-learn` call (`../../refactor-loop/SKILL.md` step 6), which applies its existing
rejection machinery (`wontfix`, a closing note or `out-of-scope/` entry) the same way it already
would for a load-bearing MR-review rejection.
