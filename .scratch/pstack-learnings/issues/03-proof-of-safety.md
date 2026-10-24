# 03 — MR report names the one safety fact and its proof level

Type: task
Status: done — PR #158

Add to the MR description the single fact the change is safe because of, and how far it was proven: said, line cited, bad case excluded, ran it, reproduced. Unproven is stated as unproven. Forge-facing, so it follows the forge-facing writing rule.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments

### 2026-10-16 — gap check against `skills/`: partial

`opening-a-merge-request.md` step 3, item 3, says what changed, which checks passed and which tests cover it. It does not name the one fact the change is safe because of, nor how far it was proven. `SKILL.md` already requires every closing claim to be confirmed during the run, which is the nearest neighbour.

### 2026-10-17 — grilled; decisions

Only when a structural change (or a Housekeeping idea) renames, moves or deletes something that can be referred to from outside the seam; otherwise the paragraph is left out. Four steps in plain words: read in the source (file and line), shown that the bad case cannot occur, run, reproduced in the running application where cheap; "said" is no step; unproved is stated as unproved. Produced at the implement point (end of step 4), by a small script or test against the real code, thrown away unless it meets *Tests worth keeping*. Unproved: the merge request still opens and says so; for the always-ask categories (security, privacy, auth, permissions, migration, idempotency, concurrency) an open question instead. Its own item in the description, between "what changed" and "decisions", in plain words (no suite terms). Not for tooling or baseline tickets. No ADR. Built in PR "The merge request says why a change is safe".

### 2026-10-24 — closed

Built in PR #158 as recorded above; checked against `skills/` on 2026-10-24.
