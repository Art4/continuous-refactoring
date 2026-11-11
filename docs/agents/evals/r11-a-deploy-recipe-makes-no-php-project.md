# r11 — A deploy recipe makes no PHP project

Played as a walk-through.

Covers: `skills/continuous-refactoring-run/references/packs/php/pack.json`, `skills/continuous-refactoring-run/references/worklist.md`, `skills/continuous-refactoring-run/references/track-scan.md`

## Situation

The fixture `static-site-deploy-script`, onboarded, on GitHub as `acme/shop`: a static site under `public/`, HTML and
CSS only, deployed with Deployer. Its only PHP file is the Deployer recipe `deploy.php`; there is no `composer.json`
and no CI yet. Housekeeping is set up, and its ticket is not due. No Tooling Pack of its own. No ticket but the Housekeeping ticket is open, no
rejection is recorded, and no ticket, plan or pull request carries an `Opener:` line.

## Call

`/continuous-refactoring-run autonomous`

## Expected

- [ ] The worklist judges that the generic Pack alone applies: `deploy.php` only configures Deployer, and there is
      no `composer.json`.
- [ ] No Stage of the PHP Pack is judged, proposed or filed, and no PHP Tool is named as missing or out of reach.
- [ ] The tickets filed are for Stages of the generic Pack only, and no Housekeeping line of a PHP Tool is planned.

## Results
2026-11-08, on 6a475fe, the scenario's first playing: pass, every line, as a walk-through.
