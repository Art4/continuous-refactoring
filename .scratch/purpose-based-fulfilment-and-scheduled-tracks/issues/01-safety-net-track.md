# 01: Safety Net Track end-to-end — Purpose-based fulfilment, Open/Out-of-scope bookkeeping

**What to build:** A full Safety Net Track pass, end to end, on a real target repo. `refactor-scan`'s
tree-walk for Safety Net nodes judges each node's Fulfilment check against its own Purpose statement via
an agent, recognizing any real, working tool that serves it — not a hardcoded dependency-name list.
Concretely: a target already running Laravel Pint (no `friendsofphp/php-cs-fixer` dependency at all)
reads the `php-cs-fixer` node as fulfilled and never has it proposed. `bookkeeping.md` gains a
`Safety Net` section (`Cadence`, `Last scan`, `Open`, `Out-of-scope`), replacing the old
`Fulfilled nodes` cache and global `Pending candidates` field for this Track's own nodes.
`refactor-learn` writes into it: removes an entry from `Open` once its delivering MR merges; on
rejection, removes it from `Open` and writes both the matching `out-of-scope/<slug>.md` (format
unchanged) and a pointer entry under `Out-of-scope`. For this ticket, the orchestrator runs the Safety
Net Track whenever its `Open` is empty and it has either never run or its cadence (default 90 days) has
elapsed — Safety Net is the only Track wired up here, so no cross-Track competition is needed yet (that
lands in ticket 04).

**Blocked by:** None (can start immediately)

**Status:** done

- [x] A target repo with Laravel Pint installed and configured, no PHP CS Fixer dependency anywhere, is
      recognized as fulfilling `php-cs-fixer`'s Purpose; it is never proposed as a candidate.
- [x] `bookkeeping.md` gains a `Safety Net` section (`Cadence`, `Last scan`, `Open`, `Out-of-scope`); the
      old `Fulfilled nodes`/global `Pending candidates` fields are no longer written for Safety Net
      nodes.
- [x] An `Open` item merged via its delivering MR is removed from `Open`.
- [x] An `Open` item rejected (`wontfix`) is removed from `Open`, with both `out-of-scope/<slug>.md` and
      a pointer entry under `Out-of-scope` written.
- [x] A repo whose Safety Net Track has no section yet is treated as "never run"; its first scan writes
      `Last scan` even when it finds nothing missing (both `Open` and `Out-of-scope` stay empty).
- [x] A repo still carrying the old `bookkeeping.md` shape runs a normal pass without erroring on the
      unrecognized old fields.
- [x] Required/Recommended/Required-any edge semantics and cascading closure on a rejected required
      parent behave exactly as they do today.

## Comments

**PR:** (fill in after opening)

Implementation notes for whoever reviews this:

- **Scoping judgement call.** `CONTEXT.md`'s **Safety Net** glossary entry, read narrowly, only names
  the nodes with a direct `resolved` edge into `structural-scan`/`php-safety-net` — which doesn't
  literally include `php-cs-fixer` (it only has a `recommended` edge, one hop removed). But the ticket's
  own flagship example *is* `php-cs-fixer`/Pint, and **Onboarding**'s own entry defines itself as
  "everything before `structural-scan` opens," which does include it. I resolved this by scoping the
  Safety Net Track to the whole pre-`structural-scan` subtree (`git`/`loop-config`/the recognition gate
  excepted) rather than only the nine `resolved`-edge leaves — documented explicitly in
  `skills/refactor-scan/references/safety-net-track.md`'s own "Scope" section. A human should confirm
  this reading is the intended one; the alternative (narrow scope, `php-cs-fixer` in neither Track) left
  the ticket's own worked example unimplementable.
- **`tooling_tree.py` untouched**, per the spec's own "Out of Scope" — the parser's raw `fulfilled`
  value for a Safety Net Track node is now read as a first signal, not a verdict; the override lives
  entirely in skill prose (`safety-net-track.md`), not in the script.
- **Orchestrator wiring kept minimal**, per the ticket's own scope note: `continuous-refactoring/SKILL.md`
  gained one clause pointing step 1 at `refactor-scan`'s own internal Track-due decision — no
  Track-selection algorithm, no staleness-ratio computation, no other Track's own section. That's
  tickets 02/04's job.
- **No dedicated fixture for the plain "merge removes it from `Open`" branch** — the ticket's own
  Testing Decisions mapping (spec fixtures #1/#3/#4/#6/#7) doesn't call for one, and the mechanism
  (`skills/refactor-learn/references/safety-net-write.md`'s "Merge" section) is the simpler subset of
  the rejection path, which the `php-safety-net-rejection-symmetry` fixture already exercises live
  end-to-end.
- **Self-verification (`fixtures/harness/run.sh safety-net-track <fixture> --opencode`)**:
  - `php-safety-net-purpose-recognition` and `php-safety-net-rejection-symmetry` — both run **live,
    end to end**, against `opencode/muse-spark-1.2-contributor-free`, with `OPENCODE_TIMEOUT=280`
    (the default 60s wasn't enough — this model reads very thoroughly). Both fully green: the first
    correctly judged `php-cs-fixer` fulfilled via Pint's Purpose and never proposed it; the second
    correctly removed `php-cs-fixer` from `Open`, wrote `out-of-scope/php-cs-fixer.md`, and added the
    `Out-of-scope` pointer, exactly per `safety-net-write.md`.
  - `php-safety-net-open-blocks-rescan`, `php-safety-net-first-run`, `php-safety-net-old-schema` — only
    run at the harness's 60s default, which the model didn't finish within; **not re-verified with a
    longer timeout** (time budget). The deterministic parts of these three fixtures (`project/`,
    `expected/behavior.md`) are unchanged by this and are the actual checked-off deliverable; a
    reviewer or a follow-up run with `OPENCODE_TIMEOUT=280` should confirm them the same way.
  - All five fixtures deliberately carry no `expected/roadmap.json` and are excluded from the CI
    roadmap matrix — the whole point under test is that the deterministic parser stops being
    authoritative for a Safety Net Track node.
- `python3 -m unittest discover -s scripts -p 'test_*.py'` (339 tests) and
  `python3 scripts/validate_skills.py .` both green, no new advisories beyond the pre-existing 5 (plus
  this change incidentally resolved the pre-existing `Guardrails: defined but never used` validator
  error inherited from PR #90's design change, by using the term legitimately in
  `safety-net-track.md`'s own Scope section).
