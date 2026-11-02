# The BC promise is a Tool on request, proposed through an Opener

> Amends [ADR-0088](0088-the-bc-promise.md): the BC promise is no longer settled in onboarding and in the first step
> of every run; a Tool on request settles it. Amends [ADR-0086](0086-tools-on-request.md): a Tool on request may also
> be proposed, as a question, once an Opener was seen.

ADR-0088 asks for the BC promise in the onboarding interview, and again in the first step of every run while the
bullet is missing. For a new project the question comes early and without context. An autonomous run that finds no
single document asks it again on every run, and the Driver does not show that the question is open. And the suite
asks for a document without helping to write one.

The question costs nothing while it is open. Until it is settled, the suite treats whatever code outside the
repository could reach as covered: Strangler Fig only, and the BC-safe Rector path. It starts to cost at the moment
a plan takes the careful way only because the promise is open. That moment is the right one to ask.

No standard exists for a BC promise document. The written promises of large projects answer the same questions
(who the consumer is, what is covered and excluded, what each consumer role may rely on, the deprecation procedure
and its window, experimental parts, exceptions, support), and a draft can answer most of them from evidence in the
repository.

## Decision

- **A Tool on request.** `bc-promise` is a Tool of the generic Pack, Role Compatibility Policy (no Signal), status
  on request, one Safety Net Stage with no `requires` and no `waits_for`. Being on request, it blocks nothing: the
  Safety Net is fulfilled without it.
- **Fulfilled** when the tracker file's **BC promise** bullet is there: a path that exists in the repository, an
  `https://` URL (not fetched to judge the Stage), `none`, or a list of these, each with its scope. A document
  without the bullet does not count.
- **An Opener.** A Tool file may name an *Opener*: the situation in a run where the Tool would have paid off. A plan
  that meets it writes `Opener: <tool> — <why>` under `Decisions`. A Stage on request with an Opener found counts as
  not known, so the next scan of its Track is due and proposes it. A ticket of the Tool in any state, or a recorded
  rejection of the Tool, its Stage or its Role, uses the Opener up. `bc-promise`'s Opener is a plan that takes the
  careful way only because the promise is not settled.
- **A ticket from an Opener waits for a human's yes,** in an autonomous run too: it carries the question "Set up
  <Tool>?" and the Opener with a link to its plan. On request stays a human's request; the Opener only asks at the
  moment the Tool would pay off. Until the yes the Tool is not asked for, so its Stage holds no Track.
- **The draft.** `bc-promise`'s ticket carries a draft that answers the questions of the Tool file from evidence in
  the repository, each answer with its evidence, each question without evidence left open. The draft describes
  practice; only the human's answer makes it a promise. The Tool file lists the questions, never a model text. A
  document that is already there gets the bullet only, the questions it leaves open named in the merge request;
  no consumer outside the repository gets `none` with its evidence.
- **The human decides on the ticket.** The merge request follows the answer, and its review is an ordinary one: the
  Driver may merge it in `merge` mode.
- **A rejection** keeps the careful default for good, and no Opener proposes the Tool again. A call that names the
  Tool still can.
- **Several promises.** The bullet may list parts, each with a scope: an area of the code or a surface (PHP API, HTTP
  API, CLI). Where scopes overlap, the stricter promise applies; code no part covers keeps the careful default; a
  single `none` holds only for the whole repository. The suite works the default branch, so the promise is that of
  its release line.
- **Roave keeps `applies_when`,** with no `requires` on `bc-promise`: through `rector-type-coverage`, which waits for
  Roave, a `requires` would hold the Safety Net until a human answers. Roave applies to the parts that follow SemVer.
- **Onboarding no longer asks.** The question leaves the interview, and *The BC promise alone* leaves the first step
  of a run.

## Considered Options

- **Keep the question in onboarding (ADR-0088).** Early, without context, and asked again on every autonomous run.
  Rejected.
- **A recommended Safety Net Stage.** Still early, and with a `requires` from Roave it would block the Safety Net
  while it waits for a human. Rejected.
- **On request without an Opener.** Nothing early, but a package whose human never thinks of it stays careful for
  good without anyone noticing. Rejected.
- **The run files the ticket itself at the Opener.** A run works one ticket; filing belongs to the scan and its
  filing decision. Rejected.
- **A merge request in every case, its review always "ask the human".** Needs an exception in the Driver's review
  and in `merge` mode. Deciding on the ticket needs none. Rejected.

## Consequences

- An onboarding is one question shorter, and a run's first step checks only the required operations.
- An open promise shows up once, where it costs, and then waits as a ticket of its own, where the Driver lists it.
- The Opener is a general mechanism. The first Opener is `bc-promise`'s; Semgrep, Psalm Taint Analysis and Secret
  Detection get theirs as a follow-up.
- New: the term Opener, the Tool, Role and Stage `bc-promise`, the extended bullet.
