# Orchestration Reference

Details the orchestrator carries — state, merge-request rules, closing report.

## Loop state

State lives in the target repo, not in the conversation:

- **Config** — `docs/refactoring/config.md`: focus areas, create-mode, pending candidates, fulfilled nodes, skip streak. See `refactoring-config.md`.
- **Remembered merge requests** — issues labeled `refactor:delivered` (GitHub/GitLab), or `docs/refactoring/merge-requests.md` (local tracker).
- **Backlog** — `refactor:*` issues on the issue tracker.
- **Learned rejections** — `docs/refactoring/out-of-scope/` entries from prior passes.

## Opening a merge request

- Read the target repo's `AGENTS.md` / `CLAUDE.md` first. If either names a mode, follow it.
- Neither does → propose `autonomous`; `refactor-learn` records the mode.
- Skills always say **merge request**; conversation with the human uses the forge's native word.

**Stacking rule:** While fewer than two suite merge requests are open, always stack (base = current suite branch) rather than branching off the default. Never two open against default at once.

**Description format:** Plain language (what this unlocks), then plain facts (link to candidate, changes, tests, CI). For a tooling-tree candidate, close with outlook: next node by Name, its Purpose worked into one sentence.

## Closing report

Two lines wherever the pass ends:

- **Status:** what happened this pass.
- **Next:** what the human can or should do now.

Examples:
- No git: "Status: no git repository found. Next: initialize git, then rerun."
- Backlog full: "Status: 2 merge requests already open. Next: review/merge one."
- Candidate delivered: "Status: delivered PHPStan Level 0 — MR #12 open. Next: review and merge."

## Completion criterion

One full pass completed — `refactor-learn` ran at least once, `Fulfilled nodes` written, outcome recorded.
