Added a `CHANGELOG.md` fragment-file mechanism: noteworthy changes drop a `.changelog.d/*.md`
fragment (enforced by CI via the `no-changelog` label escape hatch), consolidated into
`CHANGELOG.md` — and the fragments deleted — at release time.
