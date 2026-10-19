# Playbook: The Tracks

The playbook for humans. The skills do the work; this document explains how a run decides *which kind* of work it does, and how you steer that decision.

## What a Track is

A **Track** is one of four kinds of work a run can spend itself on. Each run works one ticket of one Track.

| Track | Purpose | Its tickets |
|---|---|---|
| **Safety Net** | Set up the deterministic tooling (test runner, coding standards, static analysis, CI) that catches a regression *before* structural work starts | one per tool still to set up |
| **Guardrails** | Set up further quality and security tooling once the Safety Net is in place (dependency audit, coverage floor, mess detection, …) | one per tool still to set up |
| **Housekeeping** | Recurring maintenance, and the small refactoring ideas noted along the way ([playbook](housekeeping.md)) | one standing ticket per template |
| **Investigation** | Structural refactoring — a hot spot, a module worth deepening | the tickets the suite filed after exploring, and tickets you wrote |

Safety Net and Guardrails walk the [tooling tree](../../skills/continuous-refactoring/references/tooling-model.md): each adoption step is a *Stage* — one tool, up to a stated degree; each PHPStan level is a Stage of its own. A tool plays a *Role* (static analysis, code style, testing, …), and tools come in *Packs* that apply to a project: every project, a project with PHP code, and a [Pack of your own](own-tool.md).

At the start of a run the suite searches your open tickets and sorts them: a ticket about a tool of the tree belongs to that tool's Track, the open Housekeeping ticket to Housekeeping, everything else to Investigation. Each ticket also gets a state:

- **workable** — open, and everything that blocks it is done;
- **in review** — it has an open merge request;
- **blocked** — it names a blocker that is not done;
- **waiting** — its newest comment is an open question for you.

## How a Track is chosen

Track choice is a decision point. The recommendation is the first Track, in the fixed order **Safety Net, Guardrails, Housekeeping, Investigation**, that has something:

| Track | It has something when |
|---|---|
| Safety Net, Guardrails | one of its tickets is workable — or a tool of it was never looked at, which makes its scan due |
| Housekeeping | its open ticket states a due date that is reached and is not in review — or its mechanism is not set up yet |
| Investigation | always: with open tickets it works them, without it explores |

**Safety Net comes first while it is unfinished.** When Safety Net has nothing workable, the suite reads whether it is *fulfilled*. That answer is computed from the tree, not judged: every tool that structural work depends on is in place or declined.

- fulfilled → the recommendation moves on down the order;
- not fulfilled → the recommendation is to end the run. An autonomous run ends here with "Safety Net is waiting for merges", followed by what is in review and what cannot be worked and why. In an interactive run you may choose another Track instead.

Once Safety Net is fulfilled, a Track that turns out to have nothing workable is skipped within the same run, and the next one in the order is tried. A call therefore does not end empty while another Track has work.

## Naming a Track yourself

Name the Track in the call — "work on Guardrails", "Investigation" — and the choice is answered: the run works that Track whatever the order would recommend, Safety Net's precedence included. Such a run stays there. When the named Track has nothing workable it ends and does not move on.

The same holds for a ticket you name: the run works that ticket, and ends if it turns out not to need work.

## When a Track is scanned

A tooling Track is scanned when your tracker shows **no trace** of one of its tools yet — no ticket about it, open or closed, and no recorded rejection of it, of the tool as a whole, or of the role it plays. In a scan each tool is judged against your project: is something real and working in place that serves the tool's purpose, under any name? A project running Laravel Pint has automated code style, so PHP CS Fixer counts as in place.

Then the suite offers a ticket for **every** tool that is neither in place nor declined — the blocked ones too, marked as blocked. The whole way ahead is visible in your tracker after one scan. At that decision point you file all, some or none, or decline a tool for good — one step of it, the whole tool, or the role it plays, which closes the rest of the tools of that role too.

After that, the tickets are the record:

- A tool without an open ticket counts as done. Nothing is judged again on an ordinary run — except a tool the suite learned about since, which makes the next run scan the Track for it.
- A proposal you neither filed nor declined is stored nowhere. Its tool counts as done until a later scan offers it again.
- A scan runs again when you ask for one in the call, and as a recurring Housekeeping task that re-checks both tooling Tracks — that is how a tool that went missing, or a tool the tree gained, is noticed.

Some tools can get no ticket at the moment: one that needs a newer PHP than your project allows, or one that waits behind a condition no ticket can change (a PHP tool on a project that is not PHP). The scan names them as out of reach, with the reason. For a tool below your PHP version it recommends recording a rejection that states the PHP version needed; once your project reaches it, a later run offers to reverse that rejection.

## How a ticket is selected

- **Safety Net and Guardrails** follow the tree's order. A ticket you marked as priority comes first.
- **Investigation** follows the signals: security first, then problems that get worse the longer they wait, then whatever is hot, widely used, flagged by your tools and low in risk. A ticket you marked as priority comes first here too.

Right before a tooling ticket is worked, its tool is judged once more. If you set it up by hand since the ticket was filed, the ticket is closed with a note saying what serves it now, and selection moves on to the next. An Investigation ticket gets the same kind of check: does the module it names still exist, is the friction still there?

### A tooling ticket that is too big for one merge request

A tool's change can touch so many files that nobody could review it as one. The plan then estimates the size, cuts the work into parts where the kind or the risk of the change differs — rewrites that only restate the code apart from rules that change what it does — and names in a sentence why the cut is there. Each part is a merge request of its own that is worth merging without the others. The ticket stays open until the last part is merged. Work the tool does not need for its goal can become a ticket of its own, which the run proposes to you first.

### A PHPStan baseline

A PHPStan level whose baseline still holds findings does not block the suite silently. The scan proposes one ticket, "PHPStan Level N: shrink the baseline", and the next level's ticket is blocked by it. That ticket takes one merge request after another, each removing one group of findings at their cause, and closes with the one that empties the baseline. A merge request may add a new baseline entry when the baseline still gets shorter overall, and names it. A finding that should stay ignored, or a baseline that would not get shorter, becomes an ignore rule in `phpstan.neon` — only once you have allowed it.

### PHPMD's limits

PHPMD does not get a baseline. Its metric rules (complexity, length, coupling) have limits, and when the tool is adopted each limit is set to the worst value the code has today, with a comment that names that value and where it is. The limits only ever fall: a merge request that rewrites the method which sets the worst value measures again, lowers the limit and updates the comment, and PHPMD stays green. The Housekeeping ticket lowers a limit the code has already come under. Deliberate exceptions are written at the code with a reason, never into a baseline. A project that already has a baseline gets one merge request that moves its entries into limits and suppressions and deletes the file.

A rule that would report too much to be taken in at once is not given up. The first merge request leaves it out, marked as not taken in yet with the number of its findings, and the suite proposes one ticket, "PHPMD: take in the remaining rules", worked one rule per merge request, the rule with the fewest findings first. Only you decide that a rule is declined for good.

## Investigation without tickets

With no open Investigation ticket, the run explores the code: your focus areas first, else the places the Git history shows changing again and again. Everything it finds is shown to you in order of signal. The recommendation is to file the **three strongest** — you may file others, as many as you want, or none. What is not filed is not stored; a later exploration may come upon it again. An autonomous run files those three and goes on to work the strongest.

When Investigation has open tickets but none is workable — all in review or waiting — the recommendation is to go back to Track choice instead of exploring for more, so that repeated autonomous calls do not pile up new candidates behind unreviewed ones.

## Declining a tool

Declining records a **rejection**: a closed ticket or a file with your reason, in the place your tracker section names. The first time, the suite proposes a place and writes your answer into that section. A declined tool is not proposed again.

Tickets that depended on a declined tool are a decision point of their own. Where the dependence is strict, the recommendation is to close them too; where the declined tool was only recommended first, the recommendation is to remove the blocker and keep the ticket.

## Common mistakes

- **Expecting Guardrails or structural work from an autonomous run before the Safety Net is done.** The stop is intentional. Merge what is in review, or name the Track you want.
- **Naming a Track and expecting the run to move on.** A named Track is the whole run.
- **Reading "blocked" as a failure.** The ticket waits for another ticket; the report names which.
- **Leaving a proposal unfiled and expecting it to come back next run.** It comes back with the next scan, not before.
