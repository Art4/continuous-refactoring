# Reference: planning a baseline ticket

The design point's plan for a baseline ticket (`design-point.md`, steps 1 and 3). A part has no Housekeeping slice:
the adoption carried it.

"PHPStan Level N: shrink the baseline" stays open until the baseline is empty, and takes one merge
request after another. Each run plans the next **part**.

1. Read `phpstan-baseline.neon` and group its entries by root cause: the same message pattern and
   identifier, across files. `$db might not be defined` in nine files is one group.
2. The ticket's newest plan names a group that still has all its entries → that plan stands, and no new
   one is written.
3. Otherwise pick this merge request's part, and give it a name of two or three words: the group that touches input from outside the application
   first; else the group one fix removes the most entries of. A group too large to review in one merge
   request is cut by file, and the plan names the files of this part.
4. Read every file of the part and plan the fix that removes the finding at its cause. Entries are
   removed by fixing code; an `ignoreErrors` entry moved elsewhere or an inline ignore is no fix.
5. `Done when`: the baseline, regenerated, no longer holds the part's entries, is shorter than before,
   and the test suite is green. `This merge request` names the part and counts the entries that stay.

The regenerated baseline may hold a new entry — a finding the fix surfaced and cannot remove — as long as
it is shorter overall. The merge request names each new entry and its reason. When the baseline would not
become shorter, or a finding is to be ignored for good, the ignore rule goes into `phpstan.neon` instead,
and only after the human allows it: that is an open question, and the run ends with it named.

The ticket "PHPMD: take in the remaining rules" is planned the same way, with the rules in place of the groups: a rollout ruleset exists → its rule is this merge request's; otherwise read the `<exclude>` entries marked `Not yet:` in the PHPMD config, count the findings of each rule with the rule included, and take the one with the fewest (`packs/php/phpmd.md`, *Taking in a rule*). The part is that rule whole, or its next path step, or its last. *Done when* PHPMD reports nothing with the main config and with the rollout ruleset where it is left, the rule's `<exclude>` is gone after its last part, and the test suite is green. `This merge request` names the rule, the paths of the part, and the paths and rules that stay.

The ticket "PHP CS Fixer: take in the remaining rules" is planned the same way, with the rule in progress in place of the group (`packs/php/php-cs-fixer.md`, *Taking in a rule*). A rollout file exists → its rule is this merge request's; otherwise measure the rules marked `Not yet:` in the main config and take the one in the fewest files. The part is the next path step of that rule, or its last. *Done when* `check` reports zero diffs with the main config and with the rollout file where it is left, `php -l` on the floor PHP passes over the changed files, and the test suite is green. `This merge request` names the rule, the paths of the part, and the paths and rules that stay.

The tickets "ESLint: clear the suppressions" and "ESLint: take in the remaining rules" are planned the same way, with a rule's suppressions or a rule's path step as the part (`packs/js/eslint.md`). *Done when* `npx eslint .` exits 0, the part's entries are gone from the suppressions file or its rule is on for the part's paths, and the test suite is green.

A group that only a behaviour change could remove is skipped and named in the plan under `Decisions`.
When only such groups are left, the first of the *Two findings* applies (`design-point.md`, step 4): the baseline cannot become
empty, so the level above cannot be raised. The open question names what follows from each answer. Where a
human then chooses the rejection, it is that of the next level's Stage, with this as its reason
(`rejection.md` then deals with the levels above it), and the baseline ticket is closed with a note
pointing to it.
