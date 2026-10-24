# Roave Backward Compatibility Check

The recommended Tool for the Role API Compatibility in the PHP Pack: it compares the code with the last
release and fails on a break. Run from its Docker image or GitHub Action, never a Composer entry: its own
dependencies often conflict with the target's, and the image runs on its own PHP, so no runtime floor
applies.

**Why this order.** A Safety Net Stage, because the breaks it catches come from the suite's own structural
work — an extracted class, a renamed method, a deleted path — and the check has to stand before that work
starts. It applies only to a target whose **BC promise** (`../../refactoring-operations.md`) follows semantic
versioning and that has a release tag `x.y.z`: the tool finds the release to compare against only in such
a tag, and it reports every removal as a break, which a promise counted in time and releases allows. It
requires `composer`, since it reads the API through `composer.json`'s autoload section, and waits until
`ci-runner` is decided; a rejected `ci-runner` releases it, run locally. Rector Type Coverage waits for it:
the detector before the rewriter.

### `roave-bc-check`

- **Purpose:** a change that breaks what the BC promise covers fails before it is merged. The suite's own
  restructurings are held to the promise by a tool, not only by `../../principles.md`.
- **Fulfilment check:** a CI job runs `roave-backward-compatibility-check` — the binary, the Docker image
  `nyholm/roave-bc-check` or the GitHub Action `docker://nyholm/roave-bc-check-ga` — with the tags fetched
  (on GitHub, `actions/checkout` with `fetch-depth: 0`). Presence of the invocation, not proof that it fails
  the pipeline on a break. With no CI, a run of the tool that ends green on the default branch.
- **MR scope:** the CI job, through the Docker image or the Action, with the tags fetched; on GitHub with
  `--format=github-actions`. Every source path covered by `composer.json`'s `autoload` section, which the
  tool needs to see the code — where it is not, the merge request adds the missing entry. One run against
  the last release: a break it reports was either intended, on a branch heading for the next major
  version, and goes into `.roave-backward-compatibility-check.xml` as an `<ignored-regex>` with a comment
  naming the version that releases it; or it was not, and the merge request says so and leaves it to the
  human, since restoring an API is no refactoring. Also add the Housekeeping line below to the target's
  Housekeeping template (`../../implement-point.md`, *Slices every kind of ticket can have*).
- **Ratchet:** the ignored breaks only shrink. A new entry is added only for a break the promise allows in
  the next major version, by the change that makes it.
- **Housekeeping:** after a release, remove each `<ignored-regex>` entry the release has made obsolete;
  the check then compares against the new tag.
