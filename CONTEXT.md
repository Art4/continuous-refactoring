# Continuous Refactoring

The vocabulary of a portable agent-skill suite that keeps a software project under continuous refactoring — repeated runs that find, plan, execute and verify structural improvements, with all state kept in the project's issue tracker and forge.

## Language

**Candidate**:
A **ticket** the suite works as refactoring: the adoption of a **tooling tree** node, a structural deepening, or a ticket a human wrote. Recognised by its subject, named in plain words in title and text — never by a fixed marker. A ticket a human wrote is picked up when the target's **Candidate** operation says how such tickets are marked, or when the call names it.
_Avoid_: task, todo

**Backlog**:
The ordered list of a **Track**'s tooling-tree nodes that are neither fulfilled nor rejected, blocked ones included — what the tree's parser emits and what a scan offers tickets for. Once the tickets exist, the **Worklist** is what a run works from.
_Avoid_: debt list, todo list

**Run**:
One call of the suite, from its first **decision point** to its end: reconcile → **Track** choice → scan (only when the Track needs one) → file tickets → select → design → implement → **merge request**. A run ends when the merge request is open, when the design cannot proceed without a human answer, or when nothing is workable; more work is another call, not a longer run. Nothing limits how many merge requests or candidates are open at once. The call takes free text the suite interprets — a Track, a restriction ("only the Rector nodes"), a ticket, the mode. Text addressed to the human says "run" and "skill suite".
_Avoid_: loop pass, session, sprint

**Decision point**:
One link of a **run**'s chain: the suite lays out what it found, the options, and one recommendation. Who decides is the run's mode (**Interactive / Autonomous**). Everything the suite writes to a tracker or a forge follows from a decision point.
_Avoid_: checkpoint, approval step

**Interactive** / **Autonomous**:
The two modes of a **run**. **Interactive**, the default: the human decides at every **decision point**. **Autonomous**: the suite takes its own recommendation at every one — the same chain, not a second path. Autonomous is said in the call, in free words, or mid-run ("carry on yourself from here"); it is never stored. Without that hint and with nobody answering, the run ends at the first decision point with a report and has written nothing. One write needs a human even in an autonomous run: changing the target's `AGENTS.md`.
_Avoid_: ask-each-time, human-opens, create-mode (settings that no longer exist)

**Worklist**:
The open **tickets** of a target, found by searching the tracker and sorted into **Tracks**: a ticket matching a tooling-tree node belongs to that node's Track, the open **Housekeeping ticket** to Housekeeping, everything else to Investigation. A ticket is _workable_ when it is open and its blockers are all done. The suite keeps no list of its own: a ticket's merge request, a rejection and the Housekeeping ticket are found by search each time.
_Avoid_: bookkeeping, open list, state file

**Merge request**:
The forge reviewable that delivers a completed candidate. Skills always use this term; conversation with the human uses the forge's native word (pull request on GitHub, merge request on GitLab).
_Avoid_: PR (in skills), delivery (as a second name for the same artifact)

**Issue tracker**:
Where a project's tickets live — described, not named: `docs/agents/issue-tracker.md` says how an agent reaches it, and its `## Refactoring operations` section holds the **Refactoring operations**. May be a different system than the **forge**.
_Avoid_: native-label tracker (the suite no longer sorts trackers by name or by label support)

**Forge**:
The system that hosts the repository and its **merge requests** (GitHub, GitLab, another host), read from the Git remote. The same system as the **issue tracker** on a GitHub or GitLab project; a different one where tickets live elsewhere (Redmine, Jira, local files).
_Avoid_: tracker (for where merge requests live)

**Refactoring operations**:
The named operations the suite needs from an **issue tracker**, one bullet each in that file's `## Refactoring operations` section. Required: **Search** (how tickets are searched, open and closed), **Done**, **Merge requests**. Optional: **Candidate** and **Priority** (hints for search and order), **Linked merge request**, **Comment author and time**, **Claim**, **Rejected** (how a rejection is recorded and found again — a closed ticket or a file, and where), **Blocked by** (how a ticket states what blocks it), **Housekeeping** (where the **Housekeeping template** lives and how the next **Housekeeping ticket** is made from it). A missing optional operation means the capability is absent and the suite takes its fallback: without **Blocked by** the dependency is a sentence in the ticket, without **Rejected** the suite proposes a place when the first rejection is recorded (`skills/continuous-refactoring/references/refactoring-operations.md`).

**Ticket**:
An issue on the project's tracker — the word the suite uses, in its own texts and towards the human, because it is the wording of the engineering skills the suite builds on. Not a synonym for **Candidate**: a candidate is a ticket the suite works as refactoring, not every ticket is one. A ticket the suite files names its subject in plain words in title and text (the tool's name), so a later search finds it; before filing, the suite searches for an existing ticket on the subject, open or closed.
_Avoid_: task, todo

**Tooling tree**:
The directed graph of adoption steps a target repo climbs — a generic root (the tooling-tree doc: `git`, `onboarding-setup`) that every language specialization's tree (PHP: the PHP tooling-tree doc) attaches beneath. A **node** adopts one tool, or one suite-level prerequisite at the root, up to a stated degree a tool may own several nodes (each PHPStan level is its own node). Operational lessons discovered while adopting or fulfilling a node are worked directly into its Purpose/Fulfilment check/MR scope prose, not tracked as a separate entry. Each node also carries a human-facing **Name** (the tree doc's `**Name:**` field), used instead of the slug anywhere a human reads it — ticket titles, merge requests, a run's reports; the tree's own internals (the edges table, the parser's input and output) stay keyed by the slug. A node may also carry a **Housekeeping** field — a recurring-maintenance line contributed to the **Housekeeping template** (below), ordinarily through the node's own merge request, or added by a **Housekeeping** run for a fulfilled node whose line is missing; unrelated to the node's own one-time Fulfilment check. A node may also carry a **Signal** field, naming which signals-catalogue factor its tool output feeds once the node is adopted — see the **Signal** entry below for the full picture across both usages. Deliberately not every node produces one: a node can gate `structural-scan` without producing a Signal, and vice versa — a Signal-producing node like `phpmd` or `secret-detection` carries no `resolved` edge into `structural-scan` at all (see those nodes' own entries in the tree docs).
_Avoid_: baseline, floor, bootstrap, onboarding (as a name for the tree itself — it never stops being walked; see the dedicated **Onboarding** entry below for the bounded phase within it, which is a real term)

**Track**:
One of four kinds of work a **run** can spend itself on: **Safety Net**, **Guardrails**, **Housekeeping**, **Investigation** (all below). Track choice is a **decision point**: the suite sorts the **worklist** into Tracks and recommends the first one, in that fixed order, with something workable. While Safety Net is not fulfilled, an autonomous run that finds nothing workable there ends with "Safety Net is waiting for merges"; a human may choose another Track. Once Safety Net is fulfilled, a Track with nothing workable is skipped within the same run. Housekeeping is recommended when its open **Housekeeping ticket**'s due date is reached, or when its mechanism is missing. A Track is scanned only when it has no trace yet in the tracker — no ticket of its nodes, open or closed, and no recorded rejection — or on request; with a trace, a node without an open ticket counts as done, and re-checking the tooling Tracks is a recurring **Housekeeping** task. A human names a Track in the call to work on it whatever the recommendation would be.
_Avoid_: wave (this concept's earlier name; retired once it started colliding with **Guardrails**' own former name, "Signal wave" — see that entry)

**Onboarding**:
The phase of a target's own tree walk from a bare repo through `git`, `onboarding-setup`, the language specialization's recognition gate, and every node in the **Safety Net** (below) — everything before `structural-scan` opens. Bounded and, per target, effectively one-time, unlike the **Tooling tree** itself (above), which is walked forever. Its first step, fulfilling the `onboarding-setup` node (Name "Onboarding Setup"), is not a scan: it is the first thing a call checks. A target whose tracker file has no `## Refactoring operations` section gets a short interview — where the tickets live and how the operations work there, nothing else — that writes the section; a section without **Search** gets it added the same way. Everything from the recognition gate onward is simply what the Safety Net **Track**'s first scan finds — the same mechanism as any later scan, just with more to discover the first time.
_Avoid_: baseline, bootstrap (see **Tooling tree**'s own `_Avoid_` list — those describe the never-ending tree; this term names only the bounded early phase within it)

**Safety Net**:
The tooling-tree nodes carrying a `resolved` edge into `structural-scan` (generic root: `editorconfig`, `ci-runner`) or into a language specialization's own aggregation node (PHP: `php-safety-net`) — deterministic tooling whose findings could collide with agent-driven structural work, settled before that work starts. Narrower than **Onboarding** (above): every Safety Net node lives inside Onboarding, but `git`/`onboarding-setup`/the recognition gate aren't Safety Net nodes themselves. Also names the **Track** (above) that works through these nodes.
_Avoid_: baseline, tooling gate

**Guardrails**:
The tooling-tree nodes workable only once the **Safety Net** (above) is fulfilled — required-gated on `structural-scan`/`php-safety-net` itself instead of (or alongside) a domain-specific parent. Also names the **Track** (above) that works through these nodes. Orthogonal to a node's own **Signal** field (below): a Guardrails node always carries one, but a Safety Net node can too (`psalm-taint-analysis`) — one names *when* a node becomes workable, the other names *which factor* it feeds once adopted.
_Avoid_: signal wave (this concept's former name — renamed for symmetry once both it and **Safety Net** became **Track** names, and to stop reading as an alternate spelling of the unrelated **Signal** field below), security wave (not every Guardrails node is security-flavored — `phpmd`/`coverage-floor` feed Understandability/Testability, not Security)

**Fulfilment check**:
A node's own test for whether it's already adopted — now agent-judged for every node. An agent walking the tree during its **Track**'s scan recognizes any real, working tool that serves the node's stated Purpose rather than matching a fixed list of names (a Laravel-Pint-configured target satisfies `php-cs-fixer`'s Fulfilment check the same as a directly-configured one). Lives in the node's own tree-doc entry, alongside its **MR scope** (what an adoption's merge request actually delivers) — every node carries both, together they're what "a node" (above) means operationally. Run during a Track's scan, and again right before the node's ticket is worked (**Fulfilled at pick-up**, below).
_Avoid_: adoption check, acceptance criteria

**Entry point**:
A PHP file the runtime (webserver or CLI) executes directly — never `require`d or `include`d by another file in the target's own source tree. `psr-4`'s autoloader-wiring step (that node's own doc in the PHP tree) targets every entry point directly when the target has no single **Composition root**.
_Avoid_: front controller

**Composition root**:
The one file, if any, the target's own **Entry point**s mostly delegate to for wiring the application together — the single place a target's own manual class-loading historically accumulates. Not every target has one, and recognizing one doesn't require unanimous delegation: an entry point that doesn't delegate to it still gets wired directly, on top of the root rather than in place of it. The kind of gap `psr-4`'s wiring step exists to close lives exactly here: a class missing from this one file's own manual require list, invisible to every autoloader-based test.
_Avoid_: bootstrap file (a file literally named `bootstrap.php` isn't necessarily filling this role), application root

**Housekeeping ticket**:
The one standing, open **ticket** per **Housekeeping template** that a **Housekeeping** run works: the template's recurring tasks, plus the refactoring ideas left on it as comments. It states from when it is due; its last task creates the next one, so the cycle carries itself. A comment is carried out in one or more commits of its own; one too big for Housekeeping is proposed for a ticket of its own. Any agent that notices a refactoring idea during other work proposes it as a comment here, after the human allowed it — with two open, the human chooses, the younger recommended.
_Avoid_: housekeeping issue (dated, one per due cycle — the earlier shape), chore ticket

**Housekeeping template**:
The file in the target a **Housekeeping ticket** is made from: the recurring tasks, the rhythm, and as its last item "create the next Housekeeping ticket". Where it lives and how the next ticket is made from it are the target's, written as the **Housekeeping** operation. Shared and committed like code. The rhythm is chosen by the human when Housekeeping is first set up, with a recommendation drawn from the target; several templates with different rhythms may exist side by side, each with its own open ticket. **Tooling tree** nodes contribute their Housekeeping line to it.
_Avoid_: checklist file, cadence (the rhythm is a line of the template, not a setting of the suite)

**Housekeeping** (recurring maintenance):
A periodic maintenance sweep — dependency currency, tooling-deprecation cleanup, documentation sync, the secret scan over the Git history (the whole history the first time, afterwards the commits since the last **Housekeeping ticket**). Also names the **Track** (above) that runs it, by working the open **Housekeeping ticket**; `/continuous-housekeeping` runs that Track alone, with no Track choice, so it can be scheduled. Where the mechanism is missing, the Track proposes to set it up: the **Housekeeping template**, the first ticket, the `AGENTS.md` line. Never a tooling-tree node: nothing about it is a one-time adoption with a stable Fulfilment check.
_Avoid_: maintenance loop, chore loop, cleanup pass

**Required edge**:
The gating edge between nodes: a node's ticket is workable only once every parent linked by a required edge is fulfilled. Rejecting a required parent is a **decision point** whose recommendation is to close every ticket beneath it as rejected.
_Avoid_: hard edge, blocking edge

**Recommended edge**:
The counterpart that gates on a decision rather than on fulfilment (ADR-0016): a node's ticket is workable only once every parent linked by a recommended edge is _decided_ — fulfilled, or rejected. A parent counts as rejected either directly (its own recorded rejection) or transitively, when one of *its own* required ancestors is itself rejected — the same closure a required edge already causes (see **Required edge** above), just extended here to answer "decided" too. A rejected recommended parent (either way) releases the child instead of closing it, unlike a required parent: at the **decision point** that follows the rejection, the recommendation is to remove the blocker from the child's ticket. The rejected parent is never offered again, unless its rejection is reversed. A recommended parent that hasn't been reached yet at all counts as undecided too, blocking the child just the same as one whose ticket is merely open.
_Avoid_: soft edge, nice-to-have edge, non-blocking edge

**Required-any edge**:
An OR variant of the required edge (ADR-0019): a node with required-any parents is workable once _at least one_ of them is fulfilled, not all — distinct from a **choice** (below), which is about mutual exclusion between siblings, not about unlocking a downstream child from either side. Combines with a node's ordinary required parents (if any) via AND between the two edge types, OR within the required-any group itself.
_Avoid_: optional required edge, either-or edge

**Choice**:
Two or more sibling nodes under a shared required parent where adopting one makes the others rejected by design — recorded the same way any other rejection is (a closed ticket or a file, where the target's **Rejected** operation says), not a separate mechanism. The tree has no dedicated XOR primitive; a choice is just an ordinary sibling pair plus the convention that picking one means rejecting the rest.
_Avoid_: XOR, either-or

**Recognition-only gate node**:
A tooling-tree node that never gets a ticket itself — it exists only as a required parent whose fulfilment gates other nodes. It is recognized (judged fulfilled or not by an agent, and handed to the parser like any other node's state) but never adopted through a run's design and implementation. Its fulfilment is a prerequisite for downstream nodes, not work the suite performs. Example: `is-php-project`, which holds the PHP tree closed until the target uses PHP. A node waiting behind an unfulfilled one is out of reach: no ticket could unblock it, so a scan offers none for it.
_Avoid_: gate node (too broad — a gate node that also gets a ticket is just a normal node)

**Aggregation node**:
A tooling-tree node others reach through `resolved` edges: `structural-scan`, and one per language specialization (PHP: `php-safety-net`). Its state is computed by the tree's parser from its leaves — fulfilled once every leaf is fulfilled, rejected, or closed by a rejected required parent — never handed in, never judged by an agent, and never a ticket. "Is **Safety Net** fulfilled?" is the computed state of `structural-scan`: it alone decides whether an autonomous run stops at Safety Net and whether a run moves on to the next **Track**. Whether every Safety Net node is done is a different question, and decides neither.
_Avoid_: resolved gate, plumbing node

**Floor correction**:
Bringing `composer.json`'s declared PHP floor (`require.php`) in line with what the codebase's own source already demonstrably requires — behavior-preserving, since nothing observable changes, only the metadata now tells the truth. The only node that produces this: `php-minimal-version` (the PHP tree), triggered once `rector-php-set` has fully applied a PHP-version rule set.
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
Any change to a target's observable behavior — never shipped under the refactor label; routes to the normal feature/bug path instead (`docs/adr/0004-foundational-refactoring-rules.md`). The suite's refactors are always behavior-preserving by definition; a **Floor raise** (above) is the canonical example of something that looks like tooling-tree housekeeping but is actually this.
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
The concrete refactoring plan a **run**'s design point ends with — produced by the target's own planning skill where it has one, else by the suite's fallback: the deepened module, its seam, the interface, and the surviving tests — written on the candidate's ticket so the refactor is delegable.
_Avoid_: design doc

**Proposals**:
What a scan lays out at the file-tickets **decision point**: one ticket for every tooling-tree node of the scanned **Track** that is neither fulfilled nor rejected, blocked ones included and marked as blocked — and, for an **Investigation** run with no open tickets, everything its exploration found, in order of **signal**, with the three strongest recommended for filing. What is not filed is not stored.
_Avoid_: suggestions, recommendations (a recommendation is the one option a decision point favours)

**Signal**:
The named factor (heat, leverage, security, blast radius of inaction, …) that qualified a candidate as a genuine friction spot. The full catalogue lives in the suite's signals reference; Within Investigation the order of tickets follows the signals, a ticket marked as priority first. Two distinct places carry this name: (1) the third field on a structural candidate's ticket, alongside Where and Problem, named when the suite files it; (2) a node-level **Signal** field on a **tooling tree** node (see that entry above) — once a Signal-producing node like `phpmd` or `secret-detection` is adopted, its own real tool output is what the search for structural candidates reads for that factor, in place of the generic (reading-the-code) recognition method a ticket's own Signal field would otherwise rely on. A tooling-tree node's Signal field never gates `structural-scan`; it only ever strengthens candidate selection.
_Avoid_: (none — use the term as-is)

**Findings**:
What a **decision point** lays out before its options. At reconcile, the first one of a **run**: which of the suite's merge requests were merged or closed, with what follows for each — close the ticket, record a rejection, ask — and any rejection whose stated blocker is now met, offered for reversal. Later ones: a **Fulfilled at pick-up** discovery (below), a secret the history scan turned up, or the discovery at the design point that a candidate can't be done without changing behavior — which ends as a decision point, not as a silent stop. Whatever found it may act on it, through that decision point.
_Avoid_: events, notifications

**Fulfilled at pick-up**:
The finding when a node's **Fulfilment check**, run again right before its ticket is worked, finds the node already served — typically adopted by hand since the ticket was filed. The ticket is closed with a note, with no merge request, and selection moves on.
_Avoid_: (none — use the term as-is)

**Flagged candidate**:
A candidate whose **plan** is already written, but whose design also surfaced a decision meeting
the ADR bar (hard to reverse, surprising without context, a real trade-off) while staying
behavior-preserving — distinct from a **Finding**'s breaking-change case, which never gets a plan at
all. In an interactive run the human answers at the design point. An autonomous run does not guess:
it leaves a proposed default plus an explicit open question on the ticket and ends with a message
naming that question; `ready-for-agent` (`docs/agents/triage-labels.md`) is actively removed if the
ticket already carried one, and `needs-info` is added in its place — the visible "waiting on you"
signal — until a human confirms or overrides it. A plain confirming comment is enough on its own —
the suite self-confirms it, swapping the labels itself (ADR-0066); anything else (a stated
alternative, a further question) still needs the human to swap the labels by hand once satisfied.
A still-waiting one (`needs-info` present, no newer human comment) is not workable — it doesn't
block the rest of the worklist — and becomes workable the moment `ready-for-agent` appears, whether
a human set it or the self-confirmation above did.
_Avoid_: blocked candidate, paused candidate

**Decision trail**:
A bundled comment posted on the ticket once grilling at the design point settles (structural
candidates and tickets a human wrote only), naming every question that met the ADR bar and the answer
reached live with the human — distinct from a **Flagged candidate**'s open question, which is
unresolved and blocks `ready-for-agent`. Purely a record; it never blocks anything. No qualifying
question in that run → no comment.
_Avoid_: grilling log, design notes
