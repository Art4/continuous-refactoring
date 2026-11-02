# Research: how projects document their BC promise

Date: 2026-11-02. Every claim below has the URL it was fetched from beside it. "Not verified" means
the fetched page did not say it, or no primary source could be fetched.

## 1. Summary

- No formal standard exists for a "BC promise document". SemVer requires that a public API be declared but
  leaves the form open ("in the code itself or … strictly in documentation"). CalVer and PEP 440 say nothing
  about compatibility.
- The written promises studied (Symfony, Drupal, PHPUnit, Django, Kubernetes, Angular, Python, Node.js,
  TYPO3, Doctrine) keep answering the same ten or so questions. Who the consumer is. What is covered,
  usually "documented or untagged public", with `@internal`, `_`-prefixed and test code left out. What
  each consumer role (use, extend, implement) may rely on. What each release type may change. The
  deprecation procedure, its minimum window and its markers. Experimental APIs. Exceptions (security,
  bugs). Support or LTS periods. Where upgrade notes live.
- Machine-readable markers exist in every ecosystem (`@internal`, `@api`, `@deprecated`, `#[\Deprecated]`,
  `@Deprecated(forRemoval)`, `@API(status)`, `@RequiresOptIn`, `#[non_exhaustive]`, TSDoc release tags,
  OpenAPI `deprecated`, the `Deprecation` and `Sunset` headers). None of them declares a project's promise
  as a whole.
- Most checkers work out the API from code or binaries and compare it with a baseline release: Roave,
  japicmp, Revapi, cargo-semver-checks, apidiff, gorelease, griffe and .NET package validation. Two
  of them keep a declared surface file in the repository instead: API Extractor's `.api.md` and .NET's
  `PublicAPI.Shipped.txt`/`PublicAPI.Unshipped.txt`.
- For the Stage, a draft should answer the questions in section 7 from repository evidence. Where no
  evidence exists, it should leave the question open for the human rather than pick an answer.

## 2. Versioning specs and how they define the contract

| Spec | What it says about the contract | Source |
| --- | --- | --- |
| SemVer 2.0.0 | Item 1: "Software using Semantic Versioning MUST declare a public API … This API could be declared in the code itself or exist strictly in documentation. However it is done, it SHOULD be precise and comprehensive." Item 4: in 0.y.z "Anything MAY change at any time. The public API SHOULD NOT be considered stable." Minor "MUST be incremented if any public API functionality is marked as deprecated"; major for "any backward incompatible changes". FAQ: deprecate by (1) documenting it and (2) releasing a minor version that carries the deprecation, and "If your software is being used in production, it should probably already be 1.0.0." | https://semver.org/spec/v2.0.0.html |
| CalVer | Defines no API and no contract: "CalVer deliberately does not attempt to communicate breaking changes". It recommends pairing CalVer with "a changelog and policy". Case studies (Twisted: removal a year and two releases after deprecation) are project policies, not part of CalVer. | https://calver.org/ |
| PEP 440 | Defines version syntax and specifiers only. Supports SemVer major/minor/patch "without requiring it". `~=` is a matching rule that relies on an *expected* compatibility, not a promise about behaviour. | https://peps.python.org/pep-0440/ |
| PEP 387 (Python BC policy) | Covers "all public APIs" (reference manual, C-API, documented exceptions). Leaves out `_`-prefixed names, anything documented as private, imported modules, internal inheritance patterns, `Lib/test` and provisional APIs (PEP 411). "if something is not documented at all, it is *not* automatically considered private." Deprecation: discuss, add a `DeprecationWarning` naming the removal release (plus `@deprecated` in typeshed), wait at least two minor versions or two years (five years preferred), then remove. Also defines *soft deprecation*: documented, no warning, no removal date. The steering council grants exceptions. | https://peps.python.org/pep-0387/ |
| PEP 8 | "Documented interfaces are considered public, unless the documentation explicitly declares them to be provisional"; modules "should explicitly declare the names in their public API using the `__all__` attribute"; internal names still take a leading `_`. | https://peps.python.org/pep-0008/#public-and-internal-interfaces |
| Python provisional API | "deliberately excluded from the standard library's backwards compatibility guarantees". | https://docs.python.org/3/glossary.html |
| Go 1 compatibility promise | Programs written to the Go 1 specification "will continue to compile and run correctly, unchanged". This holds at source level; binary compatibility is not promised. Exceptions: security, unspecified behaviour, specification errors, bugs, unkeyed struct literals, methods added to embedded types, dot imports, `unsafe`. Also out of scope: `syscall`, tool behaviour, performance, unreleased features. Sub-repositories may follow "looser compatibility requirements". | https://go.dev/doc/go1compat |
| Go module version numbers | v0: "no backward compatibility or stability guarantees"; minor: "backward-compatible changes to the module's public API"; patch: "changes that don't affect the module's public API". Major ≥ 2 changes the module path (`/v2`), "a new module with a separate history". | https://go.dev/doc/modules/version-numbers |
| Go: keeping modules compatible | "add, don't change or remove". No signature change is compatible. Adding a method to a public interface breaks implementers. Behaviour changes can break users "even if user code continues to compile". Techniques: new functions, option structs, unexported interface methods. | https://go.dev/blog/module-compatibility |
| Go `internal` directories | "Code in or below a directory named "internal" is importable only by code that shares the same import path". The language enforces the API boundary. | https://pkg.go.dev/cmd/go |
| Rust RFC 1105 | Splits changes into *major* and *minor*: "all major changes are breaking, but not all breaking changes are major". A minor change may break code only shallowly, where the fix could have been written in advance (glob imports, method ambiguity). Lists major changes by language construct. Unstable features are not covered. | https://rust-lang.github.io/rfcs/1105-api-evolution.html |
| Cargo SemVer reference | Labels each rule *major*, *minor* or *possibly-breaking*. For 0.y.z, y counts as major and 0.0.z is always major. Beyond the API it covers MSRV, platform requirements, features and dependencies. For binaries, authors "will need to decide if and how you want to employ a SemVer contract". Recommends adding `#[non_exhaustive]` when an item is introduced. | https://doc.rust-lang.org/cargo/reference/semver.html |
| npm | Recommends starting at 1.0.0. A table maps patch, minor and major to change types. `~` accepts patches and `^` accepts minors. Defines no public API. | https://docs.npmjs.com/about-semantic-versioning |
| Eclipse "Evolving Java-based APIs" | API = public/protected members of types in packages advertised as API; non-advertised packages are not API. Contracts are judged per client role (caller, implementor, subclasser). Tightening is safe for callers and loosening is safe for implementors. Binary compatibility is required; source compatibility "is not a requirement". "Every aspect of the API matters to some Client." The page names no `@noimplement`-style tags. | https://wiki.eclipse.org/Evolving_Java-based_APIs |
| .NET library change rules | Each kind of change is marked allowed, disallowed or "requires judgment". Groups: public contract (types, members), behaviour (values, exceptions, attributes), platform support, internal implementation (reflection on internals "generally allowed"), code changes. | https://learn.microsoft.com/en-us/dotnet/core/compatibility/library-change-rules |
| .NET breaking-change guidance | Kinds of break: source, behaviour, binary. Low-level libraries suffer most. Use `[Obsolete]` with migration text, and "CONSIDER keeping types and methods with the ObsoleteAttribute indefinitely in low and middle-level libraries". Put behaviour changes behind opt-in settings. | https://learn.microsoft.com/en-us/dotnet/standard/library-guidance/breaking-changes |

## 3. Written BC promises of major projects

### PHP

**Symfony, Backward Compatibility Promise** — https://symfony.com/doc/current/contributing/code/bc.html
- Promises BC across all minor releases, following SemVer.
- It has two parts. "Using Symfony Code" addresses users and is split into Interfaces, Classes, Traits
  and Translations, with tables of "If you…" use cases and the guarantee for each. "Working on Symfony
  Code" addresses contributors, with a table per Interface, Class and Trait: *Type of change* / *Change
  allowed* / *Notes*, and rows grouped by member kind (properties, constructors, methods, constants).
- Roles: **use** (type-hint, instantiate, call), **extend** (subclass, override), **implement** (an
  interface, use a trait).
- Exclusions: `@internal` elements and `*\Tests\` namespaces; `@experimental` features (experimental for one
  minor at most, never introduced in an LTS); security fixes; some translations; parameter names
  ("Using PHP named arguments might break your code"), except for Attribute constructors.
- `@final`, and `@final since Symfony x.y`, announce that a class becomes final in the next major.
- It also covers how to make a change compatibly, for example adding an argument through `func_num_args()`
  and a deprecation.
- Deprecation procedure — https://symfony.com/doc/current/contributing/code/conventions.html: deprecations
  only in the next minor; written as `@deprecated since Symfony 5.1, use X instead.` plus
  `trigger_deprecation()`; CHANGELOG + `UPGRADE-<minor>.md` + `UPGRADE-<next major>.md` entries in the same PR;
  removal only in the next major, "once every two years".
- Cadence and support — https://symfony.com/releases: minors every six months, majors every two years. A
  standard release gets about 8 months; an LTS gets about 3 years of bug fixes and 4 of security fixes (dated
  entries).
- Upgrade path — https://symfony.com/doc/current/setup/upgrade_major.html: clear the deprecations on the last
  minor, then read `UPGRADE-X.0.md`. `symfony/phpunit-bridge` reports the remaining deprecations.
- UPGRADE file format — https://github.com/symfony/symfony/blob/7.3/UPGRADE-7.3.md: one heading per component,
  "Deprecate X, use Y instead" bullets, Before/After code, and `[BC BREAK]` marking breaks in minors.

**Drupal, BC and internal API policy** — https://www.drupal.org/about/core/policies/core-change-policies/bc-policy
- Uses SemVer, deprecates first, and puts security ahead of stability. Every class, method and function
  counts as public or internal.
- `@api` marks something public; protected members are internal unless `@api` says otherwise. `@internal` may
  change in minors.
- It lists what is internal: DB schema, HTTP headers, test classes, controllers and forms, particular
  plugins and entity handlers, event subscribers, constructors of services, plugins and controllers,
  public methods outside an interface, `_`-prefixed functions and named arguments.
- Interfaces get three levels: `@api` may be type-hinted and implemented; untagged may be type-hinted, but
  methods may be added in minors; `@internal` should be avoided.
- It also covers CLI options, config, user-facing strings and experimental modules (treated like
  `@internal`). Frontend has a separate policy.
- Deprecation policy — https://www.drupal.org/about/core/policies/core-change-policies/drupal-deprecation-policy:
  a fixed text, `@deprecated in %deprecation-version% and is removed from %removal-version%. %extra-info%.`
  with `@see` a change record, plus `@trigger_error(…, E_USER_DEPRECATED)` in a fixed format; removal in a
  later major. Internal APIs should still be deprecated first, with the notice "As internal API, baz() may
  also be removed in a minor release."

**PHPUnit, BC promise** — https://phpunit.de/backward-compatibility.html
- SemVer with yearly majors.
- Excludes `@internal` units ("must not be used in third-party code") and parameter names: non-internal
  units carry `@no-named-arguments`. For event value objects only the query methods are covered.
- Deprecation runs in three steps over two majors: soft (`@deprecated`, no behaviour change), then hard
  (reported, in the next major), then removal (the major after that). Per-release `DEPRECATIONS.md`.
- Also: tags are immutable and branches are internal.

**Doctrine, deprecation policy** — https://doctrine-project.org/policies/deprecation.html
- Deprecations only in minors, marked `@deprecated`. Downstream users are expected to see them through
  PHPStan deprecation rules or Psalm.
- Conditional deprecations go through `doctrine/deprecations`
  (https://github.com/doctrine/deprecations: `Deprecation::trigger(package, link, message)`, PSR-3 or
  `E_USER_DEPRECATED`, silent by default).
- Each deprecation PR updates `UPGRADE.md`, and so does each removal on the next major branch.
- The release policy page (https://www.doctrine-project.org/policies/releases.html) covers only release
  timing. *Not verified:* a Doctrine-wide definition of public API or of `@internal`; none was found.

**TYPO3, deprecation policy (article 2020, edited 2023)** — https://news.typo3.com/archive/typo3-deprecation-policy
- Deprecate first; the deprecated part stays intact through the current major and goes in the next one.
  No breaking changes in bugfix releases.
- Exceptions: security, dependency updates, migrations through the Upgrade Wizard, faulty behaviour.
- `@internal` classes are excluded.
- Covered: hooks and signals, PSR-14 events, CLI commands, backend routes, PSR-15 middlewares and most config.
  Not covered: backend JS, CSS, HTML and templates.
- Tooling: a deprecation log and the Extension Scanner
  (https://docs.typo3.org/m/typo3/reference-coreapi/main/en-us/ApiOverview/Deprecation/Index.html).
- *Not verified:* the changelog entry types (Breaking/Deprecation/Feature/Important `.rst`); no fetched page
  described them.

**Laravel** — https://laravel.com/docs/12.x/releases
- Its versioning section, not a separate BC document, says: SemVer; "Minor and patch releases should
  **never** contain breaking changes"; use `^12.0`.
- "Named arguments are not covered by Laravel's backwards compatibility guidelines."
- Support: bug fixes for 18 months, security fixes for 2 years.
- *Not verified:* any Laravel definition of public versus internal API; none was found.

**WordPress**
- *Not verified for core.* The core Handbook page on backward compatibility was not found (404), and the Trac
  ticket proposing a removal policy for deprecated functions (https://core.trac.wordpress.org/ticket/49957)
  returned 403. The search snippet says it was closed as wontfix, which is secondary and unverified.
- Block editor — https://developer.wordpress.org/block-editor/contributors/code/backward-compatibility/:
  guarantees cover only the production packages exposed on the `wp` global. Functions keep their names,
  argument order and return type; components keep their props; blocks keep valid markup through `deprecated`
  versions. Class names and DOM are not API. Deprecation goes through `wp.deprecated` with `since` and
  `plugin`, and breaks are announced in "dev notes".

### Elsewhere

**Django** — https://docs.djangoproject.com/en/stable/misc/api-stability/ and
https://docs.djangoproject.com/en/dev/internals/release-process/
- Stable means everything documented, apart from the "internals" area and `_`-prefixed names.
- Stable APIs are not moved or renamed without aliases. Deprecated APIs remain "for at least two feature
  releases", with warnings. Security trumps compatibility.
- Warning classes are named after the removal release (`RemovedInDjango51Warning`).
- Pre-2028: removed in B.0 or B.1, with LTS releases. From 2028 the versioning becomes CalVer: deprecated in
  YYYY, removed in YYYY+2, three years of security fixes for every release.

**Kubernetes** — https://kubernetes.io/docs/reference/using-api/deprecation-policy/
- Numbered rules for API elements, CLI flags, features or behaviours, feature gates and metrics.
- Windows depend on tier (GA, beta, alpha). Examples: a beta API is served 9 months or 3 releases after
  deprecation; a GA CLI element lasts 12 months or 2 releases; a deprecated behaviour must function for 1
  year; alpha may be removed without notice.
- A replacement must not be less stable than what it replaces.
- Deprecated endpoints return a `Warning` header and an audit annotation.
- An "Exceptions" section; any exception must be announced in the release notes.

**Angular** — https://angular.dev/reference/releases and
https://github.com/angular/angular/blob/main/contributing-docs/public-api-surface.md
- SemVer; majors every 12 months; 24 months of support (12 active, then 12 LTS).
- Deprecations are announced in the changelog and marked `@deprecated`, kept at least one major, and
  removed only in a major. Developer preview and experimental APIs are not covered.
- A separate "public API surface" document lists covered packages and entry points. It excludes
  `@angular/compiler`, `ɵ`/`_`/private symbols, deep import paths, constructors of injectables and generated
  code. On subclassing: "All public classes are treated as `final`" unless documented otherwise.
- Peer dependency bumps are allowed in minors when they do not break anything.

**Python stdlib** — PEP 387 and the provisional API (section 2).

**Node.js**
- Stability Index — https://nodejs.org/api/documentation.html: 0 Deprecated, 1 Experimental (1.0/1.1/1.2,
  "not subject to semantic versioning rules"), 2 Stable, 3 Legacy (still covered by semver, no longer
  maintained).
- Deprecation kinds — https://nodejs.org/api/deprecations.html: documentation-only, application, runtime and
  end-of-life, each with a stable `DEP0xxx` ID; `--pending-deprecation`.
- Collaborator guide — https://github.com/nodejs/node/blob/main/doc/contributing/collaborator-guide.md: "All
  functionality in the official Node.js documentation is part of the public API"; undocumented `_`
  members and `lib/internal/**` are internal; a change that breaks the ecosystem is semver-major; a runtime
  deprecation is semver-major; nothing reaches end-of-life without a runtime deprecation first.
- Release lines — https://github.com/nodejs/release: Current, Active LTS, Maintenance LTS. From Node 27 every
  line gets 30 months of LTS.

**Sections that keep recurring** across these documents: (a) scope and consumer; (b) versioning scheme;
(c) what is covered and what is internal, usually as a list; (d) rules by consumer role (Symfony, Eclipse,
Drupal interfaces) or by kind of change (Rust, .NET, Symfony's contributor tables); (e) experimental or
preview tiers; (f) the deprecation procedure, its markers and its window; (g) exceptions such as security and
bugs; (h) support and LTS; (i) where breaks and deprecations are announced (CHANGELOG, UPGRADE,
DEPRECATIONS.md, change records, dev notes).

## 4. Machine-readable markers of API surface and stability

| Marker | Meaning | Source |
| --- | --- | --- |
| PHP `@api` (phpDocumentor) | "highlight Structural Elements as being part of the primary public API of a package"; other public elements "are not recommended to be used by the consumer" | https://docs.phpdoc.org/guide/references/phpdoc/tags/api.html |
| PHP `@internal` (phpDocumentor) | an element "with public visibility should be regarded as exempt from the API" | https://docs.phpdoc.org/guide/references/phpdoc/tags/internal.html |
| PSR-5 / PSR-19 | Both are still **Draft** at PHP-FIG. The PSR-19 draft defines `@api`, `@internal` and `@deprecated` ("will be removed in a future version"). | https://www.php-fig.org/psr/ ; https://github.com/php-fig/fig-standards/blob/master/proposed/phpdoc-tags.md |
| PHP `#[\Deprecated]` | Since PHP 8.4, with `message` and `since` (free text). Using a marked element emits `E_USER_DEPRECATED`. Targets: functions, methods, class constants; 8.5 adds traits and global constants. | https://www.php.net/manual/en/class.deprecated.php |
| PHP `final` | The language prevents extending a class and overriding a method or constant (constants since 8.1). | https://www.php.net/manual/en/language.oop5.final.php |
| `@final` (docblock) | Symfony's convention: final "without enforcing it"; `@final since x.y` announces it | https://symfony.com/doc/current/contributing/code/bc.html |
| `@psalm-internal <ns>` | "internal to a given namespace or class or even method". `@psalm-api` marks something as used (for the unused-code checks), not as stable. | https://psalm.dev/docs/annotating_code/supported_annotations/ |
| PHPStan `@internal` checks | `method.internal` and related identifiers fire when an `@internal` element is used "from outside its root namespace" | https://phpstan.org/error-identifiers/method.internal |
| PHPStan deprecation rules | Report uses of `@deprecated` symbols, but not from code that is itself deprecated | https://github.com/phpstan/phpstan-deprecation-rules |
| Java `@Deprecated(since, forRemoval)` | `forRemoval=true` means "intent to remove … in a future version" | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Deprecated.html |
| Java `@API(status, since, consumers)` (apiguardian) | INTERNAL ("Might be removed without prior notice"), DEPRECATED ("Might disappear in the next minor release"), EXPERIMENTAL, MAINTAINED (no break for at least the next minor), STABLE (no break in the current major). `consumers` names the intended consumer packages. | https://raw.githubusercontent.com/apiguardian-team/apiguardian/main/src/main/java/org/apiguardian/api/API.java |
| Kotlin `@RequiresOptIn` / `@OptIn` / `@SubclassOptInRequired` | Opt-in markers for unstable APIs, at WARNING or ERROR level. `@SubclassOptInRequired` is for an API that is "stable to use but unstable to extend". | https://kotlinlang.org/docs/opt-in-requirements.html |
| androidx `RequiresOptIn` | "part of an unstable or otherwise non-standard API surface" | https://developer.android.com/reference/kotlin/androidx/annotation/RequiresOptIn |
| androidx `@Experimental` | *Not verified* (no page fetched); the androidx `RequiresOptIn` page does not mention its predecessor. | — |
| Rust `#[deprecated(since, note)]` | rustc does not interpret `since`; rustdoc shows it | https://doc.rust-lang.org/reference/attributes/diagnostics.html |
| Rust `#[non_exhaustive]` | "may have more fields or variants added in the future"; downstream code must use `..` and `_` | https://doc.rust-lang.org/reference/attributes/type_system.html |
| Rust `#[stable]` / `#[unstable]` | Need `#![feature(staged_api)]`, so they are for std only in practice | https://rustc-dev-guide.rust-lang.org/stability.html |
| TSDoc `@public` / `@beta` / `@alpha` / `@internal` (API Extractor) | `@public` is "part of the supported contract for a package"; `@internal` is for "other NPM packages from the same maintainer". Tags apply to members recursively. | https://api-extractor.com/pages/tsdoc/doc_comment_syntax/ |
| Python `@warnings.deprecated` (PEP 702, 3.13) | `DeprecationWarning` at runtime; type checkers should report each use | https://peps.python.org/pep-0702/ |
| Python `__all__`, `_name` | Declares the public names (PEP 8) | https://peps.python.org/pep-0008/#public-and-internal-interfaces |
| Go `internal/` | Import restriction enforced by the toolchain | https://pkg.go.dev/cmd/go |
| .NET `[Obsolete]` | Build warning carrying a migration message | https://learn.microsoft.com/en-us/dotnet/standard/library-guidance/breaking-changes |
| OpenAPI 3.1 `deprecated` | Operation: "Consumers SHOULD refrain from usage"; Parameter: "SHOULD be transitioned out of usage" | https://spec.openapis.org/oas/v3.1.0.html |
| JSON Schema `deprecated` | Boolean, on a property or the whole resource (used by OpenAPI 3.1 Schema Objects) | https://json-schema.org/draft/2020-12/json-schema-validation#name-deprecated |
| HTTP `Sunset` (RFC 8594, Informational) | The date a URI is expected "to become unresponsive"; a `sunset` link relation points to the retirement policy | https://www.rfc-editor.org/rfc/rfc8594.html |
| HTTP `Deprecation` (RFC 9745, Standards Track, March 2025) | A structured-field date; a `deprecation` link relation points to human documentation, either before (as the policy) or after (as migration). `Sunset` must not be earlier. | https://www.rfc-editor.org/rfc/rfc9745.html |

## 5. Tools that check BC and API surface

| Tool | How it gets the API | Baseline / declared file | Source |
| --- | --- | --- | --- |
| Roave BackwardCompatibilityCheck (PHP) | From code (composer `autoload` paths, git) | By default compares against the last minor SemVer tag (`x.y.z` needed). Optional `.roave-backward-compatibility-check.xml` with a `<baseline>` of ignored regexes. Markdown and GitHub output. *Not verified from the README:* how it treats `@internal`. | https://github.com/Roave/BackwardCompatibilityCheck |
| Psalm / PHPStan | From docblocks | Report use of `@internal`, `@psalm-internal` and `@deprecated`. They check consumers of the API, not changes to it. | see section 4 |
| Microsoft API Extractor (TS) | From `.d.ts` exports at the entry point | **Declared and reviewed file:** `etc/<pkg>.api.md`, kept in git. A CI build fails when it is out of date, and branch policy can require approval of changes to it. Release tags are part of the report. | https://api-extractor.com/pages/overview/demo_api_report/ ; https://api-extractor.com/pages/overview/intro/ |
| japicmp (Java) | From two jar files (bytecode) | Separates source from binary compatibility. `--semantic-versioning` says which version part to bump. Include/exclude by package or annotation. *Not verified:* which annotations it knows by name. | https://siom79.github.io/japicmp/ |
| Revapi (Java and others) | From code and artifacts, also JSON and YAML | Lets you mark changes as intentional; "in beta". *Not verified:* annotation filters and semver checks, which the fetched page does not describe. | https://revapi.org/revapi-site/main/index.html |
| cargo-semver-checks (Rust) | From rustdoc JSON | Baseline: the previous release on crates.io, or a git rev. Aims for no false positives and has known gaps (type, generics and feature-subset changes). | https://github.com/obi1kenobi/cargo-semver-checks |
| Go apidiff | From two package or module versions | Reports incompatible or compatible changes. Ignores five known kinds of break and states that "No tool can detect behavioral changes". | https://pkg.go.dev/golang.org/x/exp/apidiff |
| Go gorelease | Compares against a base version | Suggests or checks the next version. A break at v1 or above needs a new module path. *Not verified:* that it builds on apidiff; the page does not say. | https://pkg.go.dev/golang.org/x/exp/cmd/gorelease |
| griffe check (Python) | From code; "your public API is what you say it is"; `_` means private | Baseline: the latest git tag or a PyPI release. Lists the kinds of break it finds (parameter changes, object removed, and more). | https://mkdocstrings.github.io/griffe/guide/users/checking/ |
| .NET ApiCompat / package validation | From assemblies and packages | `PackageValidationBaselineVersion`. An accepted break goes into `CompatibilitySuppressions.xml`, which is committed "to document and review the breaking changes". Strict mode also catches additions. | https://learn.microsoft.com/en-us/dotnet/fundamentals/apicompat/overview ; https://learn.microsoft.com/en-us/dotnet/fundamentals/apicompat/package-validation/baseline-version-validator |
| .NET PublicApiAnalyzers | From source (Roslyn analyzer) | **Declared surface files:** `PublicAPI.Shipped.txt` and `PublicAPI.Unshipped.txt`. RS0016: a public API is not declared. RS0017: an API was removed without a `*REMOVED*` entry in Unshipped. *Not verified:* the step that moves entries from Unshipped to Shipped, which the fetched pages do not describe. | https://github.com/dotnet/roslyn-analyzers/blob/main/src/PublicApiAnalyzers/PublicApiAnalyzers.Help.md ; https://github.com/dotnet/roslyn-analyzers/blob/main/src/PublicApiAnalyzers/Microsoft.CodeAnalysis.PublicApiAnalyzers.md |

In short, nearly every tool needs only **a baseline release (a tag or a published package) plus the code**. Only
API Extractor and PublicApiAnalyzers keep a **declared surface file** in the repository, and .NET's
suppression file and Roave's baseline record **accepted breaks**. All the code-based tools read the
ecosystem's visibility rules (`public`, `_`, `internal/`, exports) as the API. They know nothing of a
project's own wider exclusions, such as Symfony's "extending is not covered for X", unless those are
configured.

## 6. Best-practice guidance on writing the policy

No single best-practice guide was found. The guidance is spread across the specs above:

- **Name the consumer and how it depends.** .NET weighs low-level against high-level libraries
  (https://learn.microsoft.com/en-us/dotnet/standard/library-guidance/breaking-changes). Eclipse and
  Symfony split consumers into caller, implementor and subclasser.
- **State coverage and exclusions explicitly.** Undocumented does not mean private in PEP 387, but Node and
  Django treat documented as the boundary. Hyrum's Law: "all observable behaviors of your system will be
  depended on by somebody" (https://www.hyrumslaw.com/). It is the reason to name behaviour, named
  arguments, messages and performance as excluded (Laravel, PHPUnit, .NET, Go 1).
- **Change kinds per release type.** SemVer, Go, Cargo (major / minor / possibly-breaking), .NET (allowed /
  disallowed / judgment).
- **Deprecation procedure, with a window counted in time and releases.** Kubernetes (months *or* releases,
  whichever is longer), PEP 387 (two years or two minors, five preferred), Django (two feature releases),
  Angular (at least one major), Symfony (removal only in the next major), PHPUnit (soft, then hard, then
  removal across two majors). Give the deprecation a marker *and* a runtime signal (Symfony
  `trigger_deprecation`, Drupal `@trigger_error`, Django `RemovedInDjangoXXWarning`, Node `DEP` IDs).
- **Experimental tiers sit outside the promise**, with limits: Symfony's one minor and no LTS, Kubernetes
  alpha/beta windows, Angular developer preview, Node Stability 1, Kotlin opt-in.
- **Exceptions**: security (Symfony, Django, Go, Drupal, TYPO3), bugs and unspecified behaviour (Go), a
  steering body (PEP 387, Node TSC, Kubernetes SIGs).
- **Relation to support and LTS** (Symfony, Laravel, Angular, Django, Node).
- **Where changes are announced.** Keep a Changelog has `Deprecated` and `Removed` sections and "If you do
  nothing else, list deprecations, removals, and any breaking changes in your changelog"
  (https://keepachangelog.com/en/1.1.0/). Others: `UPGRADE*.md` (Symfony, Doctrine), `DEPRECATIONS.md`
  (PHPUnit), change records (Drupal). Conventional Commits mark breaks with `BREAKING CHANGE:` or `!`, which
  map to MAJOR (https://www.conventionalcommits.org/en/v1.0.0/).

## 7. Synthesis: the questions a BC promise document answers

| # | Question | Answered by (examples) | Evidence an agent can read in a repository |
| --- | --- | --- | --- |
| 1 | **Is there a promise at all, and to whom?** (package users, addon/plugin/extension authors, API clients, nobody) | SemVer item 1; Cargo "application compatibility"; .NET project types; Symfony and Drupal for extension authors | `composer.json` `type` (`library`, `project`, `*-plugin`, custom); a published package (Packagist/npm/PyPI/crates.io name, `"name"` + `"version"` or tags); plugin/addon/hook/event APIs; `README` install instructions ("composer require …"); dependents on the registry (outside the repo) |
| 2 | **Which versioning scheme, and what does each part mean?** | SemVer, CalVer, Go modules, Django's move to CalVer, Laravel | git tags (`v1.2.3` or `2025.04`), `CHANGELOG` headings, `version` fields, branch aliases; a 0.x-only history (SemVer item 4: no stability) |
| 3 | **What is covered (the public API)?** | Symfony's "use" tables, Drupal "API definition", Angular "public API surface", PEP 387, Node "documented = public" | language visibility (`public`/`protected`); `@api`; `__all__`; package `exports`/entry points; `autoload` namespaces; generated API docs config (phpDocumentor, typedoc); declared surface files (`*.api.md`, `PublicAPI.*.txt`) |
| 4 | **What is explicitly excluded?** | `@internal` (Symfony, Drupal, PHPUnit, TYPO3), `_` names (PEP 387, Django, Node, Angular `ɵ`), `Tests\`, `internal/` (Go), named arguments (Laravel, PHPUnit, Drupal), constructors of services (Drupal, Angular), DOM/CSS (WordPress block editor, TYPO3), behaviour and performance (Go 1) | counts and locations of `@internal`, `@psalm-internal`, `@no-named-arguments`; `internal`/`Internal` namespaces or directories; `_`-prefixed names; test namespaces; DI-container service definitions (constructors not meant for users) |
| 5 | **What may each consumer role rely on: use, extend, implement?** | Symfony (three roles), Eclipse (caller/implementor/subclasser), Drupal interfaces (`@api` vs untagged), Angular ("treated as final"), Kotlin `@SubclassOptInRequired` | the share of `final` classes and methods; `@final`/`@final since`; abstract base classes and interfaces documented as extension points; `#[non_exhaustive]`; docs that say "extend X" or "implement Y" |
| 6 | **Which changes are allowed in which release type?** | SemVer 7–8, RFC 1105, Cargo, .NET rules, Symfony contributor tables, Go module docs | a changelog's classification history (`[BC BREAK]` in minors, Conventional Commits `!`); release tags compared with the content of breaks; a configured BC checker (Roave, japicmp, cargo-semver-checks, griffe) |
| 7 | **How is something deprecated, and how is it marked?** | Symfony (`@deprecated since` + `trigger_deprecation`), Drupal (fixed text + change record), Doctrine (`doctrine/deprecations`), Django warning classes, Node DEP IDs, PHP `#[\Deprecated]`, Java `forRemoval` | existing `@deprecated` texts and their format (contains a version? a replacement?); `trigger_deprecation`/`trigger_error(E_USER_DEPRECATED)`/`#[\Deprecated]` calls; `symfony/deprecation-contracts` or `doctrine/deprecations` in `require`; PHPStan deprecation rules in `require-dev` |
| 8 | **How long does a deprecated element survive (minimum window)?** | Kubernetes (months or releases), PEP 387, Django, Angular, Symfony (next major), PHPUnit (two majors), TYPO3 | the gap between the deprecation version and the removal version in `CHANGELOG`/`UPGRADE*`; `@deprecated … removed in X` texts; the release cadence from tag dates |
| 9 | **How are experimental or unstable parts handled?** | Symfony `@experimental`, Node Stability 1, Kubernetes alpha/beta, Angular developer preview, Kotlin opt-in, TSDoc `@beta`/`@alpha`, Python provisional | `@experimental`, `@beta` tags; `Experimental`/`Beta` namespaces; feature flags; `0.x` sub-packages |
| 10 | **What exceptions override the promise?** | security (Symfony, Django, Go 1, Drupal, TYPO3), bugs and unspecified behaviour (Go 1), steering-body decisions (PEP 387, Node TSC, Kubernetes) | `SECURITY.md`; governance files; there is rarely code evidence, so this is usually a question for the human |
| 11 | **What is supported, and for how long (branches, LTS)?** | Symfony releases page, Laravel table, Angular, Django, Node release | maintained branches (`4.x`, `5.4`), a support table in the README, CI matrices across branches, a `SECURITY.md` supported-versions table |
| 12 | **Where are deprecations and breaks announced, and how does a user upgrade?** | Keep a Changelog `Deprecated`/`Removed`; Symfony and Doctrine `UPGRADE*.md`; PHPUnit `DEPRECATIONS.md`; Drupal change records; WordPress dev notes | `CHANGELOG*`, `UPGRADE*`, `DEPRECATIONS*`, `docs/upgrade*`; release notes on the forge |
| 13 | **Which non-code surfaces are covered?** (CLI flags, config files, HTTP API, events/hooks, DB schema, translations, templates) | Kubernetes (CLI, metrics, feature gates), Drupal (CLI options, config, strings, schema internal), TYPO3 (hooks, routes, middlewares, CLI), Symfony translations, OpenAPI `deprecated`, `Deprecation`/`Sunset` headers | `bin/` console commands; config schema files; OpenAPI specs with `deprecated: true`; event/hook dispatch calls; migration files; translation files |
| 14 | **How is the promise checked?** | Roave, japicmp, cargo-semver-checks, griffe, ApiCompat, API Extractor reports | a BC check job in CI; `.roave-backward-compatibility-check.xml`; `CompatibilitySuppressions.xml`; `*.api.md`; `PublicAPI.*.txt` |

Notes for the Stage:
- Questions 1, 3, 4, 5 and 7 have the strongest code evidence. Questions 8, 10 and 11 often need the human.
- Evidence of *practice* (how earlier deprecations were done) differs from a *promise*. A draft can describe
  the observed practice, but only the reviewer can turn it into a commitment.
- Symfony's split into a consumer-facing part ("Using …") and a contributor-facing part ("Working on …")
  is a reusable structure. The draft needs the consumer part; the contributor part is what the suite itself
  reads.

## 8. What does not exist

- **No formal standard or template for a "BC promise document"** was found: no RFC, ISO, PSR or PEP that
  specifies its sections. SemVer requires a declared public API but deliberately leaves the form open (item 1,
  https://semver.org/spec/v2.0.0.html). CalVer says outright that it does not communicate breaking changes
  (https://calver.org/).
- **No cross-ecosystem machine-readable declaration of a promise.** Nothing comparable to `SECURITY.md` or
  `CODEOWNERS` for compatibility turned up, and no `composer.json`, `package.json` or `pyproject.toml` field
  states "this package follows SemVer" or a deprecation window. This was not searched exhaustively; it is
  the absence of any hit across the sources read.
- **PHP has no accepted standard for `@api` and `@internal`.** PSR-5 and PSR-19 are still Draft
  (https://www.php-fig.org/psr/). Their meaning comes from phpDocumentor and the tools' conventions (Psalm:
  namespace-scoped `@psalm-internal`; PHPStan: the root namespace), and these do not fully agree.
- **No tool checks a project-specific promise.** All checkers compare visibility-based APIs. A promise that
  excludes extending non-final classes, or one counted in months, needs configuration or human judgement.
- **Unverified items:** WordPress core policy (pages unreachable), the TYPO3 changelog entry types,
  Laravel's and Doctrine's public/internal definitions, androidx `@Experimental`, Roave's `@internal`
  handling, japicmp's annotation names, Revapi filters, the gorelease–apidiff relation, and the
  PublicApiAnalyzers Shipped/Unshipped workflow. Each is marked in its section.
