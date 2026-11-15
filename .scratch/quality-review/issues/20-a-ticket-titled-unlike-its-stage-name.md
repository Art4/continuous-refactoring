# 20 — A ticket titled as its Tool file names it does not carry its Stage's Name

Type: task
Status: open
Blocked by: —

**What the plays showed** (ticket 16's second play, ticket 17's play, r7 A and r8 A for ticket 18; named four times,
so a ticket under Q81). The rollout Stage's Name is "PHP CS Fixer Rollout"; its ticket is titled, as
`php-cs-fixer.md` *Its ticket* names it and Q69 decided, "PHP CS Fixer: take in the remaining rules". The worklist,
without a Candidate operation, runs **Search** with each Stage's Name (`worklist.md`, step 1), and *matches a Stage*
by its title or text naming the Stage's subject, "the Name tells siblings apart". The title holds the adoption's Name
"PHP CS Fixer" but not "Rollout", so players matched #53 only through the Tool file's *Its ticket* line or a listing
of all tickets, and each found it by a path the text does not give. `filing-a-ticket.md` writes the Stage's `search`
words into the ticket's text, which would match a full-text search, but a brief or a ticket filed by hand does not
show them. PHPMD's and ESLint's rollout tickets share the shape ("<Tool>: take in the remaining rules").

**To decide**

- Whether the title carries the Name ("PHP CS Fixer Rollout: take in the remaining rules"), which revisits Q69.
- Or whether matching names the ticket's title from the Tool file's *Its ticket* line as a match too, so the worklist
  finds a ticket by its Stage's Name or by its Tool file's title.
- Or whether the Stage's `search` words gain the title, so the trace and the worklist search for it alike.

**Done when** a rollout ticket titled as decided is matched to its Stage by the worklist and the trace without a
detour, the scenarios that read #53 (r7, r8) pass, and tests and validator are green.
