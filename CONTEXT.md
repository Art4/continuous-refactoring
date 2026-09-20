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
The directed graph of adoption steps a target repo climbs — a generic root (`skills/refactor-scan/references/tooling-tree.md`: `git`, `loop-config`) that every language specialization's tree (PHP: `skills/refactor-scan/references/php-tooling-tree.md`) attaches beneath. A **node** adopts one tool, or one suite-level prerequisite at the root, up to a stated degree — a tool may own several nodes (each PHPStan level is its own node). Operational lessons discovered while adopting or fulfilling a node are worked directly into its Purpose/Fulfilment check/MR scope prose, not tracked as a separate entry. Each node also carries a human-facing **Name** (the tree doc's `**Name:**` field), used instead of the slug anywhere a human reads it — issue titles, merge requests, the loop's closing report; internal bookkeeping (the edges table, the **Refactoring Notes**' `out-of-scope/` filenames, ledger matching) stays keyed by the slug. A node may also carry a **Housekeeping** field — a recurring-maintenance line contributed to `housekeeping-template.md` (below), ordinarily when the node's own MR delivers, or via the **Housekeeping** Track's own reconciliation pass for a node already fulfilled before that file existed; unrelated to the node's own one-time Fulfilment check. A node may also carry a **Signal** field, naming which `signals.md` factor its tool output feeds once the node is adopted — see the **Signal** entry below for the full picture across both usages. Deliberately not every node produces one: a node can gate `structural-scan` without producing a Signal, and vice versa — a Signal-producing node like `phpmd` or `secret-detection` carries no `resolved` edge into `structural-scan` at all (see those nodes' own entries in `php-tooling-tree.md`/`tooling-tree.md`).
_Avoid_: baseline, floor, bootstrap, onboarding (as a name for the tree itself — it never stops being walked; see the dedicated **Onboarding** entry below for the bounded phase within it, which is a real term)

**Track**:
One of four scheduled work modes a loop pass can spend itself on: **Safety Net**, **Guardrails**, **Investigation**, **Housekeeping** (all below). Each carries its own `Cadence` and `Last scan` in `bookkeeping.md` — Investigation's own `Cadence` is always the literal `continuous`, never a day count, making it always due with no ratio to compute; that's what makes it the scheduler's permanent fallback whenever nothing else outranks it (`skills/continuous-refactoring/references/track-scheduler.md`). A pass runs whichever due Track is most overdue relative to its own cadence — ties, and effort allocation when several Tracks hold open work simultaneously, fall back to the fixed order Safety Net > Guardrails > Housekeeping > Investigation. **Safety Net blockade:** while Safety Net `Open` is non-empty, it is selected and nothing else runs, even if no node is currently workable; the wait is reported. **Guardrails yielding:** with at least one workable `Open` node, Guardrails is selected ahead of Investigation; with nothing workable, it yields. **Housekeeping preemption:** Housekeeping can preempt Guardrails for one pass when due (`overdue_ratio >= 1`). **Investigation waiting:** Investigation waits behind a Guardrails backlog with workable nodes. One deliberate exception, per target, one time only: the pass right after the Safety Net Track's `Open` list first empties runs Investigation, then Guardrails, then Housekeeping, one turn each in that order, before the ordinary priority order takes over — a target sees one real piece of delivered refactoring value before being asked to adopt more tooling or sit through maintenance. At most one Track is selected per pass. A Track's `bookkeeping.md` section doesn't exist until its first run — absence means "never run," not "nothing found"; the first run always records at least `Last scan`, even when it finds nothing, so a fully-compliant Track still gets its cadence honored afterward.
_Avoid_: wave (this concept's earlier name; retired once it started colliding with **Guardrails**' own former name, "Signal wave" — see that entry)

**Onboarding**:
The phase of a target's own tree walk from a bare repo through `git`, `loop-config`, the language specialization's recognition gate, and every node in the **Safety Net** (below) — everything before `structural-scan` opens. Bounded and, per target, effectively one-time, unlike the **Tooling tree** itself (above), which is walked forever. Only `git`/`loop-config` are their own, separately engineered step — a mandatory human interview, since `bookkeeping.md` doesn't exist yet and Create-mode/Focus areas/Refactoring goal are genuine preferences no scan can derive. Everything from the recognition gate onward is simply what the Safety Net **Track**'s very first run finds — the same mechanism as any later run, just with more to discover the first time.
_Avoid_: baseline, bootstrap (see **Tooling tree**'s own `_Avoid_` list — those describe the never-ending tree; this term names only the bounded early phase within it)

**Safety Net**:
The tooling-tree nodes carrying a `resolved` edge into `structural-scan` (generic root: `editorconfig`, `ci-runner`) or into a language specialization's own aggregation node (PHP: `php-safety-net`) — deterministic tooling whose findings could collide with agent-driven structural work, settled before that work starts. Narrower than **Onboarding** (above): every Safety Net node lives inside Onboarding, but `git`/`loop-config`/the recognition gate aren't Safety Net nodes themselves. Also names the **Track** (above) that works through these nodes.
_Avoid_: baseline, tooling gate

**Guardrails**:
The tooling-tree nodes proposed only once the **Safety Net** (above) has closed — required-gated on `structural-scan`/`php-safety-net` itself instead of (or alongside) a domain-specific parent. Also names the **Track** (above) that works through these nodes. Orthogonal to a node's own **Signal** field (below): a Guardrails node always carries one, but a Safety Net node can too (`psalm-taint-analysis`) — one names *when* a node is proposed, the other names *which factor* it feeds once adopted.
_Avoid_: signal wave (this concept's former name — renamed for symmetry once both it and **Safety Net** became **Track** names, and to stop reading as an alternate spelling of the unrelated **Signal** field below), security wave (not every Guardrails node is security-flavored — `phpmd`/`coverage-floor` feed Understandability/Testability, not Security)

**Fulfilment check**:
A node's own test for whether it's already adopted — now agent-judged for every node. An agent walking the tree during its **Track**'s scan recognizes any real, working tool that serves the node's stated Purpose rather than matching a fixed list of names (a Laravel-Pint-configured target satisfies `php-cs-fixer`'s Fulfilment check the same as a directly-configured one). Lives in the node's own tree-doc entry, alongside its **MR scope** (what an adoption's merge request actually delivers) — every node carries both, together they're what "a node" (above) means operationally.
_Avoid_: adoption check, acceptance criteria

**Entry point**:
A PHP file the runtime (webserver or CLI) executes directly — never `require`d or `include`d by another file in the target's own source tree. `psr-4`'s autoloader-wiring step (`skills/refactor-scan/references/php-tooling-tree/psr-4.md`) targets every entry point directly when the target has no single **Composition root**.
_Avoid_: front controller

**Composition root**:
The one file, if any, the target's own **Entry point**s mostly delegate to for wiring the application together — the single place a target's own manual class-loading historically accumulates. Not every target has one, and recognizing one doesn't require unanimous delegation: an entry point that doesn't delegate to it still gets wired directly, on top of the root rather than in place of it. The kind of gap `psr-4`'s wiring step exists to close lives exactly here: a class missing from this one file's own manual require list, invisible to every autoloader-based test.
_Avoid_: bootstrap file (a file literally named `bootstrap.php` isn't necessarily filling this role), application root

**Refactoring Notes**:
The target repo's own folder holding the loop's state — `bookkeeping.md`, `merge-requests.md`, `out-of-scope/`, `housekeeping-template.md` (only once some tooling-tree node's own `Housekeeping` field has contributed at least one line — see the **Housekeeping** entry, below, and the **Tooling tree** entry above). Default `docs/refactoring/`; overridable per target, decided once during `loop-config`'s own interview and recorded, by this name, in that target's `AGENTS.md`/`CLAUDE.md` (`skills/continuous-refactoring/references/refactoring-bookkeeping.md`) — every other skill refers to it by this name, never by restating the concrete path.
_Avoid_: suite folder, config folder, state folder

**Housekeeping** (recurring maintenance):
A periodic maintenance sweep — dependency currency, tooling-deprecation cleanup, documentation sync. Also names the **Track** (above) that runs it, on its own configurable cadence (default weekly), scheduled alongside the other three Tracks rather than by a separate skill. Never a tooling-tree node: nothing about it is a one-time adoption with a stable Fulfilment check.
_Avoid_: maintenance loop, chore loop, cleanup pass

**Required edge**:
The gating edge between nodes: a node is proposed only once every parent linked by a required edge is fulfilled; rejecting a required parent closes every node beneath it.
_Avoid_: hard edge, blocking edge

**Recommended edge**:
The counterpart that gates on a decision rather than on fulfilment (ADR-0016): a node is proposed only once every parent linked by a recommended edge is _decided_ — fulfilled, or rejected. A parent counts as rejected either directly (its own `out-of-scope/` entry) or transitively, when one of *its own* required ancestors is itself rejected — the same closure a required edge already causes for proposability (see **Required edge** above), just extended here to answer "decided" too, not only "still proposable." A rejected recommended parent (either way) still releases the child instead of closing it, unlike a required parent; the rejected parent is never re-proposed. A recommended parent that hasn't been reached yet at all counts as undecided too, withholding the child just the same as one that's merely sitting proposed-but-unactioned.
_Avoid_: soft edge, nice-to-have edge, non-blocking edge

**Required-any edge**:
An OR variant of the required edge (ADR-0019): a node with required-any parents is proposed once _at least one_ of them is fulfilled, not all — distinct from a **choice** (below), which is about mutual exclusion between siblings, not about unlocking a downstream child from either side. Combines with a node's ordinary required parents (if any) via AND between the two edge types, OR within the required-any group itself.
_Avoid_: optional required edge, either-or edge

**Choice**:
Two or more sibling nodes under a shared required parent where adopting one makes the others out-of-scope by design — recorded the same way any other rejection is, via an `out-of-scope/<node>.md` entry (in the **Refactoring Notes**) for the unchosen sibling(s), not a separate mechanism. The tree has no dedicated XOR primitive; a choice is just an ordinary sibling pair plus the convention that picking one means rejecting the rest.
_Avoid_: XOR, either-or

**Recognition-only gate node**:
A tooling-tree node that is never proposed as a candidate itself — it exists only as a required parent whose fulfilment gates other nodes. It is recognized (judged fulfilled or not by an agent) but never adopted through the ordinary propose → design → implement → learn pipeline. Its fulfilment is a prerequisite for downstream nodes, not work the suite performs. Example: `structural-scan` itself, which gates Investigation but is not itself a Track node.
_Avoid_: gate node (too broad — a gate node that is also proposed as a candidate is just a normal node)

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
The tooling-tree node names `refactor-scan` hands the orchestrator — every currently-unblocked one without an existing open candidate issue. `refactor-prioritize`'s Rank mode files a minimal candidate issue for each one (Name + Purpose line) before ranking — the same pattern Select mode already uses for a gate's own concrete findings (below), just without needing a gate to win first. `refactor-design` adds the plan afterward, once one wins a ranking (possibly a later one for a proposal that doesn't win immediately). `loop-config` is the one exception — its own interview is the only path that ever files it, never pre-filed like its siblings. Pre-filing no longer applies to Track nodes (Safety Net, Guardrails) — those are tracked in the Track's own `Open` list instead. A second, narrower exception files outside this flow entirely: a secret-history-scan **finding** (above) becomes its own `refactor:priority` candidate filed directly by `refactor-learn`, no `refactor-prioritize`/`refactor-design` step at all — there's nothing to rank or design, the finding is already concrete.
_Avoid_: suggestions, recommendations (that's `refactor-prioritize`'s output, one level further)

**Signal**:
The named factor (heat, leverage, security, blast radius of inaction, …) that qualified a candidate as a genuine friction spot. The full catalogue lives in `skills/refactor-prioritize/references/signals.md`; two of its factors (security, blast radius of inaction) additionally mark a candidate as **priority**, exempting it from the backlog's ordinary admission cap. Two distinct places carry this name: (1) the third field on a candidate issue, alongside Where and Problem, that `refactor-prioritize`'s Select mode names when it files one; (2) a node-level **Signal** field on a **tooling tree** node (see that entry above) — once a Signal-producing node like `phpmd` or `secret-detection` is adopted, its own real tool output is what Select mode reads for that factor, in place of the generic (reading-the-code) recognition method a candidate issue's own Signal field would otherwise rely on. A tooling-tree node's Signal field never gates `structural-scan`; it only ever strengthens candidate selection.
_Avoid_: (none — use the term as-is)

**Findings**:
Remembered issues or merge requests `refactor-scan` detects have since merged, closed, or — a candidate MR left in draft by an earlier interrupted pass, its fold-in bookkeeping never landed — are still open but owe a write `refactor-learn` never got to finish. Also covers a genuinely new discovery this same pass, not a remembered item's changed state — a secret a git-history scan turns up (`refactor-scan/SKILL.md` step 4c) is a finding the same way, as is a **Fulfilled at pick-up** discovery from the Track `Open` walk (below). `refactor-design` is the other origin: discovering, while grounding/grilling or planning a fix, that a candidate can't be done without changing behavior is a finding too (`skills/refactor-design/references/decision-gate.md`), handed straight to the closing call in the same pass instead of a plan. Handed to `refactor-learn` to act on either way — neither origin decides the outcome itself, only `refactor-learn` does.
_Avoid_: events, notifications

**Fulfilled at pick-up**:
The finding `refactor-scan`'s Track `Open` walk (`skills/refactor-scan/references/track-open-processing.md`) reports when its re-check — re-running a node's **Fulfilment check** right before working it — finds the node already served, typically adopted by hand since the last scan. `refactor-learn`'s early call acts on it: the node leaves its Track's `Open` with no merge request and nothing filed — scan only reports the finding, `refactor-learn` performs the removal, the suite's ordinary detect-never-write split.
_Avoid_: (none — use the term as-is)

**Flagged candidate**:
A candidate whose plan `refactor-design` already wrote, but which also surfaced a decision meeting
the ADR bar (hard to reverse, surprising without context, a real trade-off) while staying
behavior-preserving — distinct from a **Finding**'s breaking-change case, which never gets a plan at
all. The plan carries a proposed default plus an explicit open question on the issue
(`skills/refactor-design/references/decision-gate.md`); `ready-for-agent`
(`docs/agents/triage-labels.md`) is actively removed if the issue already carried one, and
`needs-info` is added in its place — the visible "waiting on you" signal — until a human confirms or
overrides it by commenting, removing `needs-info`, and adding `ready-for-agent` back.
`refactor-scan` treats a still-waiting one (`needs-info` present) as not resumable — it doesn't block
the rest of the backlog — and picks it back up the moment `ready-for-agent` appears.
_Avoid_: blocked candidate, paused candidate

**Decision trail**:
A bundled issue comment `refactor-design` posts once grilling settles (structural and
externally-labeled candidates only), naming every question that met the ADR bar and the answer
reached live with the human — distinct from a **Flagged candidate**'s open question, which is
unresolved and blocks `ready-for-agent`. Purely a record; unlike the decision gate, it never blocks
anything. No qualifying question that pass → no comment.
_Avoid_: grilling log, design notes