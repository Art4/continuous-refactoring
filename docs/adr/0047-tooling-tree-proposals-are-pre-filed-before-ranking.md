# Tooling-tree proposals are pre-filed as candidate issues before ranking, not only the winner

## Context

`refactor-scan` hands the orchestrator every currently-unblocked tooling-tree node as a **proposal** — but until now, nothing was filed for any of them until `refactor-prioritize`'s Rank mode picked one. The other unblocked nodes stayed invisible on the tracker until some future pass happened to rank them, or a human went and read the tree docs directly. This under-serves the one thing a human actually wants early in a target's life: a look at what the loop is about to propose, with a chance to comment or reject before any implementation work (and its tokens) is spent.

`structural-scan`'s own Select mode already solved this shape of problem for structural candidates: it files *every* concrete finding its codebase walk discovers as an ordinary open issue, and only recommends the strongest one forward — the others simply sit, visible, for a future pass. Tooling-tree proposals arrive already concrete (a tree doc fully specifies Tool/Purpose/Fulfilment check/MR scope for every node) — they never needed a Select-mode-style exploration step at all, which is exactly why nothing analogous to it ever ran for them.

Surfaced by a maintainer manually running the orchestrator against a fresh target (`continuous-refactoring.de`, GitLab) and asking, after `loop-config` alone landed, whether the loop would propose everything `loop-config` had just unblocked at once, or drip them out one at a time. It drips them out one at a time today — not the behavior wanted.

## Decision

`refactor-prioritize`'s **Rank mode** files a minimal candidate issue (title `Tooling tree: <Name>`, label `refactor:candidate`, body = the node's own Purpose line, no plan) for every tooling-tree proposal that doesn't already have one — right where it already reads that Purpose line to rank it. No new step, no new dispatch: the filing happens inline, in the same pass, before the ranking it feeds is even presented.

This applies to ordinary tooling-tree proposals only:

- **Not** `loop-config` itself — it keeps its own dedicated interview flow (`loop-config-interview.md`), never pre-filed like its own children.
- **Not** a gate name (`structural-scan`, a PHPStan baseline-shrink family) — those still only become concrete once Select mode's own exploration runs, exactly as before; there's nothing to pre-file before that walk happens.
- **Not** a proposal that already arrives issue-backed (`refactor-scan` step 3b: an earlier pass's own pre-filing, or a human-labeled issue) — nothing to file, it's already covered.

Starts applying the pass right after `loop-config`'s own **local** fulfilment — `bookkeeping.md` existing in the checkout, not "merged to the default branch." The interview's own confirmation (a second, related change landing alongside this one: a plain-prose summary of what's about to happen, shown before `loop-config`'s own writes) is already the human checkpoint that makes building on an unmerged `loop-config` safe; waiting for a merge on top of that would just be a second, redundant gate.

`refactor-scan` itself keeps running its tree walk (`tooling_tree.py`) every pass, unconditionally, once `loop-config` exists — see Considered Options for why. `refactor-scan` step 4 skips proposing a node by bare Name when step 3b already surfaced it as an issue-backed proposal, so the same node is never counted twice in one pass. `refactor-design` step 5, which already checked for an already-open `Tooling tree: <Name>` issue (to resume an interrupted pass without filing a duplicate), now distinguishes that case from a *minimal* one — a proposal pre-filed here that has just won a ranking — and writes the full tree-doc content into the existing issue's body instead of leaving it at a bare Purpose line forever.

## Considered Options

- **Skip `refactor-scan`'s tree walk whenever a tooling-tree candidate issue is already open**, to save the cost this ADR's own motivating observation also flagged (a cold-start pass reads through most of the tree docs before concluding "only `loop-config`"). Rejected — raised and walked back during grilling: the walk's cost was never the ongoing, steady-state cost (the underlying script is cheap; see ADR context — the real cost was one-time agent read-overhead on an empty cache, fixed separately, below), and skipping it would make `refactor-scan` blind to genuinely new unblocks for as long as any tooling issue sits open — up to the full backlog cap, five issues at once. A real regression traded for an optimization that wasn't needed.
- **Raise or special-case the existing backlog cap** ("5+ open `refactor:candidate` issues without `refactor:priority` → propose nothing new") for the burst right after `loop-config` (up to four nodes can unblock simultaneously: `is-php-project`, `ci-runner`, `editorconfig`, `secret-detection`). Rejected — the cap stays exactly as it is, unchanged, and applies to this burst too; a repo showing five brand-new proposed tools at once is already a lot for a human to review, cap or no cap. Making the cap itself configurable is a plausible later idea, not part of this decision.
- **Gate pre-filing on `loop-config`'s own merge request actually landing on the default branch**, not just existing locally. Rejected once the interview itself gained a pre-execution summary (a separate, related change) — that summary is already the human's chance to object before anything about the target's conventions is settled; waiting for the merge on top of it would only delay visibility for no added safety.

## Consequences

- `skills/refactor-scan/SKILL.md`: a new precondition (no `bookkeeping.md` yet → propose only `loop-config`, skip the tree walk); step 3b's own framing widens from "externally-labeled" to "issue-backed" (it now also naturally surfaces this ADR's own pre-filed proposals on a later pass); step 4 skips a bare-Name proposal already covered by step 3b.
- `skills/refactor-prioritize/SKILL.md`: Rank mode's step 2 files the minimal issue, described above.
- `skills/refactor-design/SKILL.md`: step 5's tooling-tree dedup check gains the minimal-vs-fully-written distinction.
- `skills/continuous-refactoring/references/loop-config-interview.md`: a fourth summary line (upcoming actions) and a status-line convention for `## Record`'s own writes — the DX half of the same grilling session, not this ADR's own subject, but what makes pre-filing safe before `loop-config`'s merge lands.
- `skills/continuous-refactoring/SKILL.md`: the closing report's Status line gained a stacked-branch clause for a pass whose write landed on a still-open suite branch rather than a fresh one — since removed along with stacking itself ([ADR-0049](0049-abolish-suite-mr-stacking.md)), the case it covered no longer arises.
- `CONTEXT.md`'s **Proposals** entry rewritten — it previously stated the exact rule this ADR reverses ("not yet candidates, since nothing is filed until Rank mode picks one").
- A future scan/design pass must not re-treat a minimally-filed tooling-tree issue as a fresh candidate needing its own new filing, and must not re-propose `loop-config`'s own children by bare Name once they already carry an issue.
