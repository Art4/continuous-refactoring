# 01 — A deploy script makes no PHP project

Type: task
Status: done
Blocked by: —

**What happened.** In the field, a static website with no `composer.json` got the PHP Pack because of one PHP file,
a deploy recipe. The run proposed PHP Stages and a Housekeeping line the human then had to reject. That was before
0.5.0, but `packs/php/pack.json` still applies when the repository holds "a composer.json …, or at least one *.php
file outside vendor/", so it would happen today.

**What to build**

- Decide how the PHP Pack's `applies_when` reads, so that a build or deploy script alone does not make a PHP project.
- A fixture under `fixtures/`: a static site with one PHP deploy script and no `composer.json`. A scenario under
  `docs/agents/evals/` with its `Covers:` line (once `quality-review` ticket 04 is in): only the generic Pack applies.
- The first case of the field rule "a miss becomes a ticket and a scenario" (`quality-review` spec, S1.4).
- A changelog fragment.

**Done when** the fixture gets only the generic Pack, the scenario passes, and tests and validator are green.

## Comments

**2026-11-08 — Done.** Decided in quality-review Q48 and Q49: a file that only configures a tool, with no
`composer.json` beside it, makes no PHP project; code of the project's own, a build script included, still does
(Q46). Fixture `static-site-deploy-script`, scenario r11; r11 and r9 pass at 6a475fe.
