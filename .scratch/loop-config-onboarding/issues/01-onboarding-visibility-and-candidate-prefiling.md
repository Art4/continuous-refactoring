# 01 — Onboarding visibility and always-on candidate pre-filing

**What to build:** Three related changes, grilled together against live observations from running the orchestrator manually on a fresh target (`continuous-refactoring.de`, GitLab):

1. **Fast-path for the cold-start scan.** `refactor-scan`'s first pass on a target with no `bookkeeping.md` took noticeably long just to conclude "only `loop-config` is proposable" — the script (`tooling_tree.py`) is cheap, but the agent read most of the tree-doc tree before reaching that conclusion. Add a third precondition to `refactor-scan`'s "Check preconditions" step, alongside "no git repo" and "5+ open issues": no `bookkeeping.md` → propose only `loop-config`, skip the rest of the tree walk entirely (nothing else can be proposable yet — every other node requires `loop-config` as a parent).

2. **Onboarding visibility, scoped to `loop-config` only.** The `loop-config` interview currently goes straight from its three questions to recording the answers and implementing — no summary of what's about to happen, no per-action status while it happens. Add, inside `loop-config`'s own interview/implementation only (not a general orchestrator rule — `loop-config` runs exactly once per target, so this never needs an opt-out or a verbosity flag):
   - After the three questions are answered, one short summary of the concrete decisions (create-mode, tracker location, metadata location) and the concrete actions about to follow (e.g. "labels will be created on GitLab: `refactor:candidate`, `refactor:priority`"), before anything is written.
   - While executing, one short status line per visible action ("Labels werden angelegt", "Issue wird erstellt", "MR wird erstellt") instead of silent execution.

3. **Always pre-file newly-unblocked tooling-tree nodes as candidates.** Today, `refactor-scan` hands the orchestrator every currently-unblocked tooling-tree node as a **proposal**, but nothing is filed until `refactor-prioritize`'s Rank mode picks a winner — the other unblocked nodes stay invisible until some future pass happens to rank them. This mirrors `structural-scan`'s own Select mode too narrowly: that mode already files *every* concrete finding it discovers as an ordinary open issue, and only recommends the strongest one forward — tooling-tree proposals should get the same treatment. Concretely: `refactor-prioritize`'s **Rank mode** gains a step, right where it already reads each proposal's tree-doc Purpose line for ranking — before ranking, file a minimal candidate issue (Name + Purpose line, no plan) for any proposal that doesn't already have one. Applies from the pass right after `loop-config`'s own local fulfilment onward (`bookkeeping.md` exists — not "merged to `main`"; the interview's own confirmation, added in point 2, is already the human checkpoint that makes building on it safe before merge). `loop-config` itself is the one exception — it never gets pre-filed for itself, it keeps its own dedicated interview flow.

## Why now, not before

Point 3 gives the human a chance to comment on or reject a proposed tool *before* any implementation work (and its tokens) is spent on it — currently the only way to see what's coming next is to read tree docs directly or wait for it to be ranked.

## Explicitly out of scope / considered and rejected

- **Skipping the tree walk when candidate issues already exist** (an optimization raised and rejected during grilling): `tooling_tree.py` itself is cheap — the cold-start slowness (point 1) is agent read-overhead on an empty cache, a one-time cost point 1 already fixes. Skipping the walk whenever any tooling-tree issue is already open would make `refactor-scan` blind to genuinely new unblocks for as long as that issue sits open (up to the full backlog cap, five issues) — a real regression, not a real optimization. The walk always runs; only the *filing* decision is deduplicated, via the existing "already has an open issue" check `refactor-scan` step 3b already performs for externally-labeled candidates.
- **Raising or special-casing the existing backlog cap** ("5+ open `refactor:candidate` issues without `refactor:priority` → propose nothing new") for the post-`loop-config` burst (up to four nodes could unblock simultaneously: `is-php-project`, `ci-runner`, `editorconfig`, `secret-detection`). The cap stays exactly as it is, unchanged, and applies to the burst too. *(Idea for a later ticket, not this one: make the cap configurable.)*
- **A new mechanism for the "resumed a still-open, unmerged `loop-config` branch" observation** (running the orchestrator a second time before merging its own setup MR): confirmed as correct, expected behavior per this suite's own existing branch-stacking design (ADR-0015/0023/0028) — not a bug, not a fifth finding. Needs no new visibility mechanism of its own: one more clause on the orchestrator's own existing, generic closing-report "Status:" line (`skills/continuous-refactoring/SKILL.md`) covers it — not part of point 2's `loop-config`-scoped mechanism, since by the time this can happen `loop-config`'s own pass has already finished.
- **A general (every pass, every skill) status-line rule.** Deliberately scoped to `loop-config` alone (point 2) — the felt need was specific to onboarding, and generalizing it would need an opt-out/verbosity mechanism to stop it from getting noisy once the loop is trusted and running routinely. Scoping to a node that runs exactly once needs no such mechanism at all.

## Vocabulary impact

`CONTEXT.md`'s **Proposals** entry currently reads (in part): "...however many that is — not yet candidates, since nothing is filed until `refactor-prioritize`'s Rank mode picks one." That's exactly the rule point 3 changes. Update to:

> **Proposals**: The tooling-tree node names `refactor-scan` hands the orchestrator — every currently-unblocked one without an existing open candidate issue. `refactor-prioritize`'s Rank mode files a minimal candidate issue for each one (Name + Purpose line) before ranking — the same pattern Select mode already uses for a gate's own concrete findings, just without needing a gate to win first. `loop-config` is the one exception (its own interview flow, no pre-filing treatment).

## ADR

Warranted: hard to reverse (every future pass behaves differently once candidate issues start appearing automatically), surprising without context (a future reader would wonder why a tooling-tree proposal now files itself immediately, unlike before), and the result of a real trade-off explicitly considered and rejected during grilling (see "Explicitly out of scope" above, especially the tree-walk-skipping optimization). Write one covering: the always-pre-file decision, the Rank-mode-not-Select-mode placement, the walk-always/dedup-only resolution, and the `loop-config` exception.

## Affected files (expected, confirm during implementation)

- `skills/refactor-scan/SKILL.md` — new cold-start precondition (point 1).
- `skills/refactor-prioritize/SKILL.md` — Rank mode gains the pre-filing step (point 3); `## Output`/completion criterion likely need a line acknowledging issues may already exist for non-winning proposals.
- `skills/continuous-refactoring/references/loop-config-interview.md` — summary-before-execution + status lines (point 2).
- `skills/continuous-refactoring/SKILL.md` — closing report's "Status:" line gains the stacking-visibility clause (the rejected-mechanism note above).
- `CONTEXT.md` — **Proposals** entry rewrite (see Vocabulary impact).
- A new ADR under `docs/adr/`.

**Status:** done — PR #76

- [x] Cold-start fast path in `refactor-scan`
- [x] `loop-config` interview: pre-execution summary + per-action status lines
- [x] `refactor-prioritize` Rank mode: pre-file a minimal candidate issue per proposal without one
- [x] Closing report: stacking-visibility clause for a pass that continues on a still-open suite branch
- [x] `CONTEXT.md` **Proposals** entry rewritten
- [x] New ADR recording the trade-offs above

## Comments

> **2026-09-12:** Grilled jointly (`/grill-with-docs`) against live observations from manually running the orchestrator on `continuous-refactoring.de` (GitLab target). All decisions above confirmed by the maintainer, including the vocabulary rewrite.
> **2026-09-12:** Implemented (`/implement`) on this same branch, reviewed against `/writing-for-agents` via `/code-review`'s two-axis process (three findings addressed: clearer cold-start wording, status-line convention anchored to every `## Record` write instead of four fixed examples, `refactor-prioritize`'s Output noting non-winning proposals now carry an issue too). `python3 -m unittest discover -s scripts -p 'test_*.py'` (307 tests) and `python3 scripts/validate_skills.py` (same 5 pre-existing advisories as `main`, no new ones) both green. PR #76.
