# Reference: Refactoring operations

The suite reaches a target's issue tracker through **operations**, never through the tracker's name. They
live in the target's **tracker file**, in a section `## Refactoring operations`: one bullet
per operation, a fixed bold name followed by prose in that file's own language and with that tracker's own
commands. The rest of the file (creating, reading, commenting on and closing a ticket) stays as its author
wrote it, and a step that needs one of those follows the file. Where the section says where the suite's
tickets live, the section wins for those tickets — the case of a target that tracks its work elsewhere and
keeps refactoring tickets as local files.

A target is onboarded when its tracker file has the section. The onboarding interview writes the section,
and completes one that lacks a required operation — **Search**, in a section written before this cut
(`onboarding-setup-interview.md`).

## The tracker file

The file that says how an agent reaches the tracker and holds the section. It is, in this order:

1. the file the target's `AGENTS.md` names for the issue tracker, in its own words;
2. where `AGENTS.md` names none, the file `CLAUDE.md` names;
3. where neither does, `docs/agents/issue-tracker.md`.

What follows from a name in `AGENTS.md` or `CLAUDE.md`:

- **The two name different files** → `AGENTS.md` wins. The contradiction is a finding at the Ready step, and
  the run goes on.
- **The named file and the default file both exist** → the named one is the tracker file; the default file
  goes unmentioned.
- **The named file does not exist** → it is still the tracker file: the onboarding interview writes the section
  there.
- **The name leaves the repository** — a URL, a path outside it → the run ends, naming it. The default is no
  fallback here: it would write a second description while the human takes the other one for the source.

Paths in the section (**BC promise**, **Tooling Pack**, **Housekeeping**) stay relative to the repository
root, not to the tracker file. The parser takes the path as an argument (`tooling-parser.md`). The suite
writes no such name into `AGENTS.md`; a human who wants the file elsewhere does.

## Required operations

| Operation | What the bullet states |
| --- | --- |
| **Search** | How tickets are searched by words in title and text, open and closed together, and how the result is narrowed to the open ones |
| **Done** | How a finished ticket is recognised, and how one is marked finished |
| **Merge requests** | Where merge requests live and which tool reaches them |

**Merge requests** names the **forge**, read from the Git remote; it may be a different system than the
tracker. Its three shapes:

- `origin` on `github.com` → `pull requests on this GitHub repository, via gh pr`
- `origin` on `gitlab.com` → `merge requests on this GitLab project, via glab mr`
- another host → what the human names; no `origin` → `none — the prepared branch is handed to the human`

## Optional operations

An absent bullet means the tracker lacks the capability, and the suite takes the fallback in the last
column — except **BC promise**, which is not about the tracker: absent, the question is not settled yet.

| Operation | What the bullet states | Without it |
| --- | --- | --- |
| **Candidate** | How a ticket is marked as refactoring work, and how the open ones so marked are listed — a hint that narrows **Search** | A ticket is recognised by its subject alone; one a human wrote freely is worked only when the call names it |
| **Priority** | How a ticket is marked to come first, and how those are listed — a hint for the order | The order is the Track's own; no ticket comes first |
| **Linked merge request** | How a merge request refers to its ticket, and how to get from a ticket to its merge request | The merge request names its ticket in plain words and is found by searching the forge's merge requests for it |
| **Claim** | How a ticket is assigned to whoever works on it | Nothing is assigned |
| **Ready after plan** | How a ticket is marked ready for implementation once the suite has posted its plan, in the tracker's own commands; the command can run again without harm | Nothing is written |
| **Rejected** | How a rejection is recorded with its reason and found again: a closed ticket or a file, and where | At the decision point that records the first rejection the suite proposes a place, and writes the bullet from the answer |
| **Blocked by** | How a ticket states which tickets block it, and when it counts as unblocked | The suite writes the dependency as a sentence in the ticket's text and reads it there |
| **Housekeeping** | Where the **Housekeeping template** lives and how the next **Housekeeping ticket** is made from it | Housekeeping's mechanism counts as missing: the Housekeeping Track proposes to set it up and writes the bullet |
| **BC promise** | Where the project's **BC promise** is written down — a path in the repository or an `https://` URL — or `none` when no code outside the repository relies on this one's; or a list of parts, each with its scope (*Reading the BC promise*, below). The suite reads the document; it models no promise of its own | Not settled yet: code outside the repository could reach counts as covered (`principles.md`, *Strangler Fig*). The Tool `bc-promise`, on request or through its Opener, settles it (`packs/generic/bc-promise.md`) |
| **Tooling Pack** | The directory in the target that holds its own **Pack**: a `pack.json` and, where the Pack adds Roles, a `roles.json`, with the Tool files beside them. Recommended place: a folder `tooling-pack` beside the tracker file | The target has no Pack of its own; only the tools of the suite's Packs are proposed |

### Reading the BC promise

- **One target or a list.** The bullet names one target — a path, an `https://` URL, or `none` — or a list of
  parts, each `<scope>: <target>`. A scope is an area of the code (a path such as `packages/client/`) or a surface
  the code serves (PHP API, HTTP API, CLI, …).
- **The part that applies** is the one whose scope covers the code a change touches. Where scopes overlap, the
  stricter part applies: the one that allows less of the change. Code no part covers is not settled: it counts as
  covered. A `none` without a scope holds for the whole repository; a part `none` only for its scope.
- **A URL** is read where the promise is needed. One that cannot be read in this run leaves its part not settled
  for this run; the plan's `Decisions` and the closing report name the URL.
- **One release line.** The promise is that of the release line the default branch is on; other maintained
  branches and their promises are not the suite's.

## Templates

The template for each tracker, and the bullets a target chooses, are in `tracker-file-templates.md`: read it
to write or complete the section.
