# Testing

Use an isolated Python environment and install `python -m pip install -e ".[dev]"`.
Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`.
CI covers Python 3.10 and 3.14 on Linux, Windows, and macOS. Image tests use Pillow
and tiny synthetic local PNG fixtures. Do not read a real media collection.

## 1.1.1 regressions

Test malformed JSON roots and containers, clean CLI diagnostics, existing files,
dangling output links and a deterministic concurrent report-creation boundary.
Inspect and install the actual wheel and source distribution outside the checkout;
verify all four documents, the sample, license, CLI output and unchanged inputs.

Also test huge integer metrics/bounds, invalid factors and paths, and finite large
batch medians. Existing relative/profile behavior and aspect-ratio precedence stay
covered; no video probing or arbitrary profile inference is supported.

A subprocess regression closes the stdout reader before execution and requires
status 2 without a traceback or interpreter-shutdown warning.

A small-report subprocess regression writes stdout to /dev/full and requires
status 2 without an interpreter-shutdown warning; skip when the device is absent.
