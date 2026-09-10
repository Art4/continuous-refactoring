# Retroactive secret-history scan is a `refactor-scan` process step, not a tooling-tree node

## Context

`secret-detection`'s own adoption MR (Signals ticket 2, ADR-0040) deliberately scoped itself to the
CI-gate half only: block *future* secrets from landing. Its own node doc explicitly kept a retroactive
scan of the target's already-committed git history — finding secrets that landed *before* the gate
existed — as separate, real follow-up work rather than silently dropping it. `.scratch/php-tooling-
tree/issues/13` tracked that remaining half.

Unlike every other tooling-tree node in this suite, there's nothing to *adopt* here: the target
doesn't gain a new dependency, config file, or CI job — the scan is a one-time action against history
that already exists, using a scanner the target already has (from `secret-detection` itself).
Modelling it as a node anyway (its own Fulfilment check, its own adoption MR) would mismatch every
node in this tree, all of which represent an ongoing adopted capability the target keeps, not a single
action performed once and then irrelevant forever.

## Decision

The retroactive scan is a new `refactor-scan/SKILL.md` step (4c), not a tooling-tree node:

- **Trigger:** `secret-detection` fulfilled, and the Refactoring Notes' `bookkeeping.md`'s new
  `Secret history scan` field is absent. Runs at most once per target — the field flips to `done`
  once every finding from that run is filed, and nothing re-triggers it after.
- **Tool reuse, not a new choice:** the same scanner `secret-detection`'s own CI job already invokes
  (`tooling_tree.py`'s `secret-detection` node now exposes which one matched in its own `details.
  scanner`, so step 4c never has to re-derive it by re-reading CI config). No second tool, no new
  adoption decision for the target to make.
- **Dedup via the scanner's own baseline mechanism** (gitleaks `--baseline-path`, detect-secrets
  `.secrets.baseline`, or the equivalent) — a finding already known, whether filed as a candidate or
  explicitly accepted as a false positive, never resurfaces. Reusing tool-native infrastructure
  instead of this suite inventing its own dedup/allowlist mechanism.
- **Filing stays with `refactor-learn`, not `refactor-scan` itself** — `refactor-scan` is "detect,
  never write"; running a read-only scan against history fits that (it changes nothing), but filing
  the resulting candidate issues doesn't, so those findings are handed to `refactor-learn`'s early
  call exactly like every other finding type. Each finding becomes its own `refactor:priority`
  candidate (Where: file/line; Problem: the scanner's own rule/finding id, **never the secret's
  actual value**; Signal: Security) — filed directly rather than routed through `refactor-prioritize`'s
  Select mode, since there's nothing to explore or rank among: the finding is already concrete.
  Security already triggers priority admission (`signals.md`, ADR-0039), so this reuses an existing
  rule rather than inventing a new one.

## Considered Options

- **A new tooling-tree node** (`secret-history-scan` or similar), mirroring `phpmd`/`secret-detection`'s
  own shape. Rejected — nothing is actually adopted; a Fulfilment check that's true forever after one
  run, with no ongoing capability behind it, doesn't fit what a node represents in this tree.
- **Run every pass**, relying purely on the scanner's own baseline file to stay idempotent (no new
  bookkeeping field at all). Rejected — a full git-history walk isn't free, especially as a target's
  history grows; a genuinely one-time action shouldn't cost every future pass just to reconfirm
  nothing new is there.
- **`refactor-scan` files the candidate issues itself**, as a narrow exception to "detect, never
  write". Rejected — no exception needed once the finding is simply handed to `refactor-learn` like
  every other finding type; carving out a special case here would be inconsistent with the rest of
  this same step's own design without buying anything.
- **Store the "already scanned" state as a suite-side timestamp** (e.g. in a hidden file) rather than
  a `bookkeeping.md` field a human can see and, if genuinely needed, remove by hand to force a re-run.
  Rejected — `bookkeeping.md` is already the target-repo-visible home for every other one-time/state
  flag this suite tracks (`Housekeeping cadence`, `Pending candidates`); a hidden side-channel would
  be the only field working differently for no real benefit.

## Consequences

`tooling_tree.py`: `_detected_secret_scanner()` (new), `secret-detection`'s own `set_node(...)` call
now also reports `details.scanner`. `refactor-scan/SKILL.md` gains step 4c. `refactor-learn/SKILL.md`'s
early-call finding list and its own completion criterion both gain the new finding type.
`refactoring-bookkeeping.md` documents the new `Secret history scan` field (`refactor-learn`-written,
the one field a human can remove by hand to force a rare re-run). `secret-detection.md`'s own
"Out of scope" note now points at this step instead of describing it as unscheduled follow-up work.
No edge-table changes — this isn't a node, so it has no edges to declare.
