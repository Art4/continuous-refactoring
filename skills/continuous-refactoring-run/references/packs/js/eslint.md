# ESLint

The recommended Tool for the Role Static Analysis in the JavaScript Pack. It plays the Role in its own scope, so
PHPStan and Psalm keep theirs on the PHP code and neither takes the other's place. Three Stages: `eslint-adoption`
sets ESLint up with its recommended rules and records what they find today, `eslint-suppressions` clears that record
part by part, and `eslint-rollout` takes in stricter rules one by one.

**Why this order.** All three are Guardrails Stages: no structural work on PHP needs the frontend linted, and an
unlinted frontend must not hold the Safety Net back. `eslint-adoption` waits until `editorconfig` is decided, as the
other code-style and lint Tools do. `eslint-rollout` waits until the suppressions are decided, so a new rule never
lands on code whose old findings are still suppressed.

### `eslint-adoption`

- **Purpose:** a linter reads the project's own JavaScript and reports defects, so a later change does not add new
  ones.
- **Fulfilment check:** all of:
  - `eslint` is a dev dependency in `package.json`;
  - a flat config is committed (`eslint.config.js`, `.mjs` or `.cjs`) that takes in `js.configs.recommended`
    (`@eslint/js`) and names the project's own JavaScript paths, leaving out minified files and build output;
  - `npx eslint .` exits 0, with the suppressions file where there is one (*Suppressions*);
  - once `ci-runner` is fulfilled, a CI job runs it. With no CI yet, the local run alone still fulfils the Stage.
- **An existing config.** A target that already runs ESLint keeps its config, whatever it extends: its rules are its
  own choice. A legacy `.eslintrc*` fulfils the Stage as well; moving it to a flat config is Housekeeping's, when the
  target's ESLint version needs it.
- **MR scope** of a fresh adoption, one commit each:
  1. `package.json` (created where there is none, `"private": true`) with `eslint`, `@eslint/js` and `globals` as dev
     dependencies, the lock file, and `node_modules/` in `.gitignore`.
  2. The flat config: `js.configs.recommended`, the globals of where the code runs (`globals.browser` for a frontend,
     `globals.node` for scripts), `sourceType` as the files are written (`script` where they are loaded by a
     `<script>` tag without `type="module"`), `ignores` for minified files, vendored copies and build output, and the
     rollout's rules that find something switched off, each marked `Not yet:` with its count (`eslint-rollout`).
     A rule that finds nothing is on from here, `prefer-const` aside.
  3. The suppressions file, written by `npx eslint . --suppress-all`, so the run is green from this merge request on
     (*Suppressions*). A target with no findings has none.
  4. Once `ci-runner` is fulfilled, the CI job.
  5. The Housekeeping line below, in the target's Housekeeping template, as a commit of its own before the changelog
     entry.
- The merge request reads in its description the paths it lints, the globals and `sourceType` with their reason, and
  the count of suppressed findings per rule.
- **Node.js:** the version ESLint needs is the `engines` field of the release installed, read from the lock file,
  never from memory. That is the developer's and CI's runtime, not the browser's; where neither has it, the run names
  that and the Stage is not set up.

### `eslint-suppressions`

- **Purpose:** clear the findings the adoption recorded, so the recommended rules hold for all the code.
- **Fulfilment check:** `eslint-adoption` is fulfilled and no suppressions file exists, or it is empty.
- **Its ticket** is "ESLint: clear the suppressions", a baseline ticket: it stays open across many merge
  requests, and each run plans the next part (`../../planning-a-baseline-ticket.md`).
- **A part** is one rule's suppressions, or a group of its files where they are too many to review at once: the rule
  with the fewest suppressed findings first. The fix removes the finding at its cause; an `eslint-disable` comment is
  no fix. `npx eslint . --prune-suppressions` then removes what the fix made obsolete.
- **MR scope** of a part: the fixes and the pruned suppressions file. A finding that only a change of behaviour could
  remove stays suppressed and is named in the plan.

### `eslint-rollout`

- **Purpose:** take in stricter rules, one by one, in merge requests a person can review.
- **Applies when:** the code may use the syntax the rules bring (ES2015: `let`, `const`, shorthand properties). It
  does where the code is built or transpiled, where the project names its browsers (a `browserslist`) and they all
  have it, or where the code already uses that syntax. Where none of this is known, the proposal carries the question
  which browsers the code must run in. Current browsers only → `ecmaVersion` stays at ESLint's default. Browsers
  without ES2015 → the Stage does not apply: the config sets `languageOptions.ecmaVersion` to `5` and holds no
  `Not yet:` entry. The adoption's merge request then also closes the rollout's ticket, quoting the answer. An
  answer after the adoption is merged goes to the Housekeeping ticket as a comment: set it, delete the entries.
- **Fulfilment check:** `eslint-adoption` is fulfilled, the config holds no rule marked `Not yet:`, and no rollout file
  exists.
- **The rules** a fresh adoption marks `Not yet:` with their count: `no-var`, `prefer-const`, `object-shorthand`,
  taken in in this order. `prefer-const` finds nothing in code written with `var`; it is counted again once `no-var`
  is on, and switched on at once where it still finds nothing.
  Each is fixed by `npx eslint --fix` without a change of behaviour. `eqeqeq` is not among them: replacing `==`
  changes what the code does. A target that already runs one of these keeps its setting; an existing config without them fulfils this Stage as
  well, its rules being its own choice.
- **Its ticket** is "ESLint: take in the remaining rules", a baseline ticket.
- **A part** is one path step of one rule: an override block in the config that turns the rule on for the paths done
  so far, or a rollout file of that shape. The fix is the tool's `--fix` run, with nothing typed by hand. The last
  part of a rule turns it on for every path and deletes its `Not yet:` entry.

### Suppressions

ESLint (9.24 or newer) records the findings that existed when a rule was switched on in `eslint-suppressions.json`,
counted per file and rule. A run with the file passes as long as no file has more findings of a rule than recorded;
a new finding fails it. `--suppress-all` writes the file, `--prune-suppressions` removes entries the code no longer
needs. On an older ESLint, the adoption raises the version first.

### Housekeeping

- **Housekeeping:** run `npx eslint . --prune-suppressions` and commit what it removes; only the suppressions file
  changes, never the code.
