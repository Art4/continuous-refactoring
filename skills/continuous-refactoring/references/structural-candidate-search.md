# Reference: the search for structural candidates

The exploration of an Investigation run: read the target's code and history, and return every genuine
friction spot as a **proposal** with a signal from `signals.md`. It only reads and judges, so it may run
in a subagent handed this file, `signals.md` and the call's restriction.

## 1. Read the project lines

The target's instruction file (`AGENTS.md`, else `CLAUDE.md`) may carry two lines a human wrote. An
absent line is unset.

```markdown
Focus areas: order intake, billing

Refactoring goal: convert legacy procedural code to OOP
```

- **`Focus areas`** says *where*: the areas to explore first.
- **`Refactoring goal`** says *what shape* the code should move towards. It is a lens for step 3:
  friction that keeps the code away from that shape is evidence for the signal it falls under. With a
  goal that names OOP, global mutable state and coupling through includes weigh heavily.

*Done when* both lines are noted as set, with their wording, or unset.

## 2. Decide where to look

The first that applies:

1. **The call's restriction names a place** — a module, a subsystem → look there, and only there.
2. **`Focus areas` is set** → those areas first, then the hot spots of the next row.
3. **Otherwise** → read the last few hundred entries of `git log --oneline --name-only` for **hot
   spots**, the files and areas that keep coming up, and take the ten that come up most. Where none
   stands out, take the top-level source directories instead.

*Done when* the places are listed in the order they will be read.

## 3. Explore

Read each place and check it against every signal of `signals.md`, structural and consequence. Where a
signal names a tool the target has set up, take that tool's result as the evidence: its existing report,
or a run of it in a mode that leaves the target's files as they are (a dry run, output to a temporary
directory outside the target).

A place qualifies by itself: it has a signal, and evidence for it you can point to. The bar is the same
for the first proposal and for the tenth. PHPStan baseline entries belong to the baseline ticket of their
level; leave them to it.

Describe each proposal in the words of module design — module, interface, depth, seam, leverage,
locality — and in the target's own names for its code.

*Done when* every place of step 2 was read against every signal.

## 4. Return the proposals

One entry per proposal, in the order and with the reason `signals.md` asks for under *Order of signal*:

- **Where** — the module and its files.
- **Problem** — the friction, in the project's domain language, in two or three sentences.
- **Signal** — the one that qualified it, and the evidence: a file and line, a count, a tool's finding.

Also return the places read. No place qualified → say so.

The search is done when every qualifying place is one entry and the entries are in order.
