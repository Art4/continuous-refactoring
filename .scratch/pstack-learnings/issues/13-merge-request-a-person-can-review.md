# 13 — A merge request a person can review

Type: task
Status: open

Found in a real run on a Rector ticket: a tooling ticket produced one merge request of 221 files and 69 commits, and a later plan for a similar ticket planned one merge request of about 144 files without weighing whether a person can review it. The node's MR scope ("adopted in levels, one MR per level") does not bound the size, and nothing in the skills asks the plan to estimate it or to cut it.

Add a principle (not a rule): estimate the size, cut at a seam of kind or risk, each part green and worth merging alone, the plan states the cut and why in one sentence; a node's MR scope is the most one merge request holds, never the least. Parts use the existing "part" mechanism (ticket stays open, merge request names the ticket with the word "part").

## Comments

### 2026-10-17 — draft built, to be checked by a second planning run

Built as a draft before grilling so a second plan run on the same ticket can compare against the first (which planned one merge request): `principles.md` (*A merge request a person can review*), `design-point.md` (*Planning a tooling ticket*: estimate, cut, parts listed in order, a later run takes the first part not yet on the default branch), `opening-a-merge-request.md` (a tooling ticket's part). Open for the grilling after the comparison: a number as anchor or none; whether the review should flag a branch that mixes kinds beyond the plan's cut; baseline tickets (already cut by part); structural tickets.
