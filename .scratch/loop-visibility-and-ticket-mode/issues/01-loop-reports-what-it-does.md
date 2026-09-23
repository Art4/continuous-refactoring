# 01: The loop says what it is doing, before and after every step

**What to build:** Today the loop announces the pass start, the scan and implement subagents, and every early stop. Prioritise, Design, both Learn calls and every write to the target (ticket creation, push, merge request, bookkeeping merge request) run silently. Make the progress visible.

**Status:** done — PR pending

## Decided behaviour (grilled with the maintainer)

- **Rule, in `refactor-loop`:** one sentence before each step (what starts), one sentence after it (the result — e.g. "Scan: 4 nodes proposed, no findings", "Chosen: <Name>, because …"). Every write to the target's forge or repo is reported on its own: ticket created, branch pushed, merge request opened, bookkeeping merge request.
- The closing report stays two lines (Status / Next); it does not repeat the per-step sentences.
- **Only the loop reports**, after the subagent returns. Subagents get no live channel; each lifecycle skill's `## Output` lists the writes it made so the loop can name them.
- **Housekeeping** follows the same rule in its own process. The rule lives in one shared reference that `refactor-loop` and `continuous-housekeeping` both point at, not copied twice.
- No schema change; skill prose and docs only. The "ticket created" line is added by 02 once the loop creates tickets.

## Docs that must read true afterwards

`docs/playbooks/loop.md`, `docs/architecture.md`, `README.md` ("How it works"), plus a `.changelog.d/` fragment.

## Acceptance

- Each of the six loop steps has a before and an after line in `refactor-loop/SKILL.md`; a dry run of one pass shows them in order.
- Each skill's `## Output` names the writes it made.
- `continuous-housekeeping` follows the same rule via the shared reference.
- `python3 -m unittest discover -s scripts -p 'test_*.py'` and `python3 scripts/validate_skills.py .` pass.
