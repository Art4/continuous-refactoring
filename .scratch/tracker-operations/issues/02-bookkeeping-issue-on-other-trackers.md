# 02: Bookkeeping in a ticket on trackers other than GitHub and GitLab

**Status:** needs-triage

**What to build:** Issue mode — the suite's state kept in one tracker ticket instead of local files — is written against `gh`/`glab`: load, save, one comment per learned rejection and per remembered merge request. Onboarding offers it only when the tracker is GitHub or GitLab. Generalise it so a tracker described through `## Refactoring operations` can hold the bookkeeping ticket too.

Open before this can be designed: which operations issue mode needs beyond the eight that exist (read and replace a ticket's body, list and delete single comments), and whether a tracker's markup (Textile on Redmine) survives the round trip of a Markdown document.

**Blocked by:** 01.
