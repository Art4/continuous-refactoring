# Psalm

Two Tools of the PHP Pack share this file, because the taint analysis and Psalm's own presence constantly refer to each other:

- **Psalm** (`psalm`), recognized for the Role Static Analysis: counted when a project has already adopted it, never proposed.
- **Psalm Taint Analysis** (`psalm-taint-analysis`), on request, for the Role Taint Analysis, with the Signal Security (`../../signals.md`). Proposed only when a human asks for it, as Semgrep is.

**Why this order.** Psalm needs `composer`. Psalm Taint Analysis is proposed once at least one of PHPStan Level 4 or Psalm is fulfilled: a target that reached PHPStan Level 4, or one that chose Psalm as its general analyser, unlocks it. It is a Guardrails Stage, workable once the Safety Net is fulfilled: the findings of a taint analysis can need a restructuring to fix, and that restructuring waits for the Safety Net.

### `psalm`

- **Purpose:** an alternative static-analysis path to the PHPStan level chain. It is recognized when a project has already adopted Psalm instead of PHPStan, never suggested as a new adoption (the same recognition Pest gets for `phpunit`).
- **Fulfilment check:** `vimeo/psalm` is present as a dependency (dev or prod) with a committed `psalm.xml` / `psalm.xml.dist`, and `vendor/bin/psalm` exits without errors.
- **MR scope:** none. It is recognition only and never a ticket; adopting Psalm from scratch is a decision made outside the proposal flow, as choosing Pest over PHPUnit is.
- **Takes the place of PHPStan.** Once this Stage is fulfilled and PHPStan's first Stage is not, Psalm fills the Role Static Analysis and PHPStan is not proposed; none of the level Stages gets a ticket. Strictness is governed by `psalm.xml`'s `errorLevel`. The agent hands in `psalm` as fulfilled and does not hand in `phpstan-level-0` for it (`phpstan.md`, *PHPStan and Psalm*).
- **Co-presence.** If both PHPStan and Psalm are present, PHPStan is the Tool in use and this Stage is harmlessly fulfilled too. A target on PHPStan that adopts Psalm Taint Analysis also installs `vimeo/psalm` and a `psalm.xml`, so this Stage's check reads fulfilled as well, which changes nothing since PHPStan's first Stage is fulfilled.

### `psalm-taint-analysis`

- **Purpose:** security-focused taint analysis (SQL injection, XSS and similar tainted-data-flow bugs): a distinct capability from Psalm's general static analysis, orthogonal to which general analyser a target chose. It is available once either general-analysis path has matured enough to layer a security scan on top, whether that path is PHPStan or Psalm. Run as `vimeo/psalm --taint-analysis`.
- **Fulfilment check:** `vimeo/psalm` is present as a dependency (dev or prod), a `psalm.xml` / `psalm.xml.dist` is committed and, once `ci-runner` is fulfilled, a CI job invokes `vendor/bin/psalm --taint-analysis` (a self-wired CI gate, the same shape as `phpstan-level-0`'s; with no CI yet, local adoption alone still fulfils the Stage).
- **MR scope:** on the Psalm path, `vimeo/psalm` and `psalm.xml` already exist, so this merge request only wires the `--taint-analysis` CI invocation. On the PHPStan path it additionally runs `composer require --dev vimeo/psalm` and commits a `psalm.xml`, reused for taint checking only and not as a competing general analyser.
- **Co-presence caveat.** Adopting this Stage on the PHPStan path installs `vimeo/psalm` and `psalm.xml` purely for taint scanning, which incidentally makes the Stage `psalm` read fulfilled too. That is harmless: Rector PHP Set requires the Role Static Analysis, which stays filled by PHPStan either way, and the choice between PHPStan and Psalm was never a written rejection (`phpstan.md`, `phpstan-level-0`), only what each Stage's own check records.
- **Why it is a Guardrails Stage.** A taint finding in the target's own code is often fixed only by restructuring: moving the escaping to one place, or splitting a function that mixes input handling with output. A Safety Net Stage holds structural work back until it is fulfilled, so a Stage whose findings need that work would wait on its own precondition, and the Safety Net would only be passed by skipping it. As a Guardrails Stage it is worked after the Safety Net, when the restructuring can be done.
