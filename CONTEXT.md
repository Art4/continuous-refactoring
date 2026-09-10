# Continuous Refactoring

The vocabulary of a portable agent-skill suite that keeps a software project under continuous refactoring — a stateful, repeatable loop that finds, plans, executes, verifies, and records structural improvements.

## Language

**Candidate**:
A backlog item filed on the project's issue tracker — either a structural deepening or a missing node on the **tooling tree**.
_Avoid_: task, ticket, todo

**Backlog**:
The set of candidate issues on the tracker, awaiting prioritisation.
_Avoid_: debt list, todo list

**Loop pass**:
One run of the orchestrator. The orchestrator carries each lifecycle skill's output to the next skill's input (ADR-0010) rather than each skill re-deriving its own context: `refactor-scan` proposes every currently-unblocked tooling-tree node and separately detects (never acts on) remembered merge requests that have since merged or closed; `refactor-learn` is the pass's only writer, acting on scan's findings and, once fewer than two suite merge requests are open, closing out at most one completed **candidate** (propose → prioritise → design → implement → learn).
_Avoid_: session, sprint

**Merge request**:
The forge reviewable that delivers a completed candidate. Skills always use this term; conversation with the human uses the forge's native word (pull request on GitHub, merge request on GitLab).
_Avoid_: PR (in skills), delivery (as a second name for the same artifact)

**Tooling tree**:
The directed graph of adoption steps a target repo climbs — a generic root (`skills/refactor-scan/references/tooling-tree.md`: `git`, `loop-config`) that every language specialization's tree (PHP: `skills/refactor-scan/references/php-tooling-tree.md`) attaches beneath. A **node** adopts one tool, or one suite-level prerequisite at the root, up to a stated degree — a tool may own several nodes (each PHPStan level is its own node). Operational lessons discovered while adopting or fulfilling a node are worked directly into its Purpose/Fulfilment check/MR scope prose, not tracked as a separate entry. Each node also carries a human-facing **Name** (the tree doc's `**Name:**` field), used instead of the slug anywhere a human reads it — issue titles, merge requests, the loop's closing report; internal bookkeeping (the edges table, the **Refactoring Notes**' `out-of-scope/` filenames, ledger matching) stays keyed by the slug. A node may also carry a **Housekeeping** field — a recurring-maintenance line contributed to `housekeeping-template.md` (below), ordinarily when the node's own MR delivers, or via the separate `continuous-housekeeping` skill's own reconciliation pass for a node already fulfilled before that file existed; unrelated to the node's own one-time Fulfilment check. A node may also carry a **Signal** field, naming which `signals.md` factor its tool output feeds once the node is adopted — see the **Signal** entry below for the full picture across both usages. Deliberately not every node produces one: a node can gate `structural-scan` without producing a Signal, and vice versa — a Signal-producing node like `phpmd` or `secret-detection` carries no `resolved` edge into `structural-scan` at all (see those nodes' own entries in `php-tooling-tree.md`/`tooling-tree.md`).
_Avoid_: baseline, floor, bootstrap, onboarding

**Fulfilment check**:
A node's own test for whether it's already adopted — the specific, node-owned criterion (a
dependency present, a config committed, a CI job actually invoking the tool, …) that `tooling_tree.
py`'s deterministic parser and the manual/LLM tree-walk fallback both evaluate the same way. Lives in
the node's own tree-doc entry, alongside its **MR scope** (what an adoption's merge request actually
delivers) — every node carries both, together they're what "a node" (above) means operationally.
_Avoid_: adoption check, acceptance criteria

**Entry point**:
A PHP file the runtime (webserver or CLI) executes directly — never `require`d or `include`d by another file in the target's own source tree. `psr-4`'s autoloader-wiring step (`skills/refactor-scan/references/php-tooling-tree/psr-4.md`) targets every entry point directly when the target has no single **Composition root**.
_Avoid_: front controller

**Composition root**:
The one file, if any, the target's own **Entry point**s mostly delegate to for wiring the application together — the single place a target's own manual class-loading historically accumulates. Not every target has one, and recognizing one doesn't require unanimous delegation: an entry point that doesn't delegate to it still gets wired directly, on top of the root rather than in place of it. The kind of gap `psr-4`'s wiring step exists to close lives exactly here: a class missing from this one file's own manual require list, invisible to every autoloader-based test.
_Avoid_: bootstrap file (a file literally named `bootstrap.php` isn't necessarily filling this role), application root

**Refactoring Notes**:
The target repo's own folder holding the loop's state — `bookkeeping.md`, `merge-requests.md`, `out-of-scope/`, `housekeeping-template.md` (only once `continuous-housekeeping` has contributed at least one line — see that skill). Default `docs/refactoring/`; overridable per target, decided once during `loop-config`'s own interview and recorded, by this name, in that target's `AGENTS.md`/`CLAUDE.md` (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`) — every other skill refers to it by this name, never by restating the concrete path.
_Avoid_: suite folder, config folder, state folder

**Housekeeping** (recurring maintenance):
A periodic maintenance sweep — dependency currency, tooling-deprecation cleanup, documentation sync — run by the separate `continuous-housekeeping` skill on its own configurable cadence (default weekly), independent of the continuous-refactoring loop's own scan/design/implement/learn pipeline. Never a tooling-tree node: nothing about it is a one-time adoption with a stable Fulfilment check, and the tree's own parser has no forge access to derive a cadence from tracker history the way this skill does.
_Avoid_: maintenance loop, chore loop, cleanup pass

**Required edge**:
The gating edge between nodes: a node is proposed only once every parent linked by a required edge is fulfilled; rejecting a required parent closes every node beneath it.
_Avoid_: hard edge, blocking edge

**Recommended edge**:
The counterpart that gates on a decision rather than on fulfilment (ADR-0016): a node is proposed only once every parent linked by a recommended edge is _decided_ — fulfilled, or rejected. A rejected recommended parent still releases the child instead of closing it, unlike a required parent; the rejected parent is never re-proposed. A recommended parent that hasn't been reached yet at all counts as undecided too, withholding the child just the same as one that's merely sitting proposed-but-unactioned.
_Avoid_: soft edge, nice-to-have edge, non-blocking edge

**Required-any edge**:
An OR variant of the required edge (ADR-0019): a node with required-any parents is proposed once _at least one_ of them is fulfilled, not all — distinct from a **choice** (below), which is about mutual exclusion between siblings, not about unlocking a downstream child from either side. Combines with a node's ordinary required parents (if any) via AND between the two edge types, OR within the required-any group itself.
_Avoid_: optional required edge, either-or edge

**Choice**:
Two or more sibling nodes under a shared required parent where adopting one makes the others out-of-scope by design — recorded the same way any other rejection is, via an `out-of-scope/<node>.md` entry (in the **Refactoring Notes**) for the unchosen sibling(s), not a separate mechanism. The tree has no dedicated XOR primitive; a choice is just an ordinary sibling pair plus the convention that picking one means rejecting the rest.
_Avoid_: XOR, either-or

**Floor correction**:
Bringing `composer.json`'s declared PHP floor (`require.php`) in line with what the codebase's own source already demonstrably requires — behavior-preserving, since nothing observable changes, only the metadata now tells the truth. The only node that produces this: `php-minimal-version` (`skills/refactor-scan/references/php-tooling-tree/php-minimal-version.md`), triggered once `rector-php-set` has fully applied a PHP-version rule set.
_Avoid_: floor bump, floor raise (see **Floor raise** — a different, deliberately out-of-scope thing)

**Floor raise**:
Committing the application to a newer PHP version than its own code currently requires — a genuine **Breaking change**, a product decision, never autonomously proposed by any tooling-tree node. Distinct from **Floor correction** (above), which changes only metadata to match already-existing reality.
_Avoid_: floor bump, upgrade (collides with `rector-php-set`'s own "PHP-upgrade rule set" wording — syntax modernization, a different concern)

**Hot spot**:
A part of the codebase that keeps appearing in change history — the primary place to look for candidates.
_Avoid_: problem area, pain point

**Deepening**:
The refactoring move that turns a shallow module into a deep one.
_Avoid_: cleanup, tidy-up

**Deletion test**:
The test for shallowness: would deleting this module concentrate complexity, or just move it?
_Avoid_: (none — use the term as-is)

**Breaking change** (behavior-preserving):
Any change to a target's observable behavior — never shipped under the refactor label; routes to the normal feature/bug path instead (`docs/adr/0004-foundational-refactoring-rules.md`). The loop's refactors are always behavior-preserving by definition; a **Floor raise** (above) is the canonical example of something that looks like tooling-tree housekeeping but is actually this.
_Avoid_: incompatible change

**Seam**:
The public boundary at which a module is tested — where tests observe behaviour without reaching inside.
_Avoid_: boundary, internal hook

**Tooling pressure**:
A candidate that an already-fulfilled tooling-tree node keeps surfacing — things that will re-fail until fixed.
_Avoid_: lint noise, tool complaints

**Leverage**:
How much future change does deepening this module unlock? A module many others call is high-leverage; a leaf nobody calls is not.
_Avoid_: (none — use the term as-is)

**Locality**:
What moves together, and what must not spread? The degree to which related code lives in one place rather than scattered across the codebase.
_Avoid_: (none — use the term as-is)

**Plan**:
The concrete refactoring plan produced by `refactor-design`: the deepened module, its seam, the interface, and the surviving tests — written on the candidate issue so the refactor is delegable.
_Avoid_: design doc

**Proposals**:
The tooling-tree node names `refactor-scan` hands the orchestrator, every currently-unblocked one, however many that is — not yet candidates, since nothing is filed until `refactor-prioritize`'s Rank mode picks one. Filing itself happens in `refactor-prioritize`'s Select mode (a concrete instance selected first, for a gate) or, for an already-concrete winner, in `refactor-design` directly — either way, `refactor-design` adds the plan afterward. One narrow exception files outside this flow entirely: a secret-history-scan **finding** (above) becomes its own `refactor:priority` candidate filed directly by `refactor-learn`, no `refactor-prioritize`/`refactor-design` step at all — there's nothing to rank or design, the finding is already concrete.
_Avoid_: suggestions, recommendations (that's `refactor-prioritize`'s output, one level further)

**Signal**:
The named factor (heat, leverage, security, blast radius of inaction, …) that qualified a candidate as a genuine friction spot. The full catalogue lives in `skills/refactor-prioritize/references/signals.md`; two of its factors (security, blast radius of inaction) additionally mark a candidate as **priority**, exempting it from the backlog's ordinary admission cap. Two distinct places carry this name: (1) the third field on a candidate issue, alongside Where and Problem, that `refactor-prioritize`'s Select mode names when it files one; (2) a node-level **Signal** field on a **tooling tree** node (see that entry above) — once a Signal-producing node like `phpmd` or `secret-detection` is adopted, its own real tool output is what Select mode reads for that factor, in place of the generic (reading-the-code) recognition method a candidate issue's own Signal field would otherwise rely on. A tooling-tree node's Signal field never gates `structural-scan`; it only ever strengthens candidate selection.
_Avoid_: (none — use the term as-is)

**Findings**:
Remembered issues or merge requests `refactor-scan` detects have since merged, closed, or — a candidate MR left in draft by an earlier interrupted pass, its fold-in bookkeeping never landed — are still open but owe a write `refactor-learn` never got to finish. Also covers a genuinely new discovery this same pass, not a remembered item's changed state — a secret a git-history scan turns up (`refactor-scan/SKILL.md` step 4c) is a finding the same way. Handed to `refactor-learn` to act on either way. Scan only notices; it never decides the outcome itself.
_Avoid_: events, notifications