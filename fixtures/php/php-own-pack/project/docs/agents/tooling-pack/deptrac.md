# Deptrac

The Tool for the Role Architecture Rules in this project's own Pack: it checks the dependencies between the layers.

**Why this order.** A Guardrails Stage: workable once the Safety Net is fulfilled. The strict rules wait for the layers.

### `deptrac-layers`

- **Purpose:** the layers of `src/` and the dependencies allowed between them are declared and checked.
- **Fulfilment check:** `qossmic/deptrac` is a dev dependency, a `deptrac.yaml` declares the layers, and `vendor/bin/deptrac analyse` exits 0.
- **MR scope:** the dependency, `deptrac.yaml` with the layers as they are, and a baseline for the violations that exist.

### `deptrac-strict`

- **Purpose:** no violation is left in the baseline.
- **Fulfilment check:** the baseline of `deptrac-layers` is empty.
- **MR scope:** fix the violations the baseline holds, part by part.
