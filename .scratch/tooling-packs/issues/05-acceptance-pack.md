# 05 — Acceptance case: a new Pack or Tool

Type: task
Status: done
Blocked by: 02, 03

The model is meant to make adding tools cheap. This ticket proves it: add the smaller of a Twig Pack
(Applies when: `.twig` templates in the repository) or Infection (`.scratch/php-tooling-tree/issues/09`),
and count what it took.

**What to build**

- The Pack or Tool: its rows in `pack.json`, its Tool file with Fulfilment check and MR scope per Stage,
  the regenerated docs, a changelog fragment.
- A comment on this ticket: which files changed and whether anything outside the Pack, its Tool file and
  the generated docs had to change. Anything else that had to change is a finding against the model.

**Done when** the new Stages appear in the parser's output on a fixture where they apply and not on one
where they do not, tests and validator are green, and the comment is written.

## Comments

> **2026-10-19:** Done with the Twig Pack (`twig-php`, scope `twig-php`; Infection stays a later ticket).
> Decisions: the Pack is named per engine and language (Twig for JS or Smarty would be Packs of their own);
> *Applies when* is the PHP Pack plus `twig/twig` in `composer.json`/`composer.lock`, never the file
> extension (`.tpl` may be Smarty, `.html` may be Twig); two Tools, Twig-CS-Fixer (Code Style, Safety Net) and
> TwigStan (Static Analysis, Guardrails, requires `phpstan-level-5`); Twig Lint was left out, since a Tool
> that fills Static Analysis or Code Style for syntax checks alone would put the real Tool out.
>
> **What it took.** New: `packs/twig-php/pack.json` (42 lines), two Tool files (11 lines each), the generated
> `docs/tooling/packs/twig-php.md` and its row in `docs/tooling/README.md`, the fixture `php-twig`, a changelog
> fragment. No change to the parser, the schema, `roles.json`, the validator or the generator.
>
> **Outside Pack, Tool files and generated docs, but not a finding against the model:** `tests/` count and
> page-list assertions (`SuiteDataTests` counts Stages per Track; `test_tooling_docs` lists the generated
> pages; two tests keyed `filled` by Role alone and now key it by Role and scope), the fixtures table, and the
> scope example in `tooling-model.md`.
>
> **Findings against the model.**
> 1. A Stage cannot require a Role in another Pack's scope: a Stage requiring a Role is checked in its own
>    Pack's scope. TwigStan's own Role is Static Analysis, in scope `twig-php`, so "requires Static Analysis"
>    would only ask for itself. It required the Stage `phpstan-level-5` instead, which names PHPStan and
>    excludes a Psalm target. If Twig on Psalm matters, a `requires` that names a scope is the extension.
> 2. The tests that count Stages and list pages by hand grow with each Pack; they are not the model's, but the
>    next Pack touches them too.
