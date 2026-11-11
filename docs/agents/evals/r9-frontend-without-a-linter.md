# r9 — The frontend has no linter

Played as a walk-through, once per variant.

Covers: `skills/continuous-refactoring-run/references/packs/js/pack.json`, `skills/continuous-refactoring-run/references/packs/js/eslint.md`, `skills/continuous-refactoring-run/references/worklist.md`, `skills/continuous-refactoring-run/references/track-scan.md`, `skills/continuous-refactoring-run/references/filing-a-ticket.md`, `skills/continuous-refactoring-run/references/selection.md`, `skills/continuous-refactoring-run/references/design-point.md`

## Situation

The fixture `php-js-plain`, onboarded, on GitHub as `acme/shop`: a PHP application whose frontend is plain
JavaScript under `public/js/`, loaded by `<script>` tags in `templates/cart.php`, with a vendored minified copy
under `public/js/lib/`. No `package.json`, no build step, no `browserslist`; its tracker file has no **BC promise**
operation. Housekeeping is set up, and its ticket is not due. No Tooling Pack of its own.

Every Stage of the generic and the PHP Pack, Safety Net and Guardrails, that is not on request, except `roave-bc-check`, has a closed ticket
whose merge request was merged, and what they set up runs in CI. No rejection is recorded, no ticket but the Housekeeping ticket is open, and no
ticket, plan or pull request carries an `Opener:` line.

**Variant A.** No ESLint ticket exists.

**Variant B.** A run before filed the three ESLint tickets, all open, none in review: the adoption's, the
suppressions' blocked by it, and the rollout's blocked by both. The rollout's ticket carries the browser question,
and the maintainer answered under it: the shop must still run in Internet Explorer 11. No other ticket but the Housekeeping ticket is open.

## Call

`/continuous-refactoring-run autonomous`

## Expected

- [ ] Variant A: the worklist judges that the generic, the PHP and the JavaScript Pack apply, and that the vendored
      `chart.min.js` is not the project's own JavaScript.
- [ ] Variant A: the Safety Net counts as fulfilled; Guardrails has no trace, since no ESLint Stage is known, and its scan is due.
- [ ] Variant A: the scan proposes `eslint-adoption`, `eslint-suppressions` blocked by it, and `eslint-rollout` blocked by
      both, the rollout carrying the question which browsers the code must run in. No PHP Stage is proposed.
- [ ] Variant A: filing creates three tickets, posts the browser question on the rollout's, and marks the blocked ones.
- [ ] Variant A: selection picks the adoption ticket. Its plan creates a `package.json` with `eslint`, `@eslint/js` and
      `globals`, and a flat config with `js.configs.recommended`, `globals.browser`, `sourceType: "script"` and the
      minified copy ignored, and records today's findings with `--suppress-all`.
- [ ] Variant A: the plan does not take in `no-var` or `eqeqeq`, though `cart.js` would break both.
- [ ] Variant B: the worklist judges that the rollout's Stage does not apply, since Internet Explorer 11 has no
      ES2015. Selection picks the adoption ticket; its plan sets `languageOptions.ecmaVersion` to `5` and marks no
      rule `Not yet:`, and it does not plan `no-var`, `prefer-const` or `object-shorthand`.

## Results

2026-11-08, on b36de5e, the scenario's first playing: pass, every line, as a walk-through. Then `eslint.md` was made explicit where the play had to infer: the adoption's config carries the rollout's rules as `Not yet:`, and an existing config without them fulfils the rollout.
2026-11-08, on 5def696 with the field test's fixes to `eslint.md`: pass, every line, as a walk-through. Then `prefer-const` was named as the exception to "a rule that finds nothing is on from the adoption".
2026-11-08, on ee5cfac with the rollout left out where the code must run without ES2015: pass, every line, both variants, as a walk-through, by one player. Then the text said who closes the rollout's ticket when the adoption has not written its `Not yet:` entries.
2026-11-08, on 6a475fe with a Deployer recipe alone making no PHP project: pass, every line, both variants, as a walk-through, by one player.
