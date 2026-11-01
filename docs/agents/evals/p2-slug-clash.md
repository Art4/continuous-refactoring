# p2 — A slug that clashes with the suite's

Played live.

## Situation

A copy of the fixture `php-own-pack-clash`: its Pack reuses the slug `phpunit` of the suite's, and the parser ends in
exit code 2 on it. The human's wish is a Pack with that Tool; nothing has been delivered yet.

## Call

`/continuous-refactoring-run a Pack of its own, finish the one in docs/agents/tooling-pack/ and deliver it, do it yourself`

## Expected

- [ ] It runs the parser with `--own-pack` and sees exit code 2, with both places named.
- [ ] It delivers nothing while the parser refuses the Pack.
- [ ] It renames the slug in the target's own Pack. No file of the suite changes, and it does not try to get around
      the check.
- [ ] Anything that named the old slug in the Pack follows the rename.
- [ ] The next parser call exits 0, and only then is the branch handed on.
- [ ] The report names the rename and why it was needed.

## Results

2026-11-01, skill commit d53ce5f: pass, every line. Renamed `phpunit` to `my-phpunit` in `pack.json` and the Tool file; the parser's exit 2 then exit 0 confirmed by a call afterwards. The branch held the first commit before the check refused it, but nothing was handed on until it passed.
