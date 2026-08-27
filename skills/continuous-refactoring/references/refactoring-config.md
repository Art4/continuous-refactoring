# Reference: `docs/refactoring/config.md` in the target repo

The config file the suite reads and writes. It doesn't exist on a fresh target repo: `refactor-scan` proposes it (the `loop-config` node, `docs/tooling-tree.md`), `refactor-design` files it as a single `refactor:candidate` issue, and `refactor-implement` creates the file when that candidate is implemented — the same path any other tooling-tree node takes.

## Structure

```markdown
# Refactoring Loop Config

**Last run:** 2026-08-21
**Create-mode:** autonomous
**Focus areas:** order intake, billing
**Pending issue:** none
```

## Fields

| Field | Meaning | Written by |
|---|---|---|
| `Last run` | Date of the last completed pass | `refactor-learn` after each pass |
| `Create-mode` | How merge requests get opened: `autonomous`, `ask-each-time`, or `human-opens` | `refactor-learn` (first time it writes bookkeeping) |
| `Focus areas` | Areas scans should target first | you, any time |
| `Pending issue` | The issue `refactor-design` just filed, not yet delivered as a merge request — `none` the rest of the time | `refactor-design` sets it when it files; `refactor-learn` clears it once the merge request is remembered (`merge-requests.md`) or the candidate is resolved another way |

`Pending issue` exists so a pass interrupted between design and implement doesn't get re-proposed as fresh work by the next `refactor-scan` — scan reads this field before walking the tree, and if it's set, that pending issue is the only thing it proposes this pass.

**`loop-config` exception:** for the `loop-config` candidate itself, this file doesn't exist yet when `refactor-design` would normally write `Pending issue` — `refactor-implement` sets it directly when it creates the file instead, leaving `Last run`/`Create-mode` for `refactor-learn`'s own follow-up commit. Because the file only exists on that candidate's own (not yet merged) branch, `refactor-learn`'s writes land there too, the one time bookkeeping doesn't go straight to the default branch. Every pass after that, once the file is on the default branch, all of this is as described in the table above.

There is deliberately no `Cadence` field: the loop never triggers itself — you kick it off whenever it's due, whether that's you running `/continuous-refactoring` by hand or a scheduler you set up outside the suite. Nothing here would read a stored cadence, so nothing stores one.

## Rules

- **`Last run` is `refactor-learn`-written; `Create-mode` and `Focus areas` you can edit by hand any time** — that's what they're for.
- The file travels with the repo. Loop state does not live in agent sessions but here (last-run, create-mode, focus areas, pending issue), in the issue tracker (backlog), in `docs/refactoring/merge-requests.md` (open suite merge requests — only when the target's issue tracker has no native label mechanism; otherwise that state lives directly on the tracker as `refactor:delivered`-labeled issues), and in `docs/refactoring/out-of-scope/` (learned rejections).
- If the file is missing, that's the `loop-config` tooling-tree node — see above. Ordinary in every way except who writes which field and which branch it lands on for that one candidate — see the `loop-config` exception above.
