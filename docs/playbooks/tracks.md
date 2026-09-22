# Playbook: The Tracks

The playbook for humans. The skills do the work; this document explains how the loop decides *which kind* of work a pass does, and how you can steer that decision. The step-by-step lives in `skills/continuous-refactoring/references/track-scheduler.md`.

## What a Track is

A **Track** is one scheduled work mode a loop pass can spend itself on. Each pass runs exactly one Track — or, if none is due, ends and says so. There are four:

| Track | Purpose | Own state in `bookkeeping.md` | Default `Cadence` |
|---|---|---|---|
| **Safety Net** | Adopt the deterministic tooling (test runner, coding standards, static analysis, CI) that catches a regression *before* structural work starts | `Cadence`, `Last scan`, `Open`, `Out-of-scope` | 90 days |
| **Guardrails** | Adopt further quality and security tooling once the Safety Net has closed (dependency audit, coverage floor, mess detection, …) | `Cadence`, `Last scan`, `Open`, `Out-of-scope` | 60 days |
| **Housekeeping** | Recurring maintenance sweep — dependency currency, tooling-deprecation cleanup, documentation sync ([playbook](housekeeping.md)) | `Cadence`, `Last scan` | 7 days |
| **Investigation** | Find and deliver one structural refactoring candidate (hot spot, deepening) — only opens once the Safety Net is in place | `Cadence` (always `continuous`), `Last scan` | none — always due |

Safety Net and Guardrails walk the [tooling tree](../../skills/refactor-scan/references/tooling-tree.md): each adoption step is a *node*, and a Track's `Open` list holds the nodes still to do. Housekeeping and Investigation have no `Open` list.

### Writing a `Cadence`

`Cadence` is a number with its unit — `12 hours`, `90 days`, `2 weeks`, `1 month` — or a fixed calendar day, `monthly on the 1st` (any day from the 1st to the 28th). A bare number from an older file still reads as days. Edit it by hand any time; the Track's next pass reads it as written. A value the loop can't read is never guessed at: the Track's default is used for that pass and the report says which value was unreadable. Limits (a month counts as 30 days, hours are only day-accurate): [known limitations](../known-limitations.md).

## How a Track is selected

Before any of this, a project that has never run the loop (no `bookkeeping.md`) is **onboarded** instead: that invocation asks a few setup questions, writes the setup files and stops, without selecting a Track — even when you named one. Track selection only happens once onboarding has run.

The `/continuous-refactoring` skill then decides one thing per pass — which Track — and hands it to that Track's own skill. It applies these rules in order:

1. **You named a Track** ("run the Guardrails Track", or you invoked `/continuous-guardrails` directly) → that Track runs, no computation. See *Overrides* below.
2. **The one-time exception**, once per repo — see below.
3. **Safety Net blockade:** while Safety Net's `Open` is non-empty, Safety Net runs and nothing else does — even on a pass where no node is currently workable (the loop then reports what it is waiting for).
4. **Otherwise the most overdue Track wins.** A Track is *due* when it has never run or `(today − Last scan) / Cadence >= 1`; the highest ratio is selected. A Track whose `Open` is non-empty drops out of this comparison — its existing work is finished instead of rescanned. Ties, and Tracks that never ran, fall back to the fixed order **Safety Net > Guardrails > Housekeeping > Investigation**.

Investigation has no interval to measure staleness against, so it is always due — but it is last in the fixed order, so it only wins a pass when nothing else does. A Guardrails Track with workable `Open` nodes is selected ahead of it; with nothing workable, it yields.

## The one-time exception

Once Safety Net's `Open` is empty, the target has its foundation — and before ordinary scheduling takes over, it gets one dedicated turn each, in this order:

1. **Investigation** — one candidate, delivered end to end, so you see real refactoring value early;
2. **Guardrails** — its first scan-and-clear cycle;
3. **Housekeeping** — its first cycle.

Ordinary scheduling resumes for good after that, including later, rarer Safety Net rescans. No flag is stored: the loop derives it from which Track sections already exist in `bookkeeping.md`. Only naming a Track yourself outranks it.

## Working a Track's open items

When a selected Track (Safety Net or Guardrails) has a non-empty `Open` list, the pass does **not** rescan; it walks the list top to bottom and works **exactly one node per pass**:

- A node is *workable* when every required parent is fulfilled (or rejected), every recommended parent is decided, its issue isn't waiting on `needs-info`, and it isn't held back by an unverified PHP floor.
- Non-workable nodes are skipped and listed with their reason in the closing report (e.g. "Skipped: phpstan-level-6 (blocked by phpstan-level-5)").
- Right before working a node, its fulfilment is judged again. If you adopted the tool by hand since the last scan, the node simply leaves `Open` — no issue, no merge request — and the walk moves on.
- The node's issue is filed only when it is actually worked.

A Track with an empty `Open` is *scanned* instead: fulfilment of every node is judged against its purpose (an agent judgement, not a dependency-name match), and the unfulfilled, unblocked ones become the new `Open` list.

## Overrides

- **Name the Track:** `/continuous-refactoring` with a Track name ("run the Housekeeping Track") bypasses selection *and* the one-time exception for this pass.
- **Invoke the Track skill directly** (`/continuous-safety-net`, …): the same override — but a project that was never onboarded is refused with a pointer to `/continuous-refactoring`, which onboards it first.
- A named Track still respects its own `Open`: naming Safety Net while its `Open` is non-empty means working that entry, never a fresh rescan.
- **Change a cadence:** hand-edit `Cadence` in that Track's section of `bookkeeping.md` (Housekeeping also offers a one-question interview). Investigation's `Cadence` is fixed.
- **Priority label:** a `refactor:priority` label you set on an issue narrows which proposals get ranked. It plays no part in Track selection, cannot bypass the Safety Net blockade, and never preempts an open-item walk — a labelled issue waits until `Open` is empty (Safety Net) or has nothing workable left (Guardrails).

## Limits that apply to every Track

- **Two merge requests at most.** Before a pass would open a *new* merge request it counts the suite's open ones; with two or more, the candidate keeps its plan, the pass tells you which requests are waiting and ends without new work. Continuing an already-open merge request isn't gated.
- **Every merge request branches off the default branch** — never off another open suite branch.
- **One candidate, one branch** per pass.

## Reading the closing report

Every pass ends with two lines. **Status** says what happened (including skipped nodes and why a pass stopped early); **Next** says what you should do — usually "review and merge #N". If a claim can't be confirmed (no remote, CI status unreadable), the report says so instead of assuming.

## Common mistakes

- **Expecting Guardrails or Investigation before the Safety Net is done.** The blockade is intentional; look at Safety Net's `Open` list to see what is missing.
- **Forcing a Track and expecting a rescan.** Naming a Track with open items works them; empty its `Open` first (or wait for it to empty).
- **Editing `Last scan` to "skip" a Track.** Raise its `Cadence` instead; `Last scan` is written by the loop.
- **Reading a skipped node as a failure.** It is waiting on a parent, a `needs-info` answer, or a floor check — the report names which.
