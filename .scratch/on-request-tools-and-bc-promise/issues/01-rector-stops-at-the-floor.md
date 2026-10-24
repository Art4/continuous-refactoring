# 01 — Rector stops at the declared PHP floor

Type: task
Status: ready-for-agent
Blocked by: —

**What to build** (ADR-0087)

- `rector-php-set` (`packs/php/rector.md`): Purpose and MR scope target the declared floor and no higher (`withPhpSets()`
  without an argument, or the level equal to `require.php` / `config.platform.php`). Fulfilment check: the applied level
  equals the floor and no rule finding is left. A floor raised later makes the Stage unfulfilled again. Code that already
  needs more than the floor gets no Stage; whoever notices it proposes an ordinary ticket.
- Remove `php-minimal-version`: the Tool and Stage from `packs/php/pack.json`, `packs/php/php-minimal-version.md`, the
  Role `runtime-floor` from `roles.json`, the pointer in `rector.md`'s *Why this order*.
- A rejection of `php-minimal-version` on record is ignored (check the parser accepts an unknown rejected slug; add a test
  if it does not).
- `CONTEXT.md`: drop **Floor correction**; replace **Floor raise** with:

  > Committing a project to a newer PHP version than the floor it declares (`composer.json`'s `require.php`) — by raising
  > the declared floor, or by changing the code so it needs a newer PHP than declared, as a Rector PHP-version set above
  > the floor would. A genuine **Breaking change**, a product decision, never autonomously proposed by any Stage of the
  > tooling tree: the suite's PHP-version rewrites stop at the declared floor.
  > _Avoid_: floor bump, floor correction (a rewrite above the floor followed by a matching `require.php` is a raise,
  > not a correction), upgrade (collides with `rector-php-set`'s own "PHP-upgrade rule set" wording)

- Regenerate `docs/tooling/`; grep `README.md` and `docs/` (outside `docs/adr/`) for the Stage and the Role.

**Done when** no reference outside `docs/adr/` names `php-minimal-version`, Runtime Floor or Floor correction, and tests
and validator are green.

## Comments
