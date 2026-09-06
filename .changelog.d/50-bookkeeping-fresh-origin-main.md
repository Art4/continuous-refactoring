Fixed a staleness bug: the bookkeeping write now reads a fresh `origin/main` immediately before
writing, instead of a snapshot that could be several commits behind.
