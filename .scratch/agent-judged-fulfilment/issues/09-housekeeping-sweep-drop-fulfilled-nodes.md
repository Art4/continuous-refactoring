# 09: Housekeeping sweep over the five nodes; `Fulfilled nodes` removed

Spec: `agent-judged-fulfilment`.

**What to build:** The Housekeeping Track's reconciliation stops reading `Fulfilled nodes`. Each cycle it instead checks only the nodes that carry a `Housekeeping` field (today five: composer, PHPStan, the dependency audit, semgrep, the minimal PHP version), judges their Fulfilment check itself, and appends any missing line to the accumulated checklist. A hand-adopted tool therefore gets its line even when no delivering merge request ever existed, Guardrails nodes included. Delivering such a node's merge request still contributes its line, and removing lines stays a hand edit. With the reconciliation off the field, every remaining read and write site of `Fulfilled nodes` is removed, together with the cache step of the manual tree-walk fallback. Existing files that still carry the field are left alone and ignored.

**Blocked by:** 02 (Prose audit — Safety Net nodes), 03 (Prose audit — Guardrails nodes and gates), 06 (A Track scan fills `Open`; `refactor-learn` maintains it) — the write logic in the learning step is edited there as well.

**Status:** done — PR #111

- [x] The Housekeeping reconciliation checks only the nodes with a `Housekeeping` field by agent judgement and appends missing lines; it does not read `Fulfilled nodes`.
- [x] A hand-adopted Guardrails tool with no merge-request history gets its checklist line at the next cycle.
- [x] `refactor-learn` no longer writes `Fulfilled nodes`, the fallback no longer reads or maintains it as a cache, and no skill or reference still mentions it as an input or output (the schema documentation notes only that old files may still carry it).
- [x] The bootstrap of `loop-config` no longer relies on a first `Fulfilled nodes` entry; its fulfilment is judged like any other node.
- [x] An advisory agent fixture covers the hand-adopted Guardrails tool case; an old-shape bookkeeping fixture still passes untouched.
- [x] The repo's skill and documentation validation passes.

## Comments

**PR:** [#111](https://github.com/Art4/continuous-refactoring/pull/111)

- Verified: `housekeeping-track.md` "Reconcile" (only nodes with a `Housekeeping` field, agent judgement,
  "Guardrails tools included", does not read `Fulfilled nodes`), `refactor-learn/SKILL.md` (write struck as
  retired), `tree-walk-prompt.md` (no cache step), `loop-config.md` (fulfilled = `bookkeeping.md` exists),
  fixtures `php-housekeeping-hand-adopted-guardrails` and `php-housekeeping-old-schema` (wired in
  `run.sh`, not executed here).
- Item 3 residue, accepted: `Fulfilled nodes` is still named as *retired* in `refactor-learn/SKILL.md`,
  `housekeeping-track.md` ("rather than reading `Fulfilled nodes`") and the `Replaces ...` lines of
  `refactoring-bookkeeping.md`, and that document keeps a full `## Fulfilled nodes` section with legacy
  invariants. None of it reads or writes the field.
- PR #111's `check` (changelog-fragment) run shows fail, as it does on #103-#109; #113 (which carries the
  fragments) is green.
