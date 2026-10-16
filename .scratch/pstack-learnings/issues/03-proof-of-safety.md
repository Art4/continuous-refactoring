# 03 — MR report names the one safety fact and its proof level

Type: task
Status: open

Add to the MR description the single fact the change is safe because of, and how far it was proven: said, line cited, bad case excluded, ran it, reproduced. Unproven is stated as unproven. Forge-facing, so it follows the forge-facing writing rule.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

## Comments

### 2026-10-16 — gap check against `skills/`: partial

`opening-a-merge-request.md` step 3, item 3, says what changed, which checks passed and which tests cover it. It does not name the one fact the change is safe because of, nor how far it was proven. `SKILL.md` already requires every closing claim to be confirmed during the run, which is the nearest neighbour.
