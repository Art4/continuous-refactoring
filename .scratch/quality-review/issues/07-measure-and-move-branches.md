# 07 — Measure what runs read, and move rare branches out

Type: task
Status: open
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
