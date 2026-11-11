# r10 — The frontend is already linted

Played as a walk-through.

Covers: `skills/continuous-refactoring-run/references/packs/js/pack.json`, `skills/continuous-refactoring-run/references/packs/js/eslint.md`, `skills/continuous-refactoring-run/references/worklist.md`, `skills/continuous-refactoring-run/references/track-scan.md`, `skills/continuous-refactoring-run/references/filing-a-ticket.md`, `skills/continuous-refactoring-run/references/selection.md`, `skills/continuous-refactoring-run/references/design-point.md`

## Situation

The fixture `php-js-eslint`, onboarded, on GitHub as `acme/shop`: a PHP application whose frontend JavaScript under
`public/js/` is linted by ESLint 9 with a flat config of its own, run by the CI job `lint-js`; `npx eslint .` exits
0, and there is no suppressions file. A vendored minified copy under `public/js/vendor/` is ignored by the config.
Its tracker file has no **BC promise** operation. Housekeeping is set up, and its ticket is not due. No Tooling Pack
of its own.

Every Stage of the generic and the PHP Pack, Safety Net and Guardrails, that is not on request, except `roave-bc-check`, has a closed ticket
whose merge request was merged, and what they set up runs in CI. No rejection is recorded, no ticket but the Housekeeping ticket is open, and no
ticket, plan or pull request carries an `Opener:` line.

## Call

`/continuous-refactoring-run autonomous`

## Expected

- [ ] The worklist judges that the generic, the PHP and the JavaScript Pack apply; Guardrails has no trace, and its
      scan is due.
- [ ] The scan judges `eslint-adoption`, `eslint-suppressions` and `eslint-rollout` fulfilled: the target keeps its
      own config, and none of its rules is marked `Not yet:`. It proposes no ticket to work.
- [ ] Filing creates one ticket for ESLint and closes it at once as done, its text naming the config and the CI job
      and the three Stages with their search words.
- [ ] The run goes on to Track choice with Guardrails marked as tried, and proposes nothing about the project's ESLint
      config.

## Results

2026-11-08, on b36de5e, the scenario's first playing: pass, every line, as a walk-through. Then `eslint.md` was made explicit where the play had to infer: the adoption's config carries the rollout's rules as `Not yet:`, and an existing config without them fulfils the rollout.
