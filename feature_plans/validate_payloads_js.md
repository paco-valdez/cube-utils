## Feature Plan: Validate Payload Types for Query Parser (JavaScript) ✅

**Context** – The JavaScript query‑parser functions (`extractCubes`,
`extractMembers`, `extractFiltersMembers`, `extractFiltersMembersWithValues`, and helpers) assume that the `payload` argument is an object.  When a string is supplied, a `TypeError` is thrown, causing test failures.

**Goal** – Gracefully handle string payloads by returning an empty result (empty array or `null`) instead of throwing. This aligns with the Python implementation and mirrors Cube.js’s handling of metadata queries represented as strings.

### Detailed Steps

1. **Create a helper** `ensureObjectPayload(payload)`
   - Accepts `payload` and returns it if `typeof payload === 'object' && payload !== null`.
   - If `payload` is a `string`, return an empty object `{}`.
   - If `payload` is `null` or any other type, throw a `TypeError` with a clear message.
   - Place this helper at the top of `cube-utils-js/src/query-parser.js`.

2. **Update `extractCubes`**
   - Call `ensureObjectPayload(payload)` at the start.
   - Proceed with existing logic using the guaranteed object.

3. **Update `extractMembers`**
   - Apply the same payload guard before extracting members.

4. **Update `extractFiltersMembers`**
   - Guard the payload; an empty object yields an empty member list.

5. **Update `extractFiltersMembersWithValues`**
   - Guard the payload similarly; a string payload results in an empty array.

6. **Update `extractMembersFromExpression`**
   - No change to logic, but add a comment noting that it expects a string expression.

7. **Update `extractMembersFromFilter`**
   - Ensure it is only called with a valid object; add a guard or comment if necessary.

8. **Add unit tests** in `cube-utils-js/test/query-parser.test.js`:
   - For each public function, create a test that passes a string payload (e.g., `"some string"`) and asserts the returned value is an empty array (or `null` where appropriate).
   - Example:
     ```js
     it('returns [] for string payload in extractCubes', () => {
       expect(extractCubes('foo')).toEqual([]);
     });
     ```

9. **Update documentation**
   - In `CLAUDE.md` add a note that all query‑parser functions now accept string payloads gracefully.
   - Update inline JSDoc comments to reflect the new behavior.

10. **Run tests**
    - Execute `npm test` inside `cube-utils-js` to ensure existing tests continue to pass and the new tests succeed.

11. **Code review**
    - Verify that the new helper and guard logic adhere to the repo’s style (ESLint, JSDoc, naming conventions).
    - Ensure no other modules import `query-parser` expecting the previous behavior.

**Outcome** – After implementation, the JavaScript parser functions will not crash on string payloads and will correctly return empty results for metadata queries, matching the Python version and Cube.js’s expectations.
