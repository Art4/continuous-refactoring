# Continuous Refactoring

The vocabulary of a portable agent-skill suite that keeps a software project under continuous refactoring — repeated runs that find, plan, execute and verify structural improvements, with all state kept in the project's issue tracker and forge.

## Language

**Candidate**:
A **ticket** the suite works as refactoring: the adoption of a **tooling tree** Stage, a structural deepening, or a ticket a human wrote. Recognised by its subject, named in plain words in title and text — never by a fixed marker. A ticket a human wrote is picked up when the target's **Candidate** operation says how such tickets are marked, or when the call names it.
_Avoid_: todo

**Backlog**:
The ordered list of a **Track**'s tooling-tree Stages that are neither fulfilled nor closed by a rejection, blocked ones included — what the tree's parser emits and what a scan offers tickets for. Once the tickets exist, the **Worklist** is what a run works from.
_Avoid_: debt list, todo list

**Run**:
One call of the suite, from its first **decision point** to its end: reconcile → **Track** choice → scan (only when the Track needs one) → file tickets → select → design → implement → **merge request**. A run ends when the merge request is open, when the design cannot proceed without a human answer or finds that the ticket would change behavior, or when nothing is workable; more work is another call, not a longer run. Nothing limits how many merge requests or candidates are open at once. The call takes free text the suite interprets — a Track, a restriction ("only the Rector Stages"), a ticket, the mode. Text addressed to the human says "run" and "skill suite".
_Avoid_: loop pass, session, sprint

**Decision point**:
One link of a **run**'s chain: the suite lays out what it found, the options, and one recommendation. Who decides is the run's mode (**Interactive / Autonomous**). Everything the suite writes to a tracker or a forge follows from a decision point.
_Avoid_: checkpoint, approval step

**Interactive** / **Autonomous**:
The two modes of a **run**. **Interactive**, the default: the human decides at every **decision point**. **Autonomous**: the suite takes its own recommendation at every one — the same chain, not a second path. Autonomous is said in the call, in free words, or mid-run ("carry on yourself from here"); it is never stored. Without that hint and with nobody answering, the run ends at the first decision point with a report and has written nothing. One write needs a human even in an autonomous run: changing the target's `AGENTS.md`.
_Avoid_: ask-each-time, human-opens, create-mode (settings that no longer exist)

**Driver**:
An agent that calls **runs** one after another on the human's behalf, each in a subagent of its own and always **autonomous**, and reviews each **merge request** — merging it, asking for changes, or asking the human — before the next call. It passes on the human's Track or restriction, and names a ticket to go on with one — reworking its merge request, its next part, a question the human answered, or the human's wish — never one that waits or is blocked. It calls the next run until a run finds nothing workable, or until an end the human set. The runs stay separate calls: the Driver keeps no state the tracker does not hold, and it never answers an open question itself.
_Avoid_: orchestrator, loop, run loop

**Worklist**:
The open **tickets** of a target, found by searching the tracker and sorted into **Tracks**: a ticket matching a tooling-tree Stage belongs to that Stage's Track, the open **Housekeeping ticket** to Housekeeping, everything else to Investigation. A ticket is _workable_ when it is open and its blockers are all done. A call that names a ticket narrows the worklist to that ticket, and reconcile with it. The suite keeps no list of its own: a ticket's merge request, a rejection and the Housekeeping ticket are found by search each time.
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
The named operations the suite needs from an **issue tracker**, one bullet each in that file's `## Refactoring operations` section. Required: **Search** (how tickets are searched, open and closed), **Done**, **Merge requests**. Optional: **Candidate** and **Priority** (hints for search and order), **Linked merge request**, **Claim**, **Ready after plan** (how a ticket is marked ready for implementation after the suite posts its plan), **Rejected** (how a rejection is recorded and found again — a closed ticket or a file, and where), **Blocked by** (how a ticket states what blocks it), **Housekeeping** (where the **Housekeeping template** lives and how the next **Housekeeping ticket** is made from it), **BC promise** (where the project's **BC promise** is written down, or `none`). A missing optional operation means the capability is absent and the suite takes its fallback — except **BC promise**, whose absence means the question is not settled yet: without **Blocked by** the dependency is a sentence in the ticket, without **Rejected** the suite proposes a place when the first rejection is recorded (`skills/continuous-refactoring/references/refactoring-operations.md`).

**Ticket**:
An issue on the project's tracker — the word the suite uses, in its own texts and towards the human, because it is the wording of the engineering skills the suite builds on. Not a synonym for **Candidate**: a candidate is a ticket the suite works as refactoring, not every ticket is one. A ticket the suite files names its subject in plain words in title and text (the tool's name), so a later search finds it; before filing, the suite searches for an existing ticket on the subject, open or closed.
_Avoid_: todo

**Tooling tree**:
What a target repo climbs, described as **Roles** filled by **Tools** that have **Stages**, delivered in **Packs** (below; the rules are in the suite's tooling-model reference). A **Stage** is one degree of a Tool, up to which a tool is adopted, and the unit a ticket is filed for (each PHPStan level is its own Stage). Each Stage and each Tool carries a human-facing **Name**, used instead of the slug anywhere a human reads it — ticket titles, merge requests, a run's reports; the parser's input and output stay keyed by the slug. The suite's own prerequisites, `git` and `onboarding-setup`, are in no Pack. Operational lessons discovered while adopting or fulfilling a Stage are worked directly into its Purpose, Fulfilment check and MR scope prose, not tracked as a separate entry. A Tool may carry a **Housekeeping** field — a recurring-maintenance line contributed to the **Housekeeping template** (below), ordinarily through the Stage's own merge request, or added by a **Housekeeping** run for a fulfilled Tool whose line is missing; unrelated to the Stage's one-time Fulfilment check. A Role may carry a **Signal**, naming which signals-catalogue factor its tool output feeds once adopted — see the **Signal** entry below. Not every Role produces one.
_Avoid_: baseline, floor, bootstrap, onboarding (as a name for the tree itself — it never stops being walked; see the dedicated **Onboarding** entry below for the bounded phase within it, which is a real term)

**Track**:
One of four kinds of work a **run** can spend itself on: **Safety Net**, **Guardrails**, **Housekeeping**, **Investigation** (all below). Track choice is a **decision point**: the suite sorts the **worklist** into Tracks and recommends the first one, in that fixed order, with something workable. While Safety Net is not fulfilled, an autonomous run that finds nothing workable there ends with "Safety Net is waiting for merges"; a human may choose another Track. Once Safety Net is fulfilled, a Track with nothing workable is skipped within the same run. Housekeeping is recommended when its open **Housekeeping ticket**'s due date is reached, or when its mechanism is missing. A Track is scanned only when a Stage of it is not known yet — no ticket of it, open or closed, and no recorded rejection of it, of its Tool or of its Role; a Stage of an *on request* **Tool** never counts as not known — or on request; a known Stage without an open ticket counts as done, and re-checking the tooling Tracks is a recurring **Housekeeping** task. A Track is a phase or function of work, never a topic: topics are **Signals**. A human names a Track in the call to work on it whatever the recommendation would be.
_Avoid_: wave (this concept's earlier name; retired once it started colliding with **Guardrails**' own former name, "Signal wave" — see that entry)

**Onboarding**:
The phase of a target's own tree walk from a bare repo through `git`, `onboarding-setup` and every Stage in the **Safety Net** (below) — everything before the Safety Net is fulfilled. Bounded and, per target, effectively one-time, unlike the **Tooling tree** itself (above), which is walked forever. Its first step, fulfilling the `onboarding-setup` prerequisite (Name "Onboarding Setup"), is not a scan: it is the first thing a call checks. A target whose tracker file has no `## Refactoring operations` section gets a short interview — where the tickets live and how the operations work there, nothing else — that writes the section; a section without **Search** gets it added the same way. Everything after `onboarding-setup` is simply what the Safety Net **Track**'s first scan finds — the same mechanism as any later scan, just with more to discover the first time.
_Avoid_: baseline, bootstrap (see **Tooling tree**'s own `_Avoid_` list — those describe the never-ending tree; this term names only the bounded early phase within it)

**Safety Net**:
The tooling-tree Stages whose Track is Safety Net — deterministic tooling whose findings could collide with agent-driven structural work, settled before that work starts. The Safety Net is *fulfilled* when every one of its Stages, in the Packs that apply and of the Tools in use, is fulfilled or closed by a rejection; the parser computes it. Narrower than **Onboarding** (above): every Safety Net Stage lives inside Onboarding, but `git` and `onboarding-setup` aren't Stages. Also names the **Track** (above) that works through these Stages.
_Avoid_: baseline, tooling gate

**Guardrails**:
The tooling-tree Stages whose Track is Guardrails — workable only once the **Safety Net** (above) is fulfilled. Also names the **Track** (above) that works through these Stages. Orthogonal to a Role's own **Signal** (below): one names *when* a Stage becomes workable, the other names *which factor* its tool feeds once adopted. Every Stage whose Role carries a Signal is a Guardrails Stage today.
_Avoid_: signal wave (this concept's former name — renamed for symmetry once both it and **Safety Net** became **Track** names, and to stop reading as an alternate spelling of the unrelated **Signal** field below), security wave (not every Guardrails Stage is security-flavored — `phpmd-adoption`/`coverage-floor` feed Understandability/Testability, not Security)

**Fulfilment check**:
A Stage's own test for whether it's already adopted — agent-judged for every Stage. An agent walking the tree during its **Track**'s scan recognizes any real, working tool that serves the Role's stated Purpose rather than matching a fixed list of names (a Laravel-Pint-configured target satisfies `php-cs-fixer-adoption`'s Fulfilment check the same as a directly-configured one). Lives in the Tool's `details` file, alongside the Stage's **MR scope** (what an adoption's merge request actually delivers) — every Stage carries both, together they're what "a Stage" means operationally. Run during a Track's scan, and again right before the Stage's ticket is worked (**Fulfilled at pick-up**, below).
_Avoid_: adoption check, acceptance criteria

**Entry point**:
A PHP file the runtime (webserver or CLI) executes directly — never `require`d or `include`d by another file in the target's own source tree. `psr-4`'s autoloader-wiring step (that Tool's file in the PHP Pack) targets every entry point directly when the target has no single **Composition root**.
_Avoid_: front controller

**Composition root**:
The one file, if any, the target's own **Entry point**s mostly delegate to for wiring the application together — the single place a target's own manual class-loading historically accumulates. Not every target has one, and recognizing one doesn't require unanimous delegation: an entry point that doesn't delegate to it still gets wired directly, on top of the root rather than in place of it. The kind of gap `psr-4`'s wiring step exists to close lives exactly here: a class missing from this one file's own manual require list, invisible to every autoloader-based test.
_Avoid_: bootstrap file (a file literally named `bootstrap.php` isn't necessarily filling this role), application root

**Housekeeping ticket**:
The one standing, open **ticket** per **Housekeeping template** that a **Housekeeping** run works: the template's recurring tasks, plus the refactoring ideas left on it as comments. It states from when it is due; its last task creates the next one, so the cycle carries itself. A comment is carried out in one or more commits of its own; one too big for Housekeeping is proposed for a ticket of its own. Any agent that notices a refactoring idea during other work proposes it as a comment here, after the human allowed it — with two open, the human chooses, the younger recommended.
_Avoid_: housekeeping issue (dated, one per due cycle — the earlier shape), chore ticket

**Housekeeping template**:
The file in the target a **Housekeeping ticket** is made from: the recurring tasks, the rhythm, and as its last item "create the next Housekeeping ticket". Where it lives and how the next ticket is made from it are the target's, written as the **Housekeeping** operation. Shared and committed like code. The rhythm is chosen by the human when Housekeeping is first set up, with a recommendation drawn from the target; several templates with different rhythms may exist side by side, each with its own open ticket. **Tooling tree** Tools contribute their Housekeeping line to it.
_Avoid_: checklist file, cadence (the rhythm is a line of the template, not a setting of the suite)

**Housekeeping line**:
The recurring task a **tooling tree** Tool contributes to the **Housekeeping template**: its **Housekeeping** field, reworded for the template's reader. It arrives through the Stage's own merge request; for a tool set up by hand, a Housekeeping run adds it.
_Avoid_: checklist line

**Part**:
What one merge request delivers of a **ticket** that takes several: one group of a PHPStan baseline's entries, or a Housekeeping setup without its first cycle. Its merge request names the ticket without a closing reference and says what stays; the ticket stays open and is worked again.
_Avoid_: partial fix, chunk

**Housekeeping** (recurring maintenance):
A periodic maintenance sweep — dependency currency, an audit of the dependencies for known vulnerabilities, tooling-deprecation cleanup, documentation sync, the secret scan over the Git history (the whole history the first time, afterwards the commits since the last **Housekeeping ticket**). Also names the **Track** (above) that runs it, by working the open **Housekeeping ticket**; `/continuous-housekeeping` runs that Track alone, with no Track choice, so it can be scheduled. Where the mechanism is missing, the Track proposes to set it up: the **Housekeeping template**, the first ticket, the `AGENTS.md` line. Never a Stage of the tooling tree: nothing about it is a one-time adoption with a stable Fulfilment check.
_Avoid_: maintenance loop, chore loop, cleanup pass

**Role**:
What a tool is for: Static Analysis, Code Style, Testing, Secret Scanning. A **Tool** plays one or more Roles, and a Role can be empty. A Role is *filled*, per scope, once the first **Stage** of one of its Tools is fulfilled; recommended Tools come before recognized ones, so with both present the recommended Tool is the one in use. Tools of other scopes do not compete (a Code Style Tool for PHP and one for Twig are both in use). A Role carries the **Purpose** a **Fulfilment check** is judged by and, where its tool output feeds one, a **Signal**. A rejection may name a Role ("no static analysis"), which closes every Tool that plays it.
_Avoid_: practice, capability (the tracker's operations use that word)

**Tool**:
The concrete tool a **Role** is played by — PHPStan, Psalm, PHP CS Fixer — or a convention that needs none (PSR-4 autoloading). *Recommended*: proposed when its Role is empty. *Recognized*: counted when present, never proposed (Psalm, Laravel Pint, Easy Coding Standard, PHP_CodeSniffer). *On request*: counted when present, proposed only when a human asks for it (Semgrep, Psalm Taint Analysis); its Stages make no scan due and count towards their Track only once one of them has a ticket. A Tool whose Role another Tool fills takes no place any more (it is *out*) and is not proposed. A Tool has a Name, the oldest runtime any version of it ran on, and its Housekeeping line; a rejection may name a Tool, which closes its Stages and leaves the Role open for another Tool.
_Avoid_: (none — use the term as-is)

**Stage**:
One degree of a **Tool**, and the unit a ticket is filed for: PHPStan Level 3, Rector's dead-code set. It has a slug, a Name, one **Track**, what it requires first (Stages, a **Role**, or a group of alternatives) and what it waits for until it is decided. A rejected required Stage closes it; a rejected Stage it waits for releases it. A Stage may carry an *Applies when* of its own, judged like a **Pack**'s.
_Avoid_: node (the word it replaced; only the parser's output keys `node` and `nodes` still carry it)

**Pack**:
Tools with a condition under which they apply: the generic Pack always, the PHP Pack when the target contains PHP code, a Pack of a target's own as it says. The condition is a sentence the agent judges once per run; a Pack that does not apply is absent everywhere. A Pack may name a **scope** — the language or area its Tools work on — and Tools compete for a Role only within a scope. A target's own Pack has the format of the suite's and may add Tools, Stages and Roles, never redefine the suite's.
_Avoid_: (none — use the term as-is)

**Ratchet**:
How a **Stage** is raised without letting the old findings back: no new violations, the existing ones shrink, one direction only — the PHPStan baseline, a coverage floor, PHPMD's limits. A property of a **Tool**. A level whose baseline still has entries is not fulfilled, and its ticket is the baseline's shrinking. PHPMD's ratchet is its limits: set to today's worst value when the Tool is adopted, lowered by the merge request that removes that worst value, never raised and never moved into a baseline.
_Avoid_: (none — use the term as-is)

**Floor raise**:
Committing a project to a newer PHP version than the floor it declares (`composer.json`'s `require.php`) — by raising the declared floor, or by changing the code so it needs a newer PHP than declared, as a Rector PHP-version set above the floor would. A genuine **Breaking change**, a product decision, never autonomously proposed by any Stage of the tooling tree: the suite's PHP-version rewrites stop at the declared floor.
_Avoid_: floor bump, floor correction (a rewrite above the floor followed by a matching `require.php` is a raise, not a correction), upgrade (collides with `rector-php-set`'s own "PHP-upgrade rule set" wording — syntax modernization, a different concern)

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

**BC promise**:
A project's documented commitment to code outside its repository — the users of a package, the addons of an application — about which parts of its code stay stable and by which path a **Breaking change** to them is allowed: a new major version under SemVer, or a deprecation period counted in time and releases (Friendica: `@deprecated`, then a triggered deprecation notice, then removal no sooner than five months and one release later). The promise is the project's own document; the suite reads it and models no variant of its own. A project without one has no BC promise. A Breaking change the promise allows is still a Breaking change: never shipped under the refactor label.
_Avoid_: library (an application with addons can have one, a package may have none), public API (the promise, not the visibility keyword, decides what is covered)

**Pinning Test** (a *pin*):
A test written before a structural change that holds the code's current behaviour at its **seam** and passes on the code as it stands — Feathers' characterization test; a snapshot (golden master) or an equivalence script serves too — the script runs the base commit and the branch on the target's own sample inputs and compares the outputs (back-to-back testing). A type check or a linter is none. The first commit of a structural ticket; not asked of a tooling or baseline ticket.
_Avoid_: safety test, regression test (a regression test guards a fixed defect)

**Reader load**:
The work a reader must do to follow code: the layers between a question and its answer, and the state they must hold in mind. A refactoring lowers only the part that does not come from the problem itself. A structural slice that lowers it nowhere is taken off.
_Avoid_: (none — use the term as-is)

**Principle**:
An aid to judgement in the suite's `principles.md`: it names when it applies, says what to weigh, and shows how it fails. Unlike a foundational rule it does not bind; departing from one needs its reason in the plan or the review.
_Avoid_: (none — use the term as-is)

**Seam**:
The public boundary at which a module is tested — where tests observe behaviour without reaching inside.
_Avoid_: boundary, internal hook

**Tooling pressure**:
A candidate that an already-fulfilled tooling-tree Stage keeps surfacing — things that will re-fail until fixed.
_Avoid_: lint noise, tool complaints

**Leverage**:
How much future change does deepening this module unlock? A module many others call is high-leverage; a leaf nobody calls is not.
_Avoid_: (none — use the term as-is)

**Locality**:
What moves together, and what must not spread? The degree to which related code lives in one place rather than scattered across the codebase.
_Avoid_: (none — use the term as-is)

**Plan**:
The concrete refactoring plan a **run**'s design point ends with — produced by the target's own planning skill where it has one, else by the suite's fallback: what changes and where, the slices in the order they are built, and the commands that show the work is done — for a structural candidate also the deepened module, its seam, the interface, the surviving tests, and the pin. Written on the candidate's ticket so the refactor is delegable; a plan the suite wrote is a comment opening with the word `Plan`.
_Avoid_: design doc

**Proposals**:
What a scan lays out at the file-tickets **decision point**: one ticket for every tooling-tree Stage of the scanned **Track** that is neither fulfilled nor closed by a rejection, blocked ones included and marked as blocked — and, for an **Investigation** run with no open tickets, everything its exploration found, in order of **signal**, with the three strongest recommended for filing. What is not filed is not stored.
_Avoid_: suggestions, recommendations (a recommendation is the one option a decision point favours)

**Signal**:
The named factor (heat, leverage, security, blast radius of inaction, …) that qualified a candidate as a genuine friction spot. The full catalogue lives in the suite's signals reference; Within Investigation the order of tickets follows the signals, a ticket marked as priority first. Two distinct places carry this name: (1) the third field on a structural candidate's ticket, alongside Where and Problem, named when the suite files it; (2) a **Signal** field on a **Role** of the **tooling tree** (see that entry above) — once a Tool of a Signal-carrying Role like `phpmd` or `secret-detection` is adopted, its own real tool output is what the search for structural candidates reads for that factor, in place of the generic (reading-the-code) recognition method a ticket's own Signal field would otherwise rely on. A Role's Signal never gates the Safety Net; it only ever strengthens candidate selection.
_Avoid_: (none — use the term as-is)

**Findings**:
What a **decision point** lays out before its options. At reconcile, the first one of a **run**: which of the suite's merge requests were merged or closed, with what follows for each — close the ticket, record a rejection, ask — and any rejection whose stated blocker is now met, offered for reversal. Later ones: a **Fulfilled at pick-up** discovery (below), a secret the history scan turned up, or the discovery at the design point that a candidate can't be done without changing behavior — which ends as a decision point, not as a silent stop. Whatever found it may act on it, through that decision point.
_Avoid_: events, notifications

**Fulfilled at pick-up**:
The finding when a Stage's **Fulfilment check**, run again right before its ticket is worked, finds the Stage already served — typically adopted by hand since the ticket was filed. The ticket is closed with a note, with no merge request, and selection moves on.
_Avoid_: (none — use the term as-is)

**Flagged candidate**:
A candidate whose **plan** is already written, but whose design also surfaced a decision meeting
the ADR bar (hard to reverse, surprising without context, a real trade-off) while staying
behavior-preserving — distinct from a **Finding**'s breaking-change case, which never gets a plan at
all. In an interactive run the human answers at the design point. An autonomous run does not guess:
its plan takes a default, the question is left on the ticket as a comment opening with the words
`Open question`, and the run ends with a message naming it. The ticket is _waiting_ — not workable,
and not in the way of the rest of the **worklist** — until an answer follows that comment: any newer
comment that opens with neither `Plan` nor `Open question`, whichever account wrote it. The answer ends the wait: the next run's design point reads it, and lets the plan stand, plans again with
the way it names, or asks once more. No label is set or removed for any of this, so it works in a
target without triage labels.
_Avoid_: blocked candidate, paused candidate

**Decision trail**:
The `Decisions` part of a **plan**: every question of the design that met the ADR bar, with the answer
reached — distinct from a **Flagged candidate**'s open question, which is unresolved. Purely a
record; it never blocks anything. Where the target's domain docs say ADRs are kept, each such decision
also becomes an ADR on the candidate's branch, travelling in its **merge request**. No qualifying
question → no `Decisions` part.
_Avoid_: grilling log, design notes
