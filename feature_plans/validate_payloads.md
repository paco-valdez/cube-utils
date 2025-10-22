## Feature Plan: Validate Payload Types for Query Parser

**Context** – The current query parser functions (`extract_cubes`, `extract_members`, `extract_filters_members`, `extract_filters_members_with_values`, and helpers) assume that the `payload` argument is a dictionary.  When a string is supplied, a `TypeError` is raised, causing failures in the test suite.

**Goal** – Gracefully handle string payloads by returning an empty result (empty list or `None`) instead of raising an exception.  This mirrors the behaviour of Cube.js for metadata queries, which are represented as simple strings.

### Detailed Steps

1. ✅ **Create a helper** `._ensure_dict_payload(payload)`
   * Accepts `payload` and returns it if it is a `dict`.
   * If `payload` is a `str`, return an empty dict `{}`.
   * If `payload` is `None` or any other type, raise `TypeError` with a clear message.
   * Place this helper in `cube_utils/query_parser.py` near the top of the file.

2. ✅ **Update `extract_cubes`**
   * Add a call to `_ensure_dict_payload(payload)` at the start.
   * Continue with existing logic, which now operates on a guaranteed dict.

3. ✅ **Update `extract_members`**
   * Same pattern: validate first, then perform extraction.

4. ✅ **Update `extract_filters_members`**
   * Validate payload; if it was originally a string, the helper returns `{}` and the function will return an empty list.

5. ✅ **Update `extract_filters_members_with_values`**
   * Validate payload; handle string case similarly, returning `[]`.

6. ✅ **Update `extract_members_from_expression`**
   * No change needed, but add a comment clarifying that it expects a string expression.

7. ✅ **Update `extract_members_from_filter`**
   * Ensure this helper is only called with a dict; add a guard or comment if necessary.

8. ✅ **Add unit tests** in `tests/test_query_parser.py`:
   * For each public function, create a test that passes a string payload and asserts the returned value is an empty list (or `None` where appropriate).
   * Example:
     ```python
     self.assertEqual(extract_cubes("some string"), [])
     ```

9. ✅ **Update documentation**:
   * In `CLAUDE.md`, add a note that all query‑parser functions now accept string payloads gracefully.
   * Update inline docstrings to reflect the new behaviour.

10. ✅ **Run tests**:
   * Execute `python -m unittest discover tests` to ensure existing tests continue to pass and the new tests succeed.

11. ✅ **Code review**:
   * Verify that the new helper and guard logic adhere to the repo's style (PEP‑8, docstrings, type hints).
   * Ensure no other modules import `query_parser` expecting the previous behaviour.

**Outcome** – After implementation, the parser functions will no longer crash on string payloads and will correctly return empty results for metadata queries, matching Cube.js’s expectations.
