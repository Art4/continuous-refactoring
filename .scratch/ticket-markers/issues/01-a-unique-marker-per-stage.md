# 01 — A unique marker per Stage in the ticket text

Type: task
Status: open
Blocked by: —

**The idea** (maintainer, 2026-11-11). A ticket the suite files carries a marker no other ticket has, for example
`<!-- continuous-refactoring:stage:eslint-adoption -->`, and **Search** looks for the marker first. It came up while
plays kept naming sibling hits: filing's search for "ESLint" also found "ESLint: clear the suppressions" and "ESLint:
take in the remaining rules", and Rector's in-place ticket found the other Rector tickets. quality-review Q51 settled
the acute case with the Name: filing keeps only hits that match the Stage as the worklist's rule says.

**What it would give**

- An exact hit for one Stage: no sibling confusion, independent of the title, of the language the human writes in,
  and of a title a human renamed.
- The slug stays out of the text a human reads, where a hidden comment renders.

**Open before deciding**

1. **Does search reach an HTML comment?** On GitHub and on GitLab, for issues and for merge requests. Existing
   tickets could not settle it: every word tried stood outside the comment too. A test needs one issue per forge with
   a word that stands only inside a comment, filed and closed again, with the maintainer's leave.
2. **Other trackers.** Redmine, Jira and Textile escape HTML, so the marker would show as text there. Either the form
   is set per tracker in `## Refactoring operations` (a new operation, or a part of **Search**), or the marker is a
   visible line like the existing `Search words:` and `Opener:` lines. A local-file tracker is searched with `grep`
   and takes either form.
3. **Old and hand-made tickets carry none.** The search by Name stays as the fallback, so the marker adds a step and
   replaces none; the worklist, filing, the trace and the Opener search would each learn "marker first, then Name".
4. **Tokenizing.** GitHub splits at punctuation, so the marker is searched as a quoted phrase, and its words must not
   match a sibling's (`eslint-adoption` against `eslint-suppressions` holds; a slug that is a prefix of another may
   not).
5. **What else it names.** A Stage alone, or also a Tool (in-place tickets), an Opener, a rejection, a Housekeeping
   ticket. And whether `Search words:` then goes.

**What to build**, once 1 to 5 are decided: an ADR; the marker in `filing-a-ticket.md` and the templates
(`tracker-file-templates.md`); "marker first" in the worklist, the trace and filing's search; scenarios that play a
ticket with and one without a marker; a changelog fragment.

**Done when** the search test is recorded, the decisions are in an ADR, and the scenarios pass.
