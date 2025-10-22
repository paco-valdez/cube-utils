# AGENTS.md

This repository contains two implementations of the same Cube.js utility
functions: a **Python** package in `cube_utils/` and a **JavaScript**
package in `cube-utils-js/`.  The code is intentionally kept identical
so that both implementations provide the same API surface.

When adding or modifying code:

* Follow the style guidelines in `CLAUDE.md`.
* Keep the public API consistent across both languages, the API is also described in `CLAUDE.md`.
* Ensure any new functionality is covered by tests in the `tests/` directory.
* **When generating a new file, write it to the repository.**
  The agent should not leave draft or incomplete files; if a file is
  created as part of a feature plan or implementation, it must be
  committed to the filesystem using `apply_patch` (or the equivalent
  file‑creation command). This avoids situations where a file appears
  in the plan but never actually exists in the repo.
* **If a command cannot be executed by the agent, explicitly suggest the user to run it** – for example:
  ```bash
  npm test --prefix cube-utils-js
  python -m unittest discover tests
  ```

The `tests/` folder contains unit tests that validate the expected
behaviour of both the Python and JavaScript versions.
