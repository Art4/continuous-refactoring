# Opening a merge request

Rules for any suite skill opening or basing a merge request (MR): `refactor-implement` for a candidate, `refactor-learn` for a bookkeeping MR.

**Create-mode.** Read the Refactoring Notes' `config.md`'s `Create-mode` field and follow it — `autonomous`, `ask-each-time`, or `human-opens`. Decided exactly once, during `loop-config`'s own interview (`skills/continuous-refactoring/references/loop-config-interview.md`) — not inferred fresh per merge request, not deferred to `refactor-learn`. That interview reads `AGENTS.md`/`CLAUDE.md` first: either already names a mode → that becomes the recommended (not automatic) answer put to the human; neither does → the recommended answer is `autonomous`. Either way, the human decides, and the answer lands in `Create-mode` when `refactor-implement` creates `config.md`. `refactor-learn` follows the same field for its own bookkeeping MR — it no longer decides the mode itself, except a narrow fallback for a `config.md` that predates this convention.

**Vocabulary.** Skills always say **merge request**; talking to the human, use the forge's own word (pull request on GitHub, merge request on GitLab).

**Basing/stacking.** While fewer than two suite MRs are open, a pass may deliver one more — always **stack** it (base = whatever suite branch is currently open), never branch parallel off the default branch. This holds regardless of whether the new candidate is a tooling-tree child of what's in flight — it keeps two branches from ever writing the Refactoring Notes' `config.md` concurrently (a past conditional version of this rule caused repeated merge conflicts there). After the base merges, the next pass retargets or rebases the child.

**Description.** Opens with one or two plain sentences for a human who doesn't know the suite's vocabulary — what this unlocks for the project, not which tree node it fulfils. Then the plain facts: link the candidate, what changed, which tests survive, what CI proves.

**Outlook**, tooling-tree candidate only: close the description with one plain sentence naming the next node's **Name** and working its Purpose into the same sentence (e.g. "next up: Composer — dependency management for the Composer-stack track"). Nothing about how that was determined belongs in it — no shell command, no file path, no `Purpose:`-labelled field. To find it: re-run `python3 skills/refactor-scan/references/tooling_tree.py <target-repo> --steps 1` against the now-changed working tree and look up the returned slug's Name in the tree doc. No `python3`, or not permitted → dispatch a sub-agent with `skills/refactor-scan/references/tree-walk-prompt.md`'s prompt (`{N}=1`) instead; no sub-agent mechanism → run that prompt's steps yourself inline.

A structural candidate carries no outlook — there's no single next child a deepening unlocks the way a tree node does.

**No forge/remote available.** `git remote -v` (or equivalent) shows nothing, or the configured remote can't be reached — there is nowhere to push to, in any create-mode. This is not the same situation `git-only-reconciliation.md` covers (that's "a remote exists, only the API is unavailable") — here there's no remote at all. Don't invent a substitute: no local-only "merge request," no direct commit to the default branch. Stop at this step and hand the branch to the human with both options named:

- **They commit it themselves** — merge or cherry-pick the branch into the default branch by hand, skipping review. Reasonable for a low-stakes, first-ever change (`loop-config` itself is the common case).
- **They push and open the merge request themselves**, once forge access exists — the branch and its commits stay exactly as prepared, nothing about them changes.

Name the branch and what it contains in the closing report. Leave the candidate's own state exactly as if its merge request were still open (label, `Pending candidates`) — a later pass detects it delivered once the human's own action lands it, via `git-only-reconciliation.md`'s no-remote variant, the same as any merge request closing outside the loop's own action.
