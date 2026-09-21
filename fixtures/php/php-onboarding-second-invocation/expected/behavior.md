# Expected behavior — the invocation after onboarding is an ordinary pass

The state the onboarding leaves behind, committed: `docs/refactoring/bookkeeping.md` holding only `Create-mode`
(no `Pending candidates`, no Track sections), `docs/agents/issue-tracker.md` (Local Markdown),
`docs/agents/triage-labels.md` and the suite's section in `AGENTS.md`. Not deterministically checkable; run via
`fixtures/harness/run.sh agent-loop php-onboarding-second-invocation`, local-only and advisory.

## Expected: `/continuous-refactoring`

1. **No onboarding text** — step 0 finds `bookkeeping.md` and skips straight to Track selection, without
   saying anything about onboarding (not even that it is complete).
2. No `## Safety Net` section exists, so the Safety Net Track is treated as never run and selected (it wins its own
   ratio comparison; the one-time exception needs an existing `## Safety Net`). The dispatcher says so in one
   sentence and invokes `/continuous-safety-net`.
3. `refactor-loop` announces the pass and starts the scan in a subagent ("Starting a fresh scan in a subagent") —
   no abort for a missing `bookkeeping.md`.
4. The pass proceeds as any other Safety Net first pass (`php-safety-net-first-run` covers the recording of `Last
   scan`); the human-visible difference from before is only that the questions were asked one invocation earlier.

## Verified

Confirmed live on 2026-09-21: the sandbox left by the `php-onboarding-fresh` run above, its four files
committed by the human, then `/continuous-refactoring` again (`opencode` 1.18.31, `opencode/big-pickle`).
Observed: no onboarding interview; the existing `bookkeeping.md` — holding only `Create-mode` — was accepted,
all four Tracks counted as never run, the fixed order selected Safety Net, and the scan subagent started
normally; the files the onboarding wrote (`issue-tracker.md`, `triage-labels.md`, `AGENTS.md`) were read and
used through prioritise, design, implement and the closing bookkeeping write. One deviation: the run said
aloud that onboarding "is complete" before selecting the Track. Step 0's wording was changed afterwards so
the already-onboarded case stays silent; that change has not been re-run live.
