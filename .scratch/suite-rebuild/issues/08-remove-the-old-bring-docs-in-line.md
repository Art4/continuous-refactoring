# 08: Remove the old, bring the docs in line

**What to build:** The repository holds two skills and their references, and nothing of the nine removed
skills. A human reading the README, the architecture page, the playbooks, the FAQ and the known
limitations learns the suite as it now works, including how to install it and how to move a target over
from 0.6.0.

Spec: `../spec.md` (sections *Shape of the suite*, *Onboarding and existing targets*, user stories 45–49).

**Blocked by:** 05, 06, 07

**Status:** done

- [x] The skills `refactor-loop`, `refactor-scan`, `refactor-prioritize`, `refactor-design`,
      `refactor-implement`, `refactor-learn`, `continuous-safety-net`, `continuous-guardrails`,
      `continuous-investigation` are gone; the tooling-tree files and the parser live under a skill that
      remains
- [x] No remaining skill text or reference points to a removed file, to bookkeeping, a config file, a
      cadence or a cap
- [x] The **Comment author and time** operation is removed from the operations reference, its templates,
      the onboarding interview and the glossary, unless ticket 07's comments say Housekeeping reads it
- [x] `README.md`, `docs/architecture.md`, `docs/playbooks/`, `docs/FAQ.md`, `docs/known-limitations.md`
      and `CONTRIBUTING.md` read true against the rebuilt suite, in their own words, citing no ADR, ticket
      or scratch path
- [x] The install instructions name two symlinks
- [x] The known limitations state: a freely written ticket on a large tracker is found only through a
      **Candidate** hint or by being named; parallel merge requests may conflict and resolving that is the
      developer's; a target that is not a PHP project never gets a fulfilled Safety Net gate, so an
      autonomous run stops there; on a tracker strangers can write to, an autonomous Housekeeping run
      weighs a stranger's comment as a proposal like anyone's, carries it out only as a behaviour-keeping
      refactoring, and delivers it in a merge request a human reviews; with a daily rhythm the re-check
      of the tooling Tracks runs daily unless the human moves that task into a rarer template
- [x] `AGENTS.md`'s description of the suite matches the two skills
- [x] A changelog fragment marks the rebuild as breaking for 0.7.0 and lists the steps for an onboarded
      target: run onboarding again, delete the old files under the suite's scratch folder (or name the old
      rejections folder under **Rejected**), remove the symlinks of the removed skills
- [x] No test is written or changed; which checks are red afterwards is listed in a comment on ticket 09

## Comments

Done on `suite-rebuild`.

### What exists now

- **Moved** from `skills/refactor-scan/references/` to `skills/continuous-refactoring/references/`:
  `tooling_tree.py`, `tooling-tree.md`, `php-tooling-tree.md`, `tooling-tree/`, `php-tooling-tree/`.
  `tooling-tree-parser.md` names the new place in its two lines. The parser's output for this repository
  is byte-identical before and after the move and the tree-doc edits.
- **Deleted:** the nine skills with all their references, and `refactoring-bookkeeping.md` and
  `remote-bookkeeping.md` under `continuous-refactoring/references/`.
- **Tree docs** (both tree files and every node file): no pointer to a deleted file is left. Old terms
  replaced: Signal wave → Guardrails, pass → run or scan, the loop → the suite, Select mode → the search
  for structural candidates, Refactoring Notes / `out-of-scope/` → a recorded rejection.
- **Comment author and time** removed from `refactoring-operations.md` (table, GitHub and GitLab
  template), the interview and the glossary.
- **Human docs** written new: `README.md`, `docs/architecture.md`, `docs/playbooks/run.md`,
  `docs/playbooks/tracks.md`, `docs/playbooks/housekeeping.md`, `docs/FAQ.md`,
  `docs/known-limitations.md`. Changed in place: `CONTRIBUTING.md`, `AGENTS.md`,
  `docs/agents/skill-references.md`, one word in `docs/playbooks/reviewer-loop.md`.
- **Changelog fragment:** `.changelog.d/suite-rebuild.md`.

### One limitation is worded differently from this ticket

The ticket asks the known limitations to say that a target that is not a PHP project "never gets a
fulfilled Safety Net gate, so an autonomous run stops there". Against the skill texts that holds only
for a run that scanned. Tried with the parser on an empty non-PHP repository:

- with the seed a **scan** produces (PHP leaves undecided), `structural-scan` is not fulfilled;
- with the **seed from the trace** (`tooling-tree-parser.md`: every node of the Track without an open
  ticket is handed in as fulfilled), `structural-scan` is fulfilled.

So: where the first scan files tickets for `.editorconfig` or the CI pipeline, the Track has a trace,
and once those tickets are closed a later autonomous run counts Safety Net as fulfilled and moves on.
The stop is permanent only where both language-neutral tools were already in place — nothing is filed,
no trace arises, every run scans again. `docs/known-limitations.md` and
`tooling-tree/is-php-project.md` say it this way. The behaviour itself is not changed here; whether
the trace seed should take a node behind an unfulfilled recognition-only node as done is for the
acceptance run (noted on ticket 09).

### Decided here, not stated by the spec

**Move and delete**

- The parser and the tree docs lie flat in `continuous-refactoring/references/`, beside
  `tooling-tree-parser.md`, not in a subfolder.
- Two docstrings of `tooling_tree.py` no longer name the deleted Outlook reference, and four comments
  lost old words (pass, loop, Signal wave). No code line changed. `directly_unblocked_children` and
  `--unblocked-by` stay, although nothing in the suite calls them any more: removing them would break
  their tests.
- Nothing of the nine skills was carried over into a new reference. `never-delete-without-record.md`,
  `phpstan-baseline-shrink.md`, `baseline-shrink-selection.md`, `outlook-comment.md` and the rest were
  covered or dropped by tickets 04 to 07.

**Tree docs**

- `onboarding-setup`: fulfilled by the `## Refactoring operations` section, settled by the parser.
- `structural-scan`: described as the Safety Net's gate, never a ticket. Its old MR scope (proposed
  like a node, then turned into a candidate) is gone; Investigation is no longer held back by it.
- `is-php-project`, *Known gap*: rewritten to what happens now (out of reach in a scan).
- `secret-detection`: the scan over the Git history is named as a Housekeeping task; the node's own
  merge request scans the working tree once.
- `php-tooling-tree.md`, *PHP floor precheck*: the old "skip silently, write no rejection" is replaced
  by what `rejection.md` does — a scan proposes a rejection carrying the PHP version as its blocker.
- `psalm`, *Mutual exclusion*: the old instruction that the scanning agent writes a rejection of
  `phpstan-level-5` by itself is gone, since a scan writes nothing. On a Psalm-only target the PHPStan
  levels above 0 are out of reach in a scan and get no ticket; `phpstan-level-5` then counts as done
  through the Track's trace. Within the run that scanned, the gate stays unfulfilled.
- `php-minimal-version`: its **Housekeeping** field is worded without the parser's names; *Re-triggering*
  points to a scan on request and Housekeeping's re-check; the reversal bullet uses `Blocker: PHP >= X.Y`.
- `phpstan.md`, *Stop conditions*: the baseline points to `track-scan.md` step 4 and `design-point.md`.
- Left as it is: the history the tree docs tell about themselves ("renamed from", "moved out of the
  Safety Net", "no longer a leaf"). It names no deleted file and no old term; pruning it is a rewrite of
  the tree docs, which the spec carries over as content. The node headers still point to `CONTEXT.md`,
  which does not ship with the skills.

**Comment author and time**

- The interview also removes that bullet from an existing section, next to **Bookkeeping** and **Filed
  date**, so a target moving over ends with a section in the new cut.

**Glossary**

- **Aggregation node** now says "closed by a rejection" (ticket 11's comment named the old clause as
  untrue). Nothing else in `CONTEXT.md` changed beyond the operation's removal.

**Human docs**

- `docs/playbooks/loop.md` is renamed to `docs/playbooks/run.md`.
- The README has a section *Moving over from 0.6.0* and *Where things live* in place of *Loop state*. To
  keep the rule "no `.scratch/` paths", README and FAQ name the old files (`config.md`, `bookkeeping.md`,
  `merge-requests.md`, `out-of-scope/`) "in the suite's scratch folder"; the full paths are in the
  changelog fragment only.
- Step 2 of moving over excludes the local tickets folder: on a Local Markdown target the tickets live
  under the same scratch folder and are still read.
- The install instructions add that the two symlinks sit side by side, because
  `continuous-housekeeping` reads files of `continuous-refactoring` through a relative path.
- The engineering-skills note in the README now says what they still give: the tracker file, the domain
  docs, and skills a run offers at the design and implement point. The old setup-gap question is gone.
- Known limitations: beyond the five the ticket lists, one more is new ("a proposal you did not file is
  not remembered"). Gone with their mechanisms: the ledger file, where the state lives, the create-mode
  defaults, the implement hand-back, the cadence arithmetic, the GitHub labels, remote bookkeeping.
  "Without `gh`/`glab`" shrank to: merge requests are read through the tool the tracker file names.
- The troubleshooting table is built from the endings the skill texts have.
- FAQ, "Can I run the onboarding again?": it runs by itself when a required operation is missing; on a
  complete section the interview ends at once, so the answer is to edit the tracker file.
- FAQ counts the earlier suite as eleven skills (the nine removed and the two kept); the spec says ten.
- `docs/agents/skill-references.md` now states that no suite skill names a global skill.
- `docs/playbooks/reviewer-loop.md` keeps its line about the reviewer's own findings log under a scratch
  folder: it is where a reviewer writes, not a pointer to a ticket of this repository.
- `AGENTS.md`: the "Docs stay in sync" list names `run.md` and "a run" instead of the cadence and "a
  pass". The Git-workflow section still says every change needs a branch and a pull request, although
  this work was committed on `suite-rebuild` as told.

**Changelog fragment**

- One fragment for the whole rebuild, two paragraphs: what changed, and the three steps. It is longer
  than "one short sentence or paragraph" and carries "**Breaking, for 0.7.0:**", following the 0.6.0
  entry and this ticket's criterion.
- Beyond the three steps it says: a rejection that should come back by itself needs a line
  `Blocker: PHP >= X.Y` (0.6.0 wrote `**Blocked by:** PHP >= …`), and a tracker issue that held remote
  bookkeeping can be closed.

### Review

Reviewed on two axes before the commit. Taken over: old words in four parser comments; the interview
removing the **Comment author and time** bullet (the fragment claimed it did); the FAQ's answer on
running the onboarding again; the skill count; the heading and the trace distinction of the non-PHP
limitation; "rejection" dropped from the vocabulary list in `AGENTS.md`; an avoided term ("acceptance
criterion") in the architecture page; relative pointers in two node files; "the suite's own state" in
the `onboarding-setup` Tool line; three loose wordings in README and playbooks.

### Red afterwards

The full list is in a comment on ticket 09.
