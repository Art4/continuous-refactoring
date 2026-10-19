# A Role is filled per scope

> Amends [ADR-0079](0079-tooling-model-roles-tools-stages-in-packs.md): a Role filled by another Tool takes the
> place of a Tool only among Tools of the same scope.

A Role is what a tool is for, and the first model let one Tool fill it for the whole target: PHPStan was *out* on
a target on Psalm, which is right, because both analyse PHP. It is wrong across languages. A target with PHP and
Twig templates needs a code-style fixer for each, and a front end adds a third; with one filler per Role, the
first fixer in use would have made every other one *out*, and none of them would ever be proposed.

## Decision

**A Pack may name a `scope`**, the language or area its Tools work on (`php`, `twig`, `js`); the generic Pack
has none. A Role is filled **per scope**: Tools compete for it, and take each other's place, only with Tools of
their own scope. A Stage that requires a Role needs it filled in its own Pack's scope (a Stage of a Pack without
a scope: in any), and the Pack is refused when no Tool of that scope plays the Role. A rejection of a Role still
closes its Tools in every scope; to leave one language out, the Tool or the Pack is rejected. A target's own
Pack for PHP names the scope `php`, which lets its Tools stand beside the suite's.

## Considered Options

- **A Role per language** (`code-style-php`, `code-style-twig`). The Roles multiply with every language and
  stop saying what a tool is for. Rejected.
- **The scope on the Tool.** More general, and a Pack with Tools of several languages would be possible, but
  every Tool repeats it and a Pack that mixes languages is a Pack that should be two. Rejected.
- **Per Pack.** A target's own Pack for PHP would be a scope of its own, and a Stage of the suite that requires
  Static Analysis would never see the target's analyser. Rejected.

## Consequences

The parser's `roles` output is one entry per Role and scope, `{role, name, scope, filled_by}`. The suite's PHP
Pack gets `"scope": "php"`; the generic Pack stays without. Twig, as the first Pack beside PHP, brings its own
scope.
