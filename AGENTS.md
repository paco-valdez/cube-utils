# AGENTS.md

This repository contains two implementations of the same Cube.js utility
functions: a **Python** package in `cube_utils/` and a **JavaScript**
package in `cube-utils-js/`.  The code is intentionally kept identical
so that both implementations provide the same API surface.

When adding or modifying code:

* Follow the style guidelines in `CLAUDE.md`.
* Keep the public API consistent across both languages, the API is also described in `CLAUDE.md`.
* Ensure any new functionality is covered by tests in the `tests/`
  directory.

The `tests/` folder contains unit tests that validate the expected
behaviour of both the Python and JavaScript versions.
