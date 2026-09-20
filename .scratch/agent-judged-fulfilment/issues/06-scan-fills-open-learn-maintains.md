# 06: A Track scan fills `Open`; `refactor-learn` maintains it

Spec: `agent-judged-fulfilment`.

**What to build:** A scan of a Safety Net or Guardrails Track evaluates every node of the Track's scope by agent judgement (all Fulfilment checks, including the gate nodes), hands that fulfilled set to the script, and records every unresolved node of the scope into the Track's `Open` in the script's order, blocked nodes included. A completed scan still records `Last scan`, even when everything is already resolved. Afterwards `Open` is kept up to date: a merged candidate leaves `Open`; a rejection leaves `Open`, writes the recorded rejection and the `Out-of-scope` pointer as today, and every node closed by the rejected ancestor (as reported by the script) also leaves `Open`, with no new files. Reversing a rejection makes the next scan bring those nodes back. The manual fallback follows the same steps by hand.

**Blocked by:** 02 (Prose audit — Safety Net nodes), 03 (Prose audit — Guardrails nodes and gates), 04 (`Open` as the complete backlog), 05 (Script reduced to graph logic).

**Status:** implemented — PR #108, open items listed in Comments

- [ ] A scan of a Track writes `Open` containing every unresolved scope node in the script's order (blocked ones included), leaves `Out-of-scope` as recorded, and writes `Last scan`.
- [x] A scan that finds every scope node resolved writes `Last scan` and an empty `Open`.
- [x] Merge of a Track candidate removes its entry from `Open`.
- [x] Rejection removes the entry, writes the recorded rejection and the `Out-of-scope` pointer, and removes every node closed by that rejection without writing further files.
- [x] After a rejection is reversed, the next scan re-adds the reopened nodes to `Open`.
- [x] Bookkeeping in the old shape or with an old-meaning `Open` is not migrated and does not cause an error; a selected Track with such an `Open` works it like any other (no forced rescan, also not via a manual Track override), and the scan that runs once `Open` is empty corrects it.
- [x] Advisory agent fixtures cover: populating `Open` with blocked nodes in order, the rejection cascade and its reversal, and old-shape pass-through. The manual fallback's prose describes the same steps.

## Comments

**PR:** [#108](https://github.com/Art4/continuous-refactoring/pull/108)

- Verified: `safety-net-write.md`/`guardrails-write.md` (merge, fulfilled-at-pick-up, rejection with
  `closed_by_rejection()` closures and no new files, reversal, `Last scan` incl. the all-resolved empty-`Open`
  case, old-schema section), `tree-walk-prompt.md` ("Filling `Open`"), and fixtures
  `php-guardrails-scan-fills-open`, `php-safety-net-rejection-cascade` (incl. the reversal half),
  `php-safety-net-old-meaning-open`, `php-safety-net-old-schema`, `php-guardrails-old-schema`, all wired in
  `run.sh`. The agent fixtures were not executed here (they need opencode and model credentials).
- Item 1 not met, the prose does not yet say cleanly that a scan records the whole ordered backlog:
  - `safety-net-track.md` and `guardrails-track.md` "Filling `Open`" describe it, but their "Proposing and
    recording" sections still say only unresolved, *currently unblocked* nodes are proposed and added to
    `Open`, and their "Judging fulfilment" sections still open with "run `tooling_tree.py` ... its
    `detected` map is a first signal" and "the parser's own signal still counts".
  - `refactor-scan/SKILL.md` step 4 runs the script without a seed and reads `next`; it never tells the
    scan to write the fulfilled set as a seed file or to read `backlog`. Without a seed an empty-`Open`
    Track derives every node as fulfilled (see ticket 05 item 2).
  - `safety-net-write.md`/`guardrails-write.md` state the merge/rejection/reversal/`Last scan` writes but
    never instruct `refactor-learn` to write the script's `backlog` into `Open` after a scan.
