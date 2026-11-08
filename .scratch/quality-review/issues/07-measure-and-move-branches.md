# 07 — Measure what runs read, and move rare branches out

Type: task
Status: done
Blocked by: 05

**What to build** (spec S4.1, S4.2)

- **Measure.** From the runner's transcripts: which skill files and sections a run actually reads, per scenario.
  Record the numbers (words per file, words per run path) in this ticket, the glossary's share named on its own:
  how often a run opens it and how much of it it reads.
- **Move.** Branches a run rarely takes, such as the design point's *Planning a baseline ticket* and *Open
  questions*, go into reference files read only when their table row applies. The wording stays the same.
- Play the affected scenarios after the move.

**Done when** the numbers are recorded, the rare branches are moved, the affected scenarios pass, and tests and
validator are green.

## Comments

**2026-11-08 — measured.** From the transcripts of the 35 finished players of the first full playing and the plays
after it (2026-11-07/08): every `Read`, `cat`, `sed -n` and `head` on `skills/`, counted in words against the files
on `main` at e9a85b7, so an approximation where a file changed since.

- **A run reads files whole.** For nearly every file the words read per play match the file's size: plays do not
  pick sections, they `cat` the file. So what a run carries is decided by which files it opens, and only moving a
  branch into its own file takes it off the paths that do not need it.
- **Words per run path:** a run that scans and files (r1–r5, r7, r8) reads 16k–24k words in 15–21 files. A Driver
  play reads 2k–16k, depending on how far it follows the run; a Pack build (p1, p2) 8k–14k.
- **Read in most plays** (plays out of 35, words): run `SKILL.md` 34 (1,513), `reporting-progress.md` 32 (289),
  `worklist.md` 26 (1,140), `track-choice.md` 25 (621), `reconcile.md` 23 (556), `refactoring-operations.md` 21
  (1,934), `tooling-parser.md` 21 (1,268), `forge-facing-writing.md` 21 (262), `selection.md` 17 (643),
  `track-scan.md` 15 (1,640), Driver `SKILL.md` 15 (1,528), `opening-a-merge-request.md` 15 (1,374),
  `design-point.md` 13 (3,006), `investigation-track.md` 12 (1,101), `updating-the-base.md` 10 (1,202).
- **The glossary:** opened in 1 play of 35 (r7, before the pointer said to look a term up only where the text leaves
  it unclear), read whole: 5,235 words. After the reworded pointer, no play opened it.

**Moved,** wording unchanged:

- `design-point.md`, *Planning a baseline ticket* (636 words) → `planning-a-baseline-ticket.md`. design-point.md
  goes from 3,006 to 2,359 words for the 13 plays that read it; only a baseline ticket reads the new file.
- `refactoring-operations.md`, *Templates* with *Bullets the target chooses* (about 710 words) →
  `tracker-file-templates.md`. refactoring-operations.md goes from 1,934 to 1,221 words for the 21 plays that read
  it; the onboarding interview, a recorded rejection's **Rejected** bullet and Investigation's **Candidate** bullet
  read the new file.

About 1,350 words fewer on a scan-and-file path, some 6–8 % of it. *Open questions* stays in `design-point.md`:
filing, reconcile and step 1 all reach it, so it is no rare branch.
