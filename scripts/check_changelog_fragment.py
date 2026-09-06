#!/usr/bin/env python3
"""CI gate: a PR touching user-facing paths must add a changelog fragment.

See CONTRIBUTING.md's "Changelog" section for the full mechanism: noteworthy
changes drop a free-form `.changelog.d/<slug>.md` fragment, consolidated into
`CHANGELOG.md` (and the fragments deleted) at release time.

This script only judges whether a *fragment is required and present* — it
does not judge whether a change is "noteworthy" (that's a human call at
review time) beyond the coarse, path-based heuristic below. A PR that
genuinely needs no fragment carries the `no-changelog` label instead.

Run in CI as:
    python3 scripts/check_changelog_fragment.py <changed-file>...

Changed files are normally supplied via `git diff --name-only` against the
PR's base ref; the `no-changelog` label bypass is read from the
CHANGELOG_FRAGMENT_LABELS environment variable (comma-separated label names).
"""

import os
import sys

FRAGMENT_DIR = ".changelog.d/"
EXEMPT_PREFIXES = ("docs/adr/",)
TRIGGER_PREFIXES = ("skills/", "docs/")
TRIGGER_FILES = ("README.md", "CONTRIBUTING.md")
NO_CHANGELOG_LABEL = "no-changelog"


def is_trigger_path(path):
    if path.startswith(EXEMPT_PREFIXES):
        return False
    if path in TRIGGER_FILES:
        return True
    return path.startswith(TRIGGER_PREFIXES)


def requires_fragment(changed_files):
    return any(is_trigger_path(f) for f in changed_files)


def has_fragment(changed_files):
    return any(
        f.startswith(FRAGMENT_DIR) and f.endswith(".md") for f in changed_files
    )


def check(changed_files, labels):
    if not requires_fragment(changed_files):
        return None
    if has_fragment(changed_files):
        return None
    if NO_CHANGELOG_LABEL in labels:
        return None
    return (
        "This PR touches skills/**, docs/** (outside docs/adr/**), README.md, "
        "or CONTRIBUTING.md but adds no .changelog.d/*.md fragment. Add one "
        "describing the user-visible change (see CONTRIBUTING.md), or apply "
        f"the '{NO_CHANGELOG_LABEL}' label if this change has no user-visible "
        "effect."
    )


def main(argv):
    changed_files = argv[1:]
    labels_env = os.environ.get("CHANGELOG_FRAGMENT_LABELS", "")
    labels = [label.strip() for label in labels_env.split(",") if label.strip()]

    message = check(changed_files, labels)
    if message is None:
        return 0

    print(message, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
