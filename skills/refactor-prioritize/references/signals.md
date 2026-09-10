# Signal factors

The catalogue of **Signal** values a candidate issue's third field (Where/Problem/**Signal**) can
name. Purely descriptive — how to recognise each while exploring — never an execution mechanism: this
skill never runs a tool itself, and nothing here is tracked as adopted the way a Safety Net node's
Fulfilment check is. `structural-candidate-search.md` and `baseline-shrink-selection.md` both read
this file when picking and ranking candidates; recognising a factor's evidence stays this skill's own
judgement call.

Some factors are readable from git/the filesystem alone (**generic**); others need a language-aware
tool to say anything precise (**language-specific** — the PHP tree names one below where it applies;
a future language specialization would name its own).

## Structural cues

- **Shallow modules** — little depth: interface nearly as complex as the implementation.
  **Deletion test**: would deleting it concentrate complexity, or just move it? "Concentrates" is
  the signal. *Generic* — reading the code.
- **Missing locality** — pure functions extracted for testability, but the real bugs hide in how
  they're called. *Generic* — reading the code.
- **Low leverage** — a lot of interface surface buying little behaviour. *Generic* — reading the code.
- **Tightly-coupled seams** — modules leaking across their boundaries. *Generic* — reading the code.
- **Untested / hard-to-test** — no test reaches it, or its current interface resists testing.
  *Generic* — the test suite itself, or its absence. *Language-specific* for a numeric proxy — PHP:
  `coverage-floor`'s own Clover-XML coverage report, once adopted (a file sitting meaningfully under
  the current floor is this factor's own real evidence).
- **Tooling pressure** — places the fulfilled tooling (PHPStan, Rector, style) keeps flagging, or a
  dependency approaching end-of-life/unsupported status. *Language-specific* — the fulfilled static
  analysis/lint tools' own output; PHP: `phpstan.neon`/`phpstan-baseline.neon` residuals, Rector
  dry-run findings, `composer outdated`.

## Consequence cues

- **Security** — an exposed secret, an unauthenticated path to sensitive data, an injection class not
  yet closed. *Generic* usually (reading request handling, deployment/docroot config) — sometimes
  *language-specific* (PHP: Psalm's own taint analysis, once adopted; `semgrep`'s OWASP-Top-10 ruleset
  once adopted, for the categories taint analysis doesn't reach — crypto misuse, misconfiguration,
  logging gaps). **Triggers priority admission**
  (`refactor-scan`'s backlog cap, see that skill's step 1) — leaving it unfixed doesn't just carry
  risk, it actively worsens with every day it's live.
- **Blast radius of inaction** — the cost of leaving this alone keeps rising, not just the risk of
  touching it (a growing dependency that will be harder to migrate the longer it's deferred; a
  workaround other code is starting to build around). *Generic* — reading the surrounding code and
  its trend over recent commits. **Triggers priority admission**, same reasoning as Security.
- **Defect density** — distinct from Heat (raw change frequency): where do bugs/incidents actually
  cluster, regardless of how often the area changes? *Generic* — issue tracker history, commit
  messages mentioning fixes, `git log --grep`.
- **Understandability** — how hard this is for a person to follow or safely change: cognitive load
  (nested conditionals, implicit state, unclear naming) and knowledge concentration (does only one
  person actually understand this part) both live here. *Generic* — reading the code; `git shortlog`
  or blame for the concentration half. *Language-specific* for a numeric proxy — PHP: `phpmd`'s
  cyclomatic-complexity rule.
- **Observability** — can anyone tell when this breaks? Missing logging/monitoring around a path that
  matters. *Generic* — reading the code for silent failure modes (swallowed exceptions, unchecked
  return values).
- **Domain/business criticality** — sits on a core user journey or revenue path, per what `CONTEXT.md`
  or the target's own README states the application must preserve. *Generic* — cross-reference
  against the documented domain model.
- **Timing / sequencing** — a larger change already planned (or already landed) either resolves this
  for free or makes it materially more urgent to do now, before more work builds on the current shape.
  *Generic* — recent commit history and open candidate issues.
