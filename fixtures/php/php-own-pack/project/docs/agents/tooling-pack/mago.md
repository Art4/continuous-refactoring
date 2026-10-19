# Mago

This project uses Mago for static analysis instead of PHPStan. It is recommended in this Pack; the project rejects the suite's PHPStan.

### `mago`

- **Purpose:** static analysis introduced green.
- **Fulfilment check:** `carthage-software/mago` is a dev dependency, a `mago.toml` is committed, and `vendor/bin/mago analyze` exits 0.
- **MR scope:** the dependency, `mago.toml` and the fixes or baseline the first run needs.
