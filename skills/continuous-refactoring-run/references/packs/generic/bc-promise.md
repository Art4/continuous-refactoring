# BC promise

The Tool for the Role Compatibility Policy in the generic Pack, proposed only on request or through its Opener:
the project's own document of what it promises code outside the repository (`../../refactoring-operations.md`,
**BC promise**). Not a runnable tool: a document, and the bullet that points to it. Language-neutral, so it is in
the generic Pack.

**Why this order.** A Safety Net Stage that requires nothing and waits for nothing: what the promise covers decides
how the suite's own structural work may change code (`../../principles.md`, *Strangler Fig*). It holds nothing
back while it is open: until it is settled, whatever code outside the repository could reach counts as covered.

### `bc-promise`

- **Purpose:** the promise is written down and recorded, so that a run knows which code it may delete or reshape
  and which it may only deprecate.
- **Fulfilment check:** the target's `## Refactoring operations` section has a **BC promise** bullet: a path that
  exists in the repository, or `none`. A document without the bullet does not count.
- **Opener:** a plan that takes the careful way only because the bullet is missing: Strangler Fig, with the old path
  kept beside the new, where *Migrate callers, then delete* would apply if no code outside the repository relied on
  this one's. Its question asks more than "Set up BC promise?": the scan works out the proposal (*MR scope*,
  below) and the question holds what *Finding the BC promise* found and the draft in full or the bullet the merge
  request would hold, and asks whether to record it so. One answer settles both.
- **MR scope:** the bullet, placed after the last bullet of the section, the rest of the file unchanged, plus what
  *Finding the BC promise* led to:
  - **one document found** → the bullet only; the description names which of the questions below the document
    leaves open;
  - **evidence that no code outside the repository relies on this one's** — a `project` type, no published
    package, no plugin, hook or event API → the bullet `none`, the evidence in the description;
  - **otherwise** → a draft named `bc-promise.md` in the `docs` folder, or `BC-PROMISE.md` at the root where
    there is none; a docs convention the project has (a folder for its website, say) wins. The draft speaks to the users of the
    project's code, not to its contributors. It answers each question below from evidence in the repository,
    names the evidence beside each answer, and leaves each question without evidence as an open question for the
    human. What the code shows is written as what the project has done so far; only the human's answer makes it
    a promise. A question still without an answer when the document is recorded stays in it as not settled,
    never as a promise.
- **Autonomous run:** a merge request only for what a human answered on the ticket. Where the ticket carries no
  answered proposal yet — it was asked for in the call, not filed through the Opener — the plan posts the proposal
  as an open question (`../../design-point.md`, *Open questions*), and the run ends with it named. An answer that
  confirms the proposal, or names what to change, is planned from as it stands; the merge request holds what the
  human answered, and its review is an ordinary one.
- **Rejection:** the careful default stays for good, and no Opener proposes the Tool again.

#### Finding the BC promise

Read-only. Look for a document in which the project promises code outside the repository — the users of its
package, the addons of its application — which parts stay stable and how a breaking change is allowed: `AGENTS.md`,
`CLAUDE.md`, `CONTRIBUTING*`, `README*`, `UPGRADE*` and `docs/`, for words such as backward compatibility, BC
promise, deprecation policy or semantic versioning. A pointer in `AGENTS.md` to such a document counts as finding
it. A sentence that only names SemVer for the version numbers is no promise. The result is **one document**,
**several** (the proposal names each, with a line from it, and asks which), or **none found**.

#### The questions a draft answers

Written promises of large projects answer the same questions; no standard prescribes the form. Read the evidence
named for each; where there is none, the question stays open.

| # | Question | Evidence in the repository |
|---|---|---|
| 1 | Is there code outside the repository that relies on this one's, and whose: users of a package, authors of addons, clients of an API? | `composer.json` `type` and `name`, a published package, install instructions in the README, plugin, hook or event APIs |
| 2 | Which versioning scheme, and what does each part mean? | tags, changelog headings, branch aliases; a history in `0.x` only |
| 3 | What is covered? | visibility, `@api`, the namespaces the autoload section exports, API docs configuration |
| 4 | What is left out explicitly? | `@internal`, `@psalm-internal`, `@no-named-arguments`, `Internal` namespaces or folders, test namespaces |
| 5 | What may a user rely on when calling, extending, implementing? | the share of `final` classes and methods, `@final`, abstract classes and interfaces documented as extension points |
| 6 | Which changes may each kind of release hold? | the changelog's history of breaks, a configured backward-compatibility check |
| 7 | How is something deprecated, and how is it marked? | `@deprecated` texts and their form, `trigger_deprecation`, `E_USER_DEPRECATED`, `#[\Deprecated]`, a deprecation package in `require` |
| 8 | How long does a deprecated part survive at least? | the gap between deprecation and removal in the changelog or upgrade notes; usually the human's |
| 9 | How are experimental parts handled? | `@experimental`, `@beta`, `Experimental` namespaces, feature flags |
| 10 | Which exceptions override the promise (security, bugs)? | `SECURITY.md`; usually the human's |
| 11 | Which versions are supported, and for how long? | maintained branches, a support table, a supported-versions list in `SECURITY.md`; usually the human's |
| 12 | Where are deprecations and breaks announced, and how does a user upgrade? | `CHANGELOG*`, `UPGRADE*`, `DEPRECATIONS*`, release notes |
| 13 | Which surfaces besides code are covered: console commands, configuration, HTTP API, hooks, schema, templates? | `bin/` commands, configuration schemas, an OpenAPI file, the event names it dispatches, migrations |
| 14 | How is the promise checked? | a backward-compatibility check in CI and its configuration |
