# Playbook: Adding a tool of your own

The suite proposes the tools its Packs know. A project that uses a tool the suite does not know, or has a house rule it wants worked off step by step, keeps a **Pack of its own**. The suite reads it beside its own Packs, proposes its Stages like any other, and judges whether they are fulfilled the same way.

## What you need

Three things in the project, all committed:

1. **A directory** for the Pack, recommended `docs/agents/tooling-pack/`.
2. **`pack.json`** in it: the Pack, its Tools and their Stages.
3. **One Markdown file per Tool**, named in the Tool's `details` field, relative to the directory: what the suite checks to call a Stage fulfilled (the *Fulfilment check*) and what a merge request for it contains (the *MR scope*).

Add a **Tooling Pack** bullet to the `## Refactoring operations` section of `docs/agents/issue-tracker.md`, naming the directory:

```markdown
- **Tooling Pack**: `docs/agents/tooling-pack/`
```

Without the bullet the suite does not look. The onboarding does not ask about it; it lists it among what was left out.

## A small example

A project that checks the dependencies between its layers with Deptrac, and wants the violations worked off:

```json
{
  "$schema": "../../../.agents/skills/continuous-refactoring/references/pack.schema.json",
  "pack": "house-rules",
  "scope": "php",
  "applies_when": "Always.",
  "tools": [
    {
      "tool": "deptrac",
      "name": "Deptrac",
      "uses": "qossmic/deptrac",
      "roles": ["architecture-rules"],
      "status": "recommended",
      "details": "deptrac.md",
      "stages": [
        {
          "slug": "deptrac-layers",
          "name": "Deptrac Layers",
          "track": "Guardrails",
          "requires": ["composer"],
          "after": []
        },
        {
          "slug": "deptrac-strict",
          "name": "Deptrac Strict Rules",
          "track": "Guardrails",
          "requires": ["deptrac-layers"],
          "after": []
        }
      ]
    }
  ]
}
```

`architecture-rules` is a Role the suite does not have. A Pack that adds a Role keeps it in a `roles.json` beside the `pack.json`: a slug, a name, a one-sentence purpose, and the signal it feeds, or `null`. The suite's [tooling overview](../tooling/README.md) lists the Roles it has; use one of them where it fits, so the suite sees your tool as an alternative to its own.

## The rules

- **Add, never redefine.** Slugs are unique across the suite's Packs and yours: a Tool, a Stage, a Role or a Pack of the same slug ends the run's tooling step with an error that names both places. A Tool of the suite you do not want is declined with a rejection, as any other.
- **The scope decides who competes.** A Pack names the language it works on (`"scope": "php"`). Tools of one scope compete for a Role: a project that uses Mago instead of PHPStan names the scope `php`, declines PHPStan, and Mago fills Static Analysis, so Rector's Stages stop waiting for PHPStan. Tools of other scopes do not take each other's place: a Code Style Tool for Twig and one for PHP are both in use.
- **A Stage may wait for the suite's.** `requires` and `after` can name Stages and Roles of the suite's Packs (`composer`, `static-analysis`); nothing of the suite waits for yours.
- **It comes last.** The suite's Stages are proposed first.
- **Applies when** is a sentence the suite judges against the project, once per run. A project's own Pack usually says "Always."
- The `"$schema"` line points at the schema in the project's installed skills; it lets an editor check and complete the file. Write the file in the form the suite's own Packs have: two-space indent, objects one key per line, lists of plain values on one line.

## When the suite renames something

The suite adds Tools over time. If one takes a slug your Pack uses, the next run ends with the error above. Rename your slug; the suite's tickets keep theirs.
