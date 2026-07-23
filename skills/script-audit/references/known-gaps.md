# Known Gaps and Historical Fixes

Last Updated: 2026-07-24

## Resolved Issues

### 2026-07-24: script-audit self-correction — v2 auth, pagination, input wrapping

**Issue**: This skill (`script-audit`) previously stated three claims that contradicted the published v2 contract and live API behavior:

1. **Auth**: "v2 无 `api-key` header" / "v2 调用用 `api-key` 会静默未鉴权 → error". The published `public/openapi.json` lists `ApiKeyAuth` (`api-key` header) alongside `BearerAuth` and `QueryTokenAuth` as global security on every operation including `runWorker`. So `api-key` header is a legitimate v2 auth mode, **not** an error. (The sibling `readme-writer` skill already stated this correctly.)
2. **Pagination**: "1 基页索引（`page_index = offset/limit + 1`），用 `offset += limit` 跳行会拿到错页". Live verification on run `01KY6QQKPAAQS6DGQ6RD7JWDE8` (100 rows): `offset` is a **zero-based row offset** — `offset=0,limit=5` returns rows 1-5, `offset=5,limit=5` returns rows 6-10, `offset=10,limit=5` returns rows 11-15. So `offset += limit` is **correct** and does not skip rows. `page_index = floor(offset/limit)+1` is a response-only 1-based display page number, not a request parameter and not a row offset. `offset` need not align to a multiple of `limit` (`offset=3,limit=5` is legal, returns rows 4-8).
3. **Input wrapping**: the REST fallback example showed `{"input": {...}}` (top-level object). v2 `runWorker` requires Worker form fields under `input.parameters.custom` (not top-level `input`, not legacy `custom_params` string).

**Verification (2026-07-23/24)**: live `GET /api/v2/worker-runs/{runId}` and `/result` calls confirmed response field shapes (`slug`, `status`, `results`, `err_msg` absent on success, `usage`/`traffic`, `started_at`/`finished_at`/`duration` Unix seconds; result `count`/`headers[].{key,label}`/`list[]` with internal `__coreclaw_data_id__`); `GET /api/v2/worker-runs/{runId}/log` confirmed `all_logs_url` + `list[].{type,group,content,timestamp}` (ms) + `result_count`. Status enum confirmed `ready/running/succeeded/failed/aborting` — `aborted` not in contract.

**Fix**:
- `SKILL.md`: removed `api-key` from the `error` severity list; corrected the auth paragraph to "v2 支持三种等价鉴权"; added verified run-detail/result/log response-field facts to the MCP/API section; added status-enum note (`aborted` not in contract).
- `references/verification-protocol.md`: corrected REST example to `input.parameters.custom`; corrected auth note; corrected the "无漏行" check row (offset is row offset, not page number).
- `references/concurrency-suggestions.md`: rewrote the P2 pagination section — `offset` is a row offset, `offset += limit` is correct, `page_index` is a response-only display page number.
- `README.md`: corrected the "1 基分页 offset" hook to "分页语义（offset 行偏移 + page_index 显示页号）".

**Status**: ✅ Resolved — these were the same class of error as the 2026-06-17 "code 4000" incident (claim contradicted by live probe). Recorded here per the skill's own source-traceability principle so future audits do not reintroduce them.

### 2026-06-30: New concurrency fields contract not supported

**Issue**: CLI validation treated legacy `b` as required and local `--split` only supported single-field `b` splitting. The platform now prefers `concurrency.fields` with optional `remove_fields`, while keeping `b` only as legacy fallback.

**Documentation**: 平台并发拆分规则说明 HTML（2026-07 版），`coreclaw-cli` 仓库内引用

**Fix**:
- Added schema validation for `concurrency`, `fields`, and `remove_fields`
- Removed the missing-`b` error when `concurrency.fields` is used or no split key is configured
- Updated local split expansion for preferred fields, `remove_fields` deletion, empty item filtering, primitive wrapping, object merging, and union splitting
- Kept legacy `b` fallback with trim support and empty-array errors
- Updated Apify migration schema drafts to emit both `concurrency.fields` and legacy `b`
- Added `references/concurrency-rules.md` and R190-R202 in the contract checklist

**Tests**: Added focused schema/runtime split tests and migration draft assertions.

**Status**: ✅ Resolved

### 2026-06-22: SOCKS proxy implicit dependency not detected

**Issue**: Python workers using `requests` with `socks5://` proxy URLs fail in cloud with "Missing dependencies for SOCKS support" because `PySocks` is not declared. CLI had no detection for this cross-module implicit dependency.

**Documentation**: proxy-support.md — all examples use socks5:// protocol.

**Fix**:
- Added `validateSocksProxyDependencies()` for Python: detects requests + socks5:// without PySocks → error
- Added `validateNodeSocksProxyDependencies()` for Node.js: detects socks-proxy-agent usage → error
- Added R130, R131 to contract checklist

**Tests**: 3 new test cases (Python socks missing, Python socks declared, Node socks-agent missing)

**Status**: ✅ Resolved

### 2026-06-22: HTTP workers without proxy only warned

**Issue**: Official docs (builds-and-runs.md) state "Network is sandboxed — HTTP request scripts must use the built-in SOCKS5 proxy". Without proxy, all outbound requests fail in cloud. CLI only warned.

**Fix**: Upgraded `http_proxy_env_not_used` from `warn` to `error`. Updated message to emphasize cloud failure.

**Tests**: Updated existing proxy test assertions

**Status**: ✅ Resolved

### 2026-06-22: Browser framework dependencies not checked

**Issue**: Workers using Playwright/Selenium/Puppeteer/DrissionPage without declaring the framework package would fail at import time in cloud. CLI only checked browser endpoint env vars.

**Fix**: Added `validateBrowserFrameworkDependencies()` with Python and Node.js framework pattern matching. Supports -core variants. Added R140, R141 to contract checklist.

**Status**: ✅ Resolved

### 2026-06-22: Protobuf version not pinned warning missing

**Issue**: Python-example.md states "protobuf version must match the one used to generate sdk_pb2.py". Unpinned versions can cause deserialization errors.

**Fix**: Added `validateProtobufVersionMatch()` — warns when protobuf is not pinned with ==. Added R160.

**Tests**: 2 new test cases

**Status**: ✅ Resolved

### 2026-06-22: Hardcoded User-Agent not detected

**Issue**: browser-fingerprinting.md says platform manages fingerprints. Hardcoded User-Agent may trigger anti-bot detection.

**Fix**: Added `validateHardcodedUserAgent()` — warns on User-Agent strings. Added R170.

**Tests**: 1 new test case

**Status**: ✅ Resolved

### 2026-06-22: Static push_data key analysis missing

**Issue**: output-schema.md requires push_data keys to match output_schema.json. CLI only checked at runtime.

**Fix**: Added `validateStaticPushDataKeys()` — bidirectional comparison of set_table_header keys with output_schema.json names. Added R180, R181.

**Status**: ✅ Resolved


### 2026-06-17: Editor-type mismatches only warned, not errored

**Issue**: Platform rejects workers with code 4000 "Invalid custom parameters" when editor type doesn't match property type (e.g., textarea+array, input+integer), but CLI only produced `warn` severity.

**Documentation**: input-schema.md — editor type guide tables show which types each editor supports.

**Fix**: 
- Upgraded `input_editor_type_mismatch` from `warn` to `error`
- Added STRING_ONLY_EDITORS check for input/textarea/datepicker
- Added ARRAY_ONLY_EDITORS check ensuring array type uses compatible editors
- Error message now includes "code 4000" and remediation suggestion

**Tests**: 5 new test cases (textarea+array, input+integer, array+input, stringList ok, stable codes)

**Commit**: b87e766

**Status**: ✅ Resolved (then **reversed on 2026-07-13**: platform verification with `examples/verify-code4000` v2 proved the platform does NOT reject any of the 11 mismatched combos — all upload and run. Downgraded back to `warn` and removed "code 4000" wording. See the resolved C1 entry above.)

### 2026-06-17: requestList/stringList default shape only warned

**Issue**: Invalid default items for requestList (missing url) and stringList (missing string) were only warnings, but platform rejects these.

**Fix**: Upgraded `input_default_list_item_invalid` from `warn` to `error` for requestList and stringList.

**Tests**: 2 new test cases

**Commit**: b87e766

**Status**: ✅ Resolved

### 2026-06-17: output_schema missing column type not detected

**Issue**: When `output_schema.json` column definition omits the required `type` field, the error message said "is not supported" rather than "is required".

**Fix**: Added explicit `column.type === undefined || null` check before the supported-type check.

**Tests**: 3 new test cases (missing type, unsupported type, all valid types)

**Commit**: b87e766

**Status**: ✅ Resolved

---

## Pending Issues

### Resolved: unsupported editor upgraded to error (platform-verified)

**Date**: 2026-07-14

**Issue**: `input_property_unsupported_editor` (and `input_param_unsupported_editor`) were `warn`, with a vague "Verify platform rendering before upload" message. Real scripts used `editor: "text"` (undocumented; docs say `input` for single-line text).

**Platform verification (2026-07-14)**: Two workers used `editor: "text"` and the user observed the form fields did not render. An undocumented editor value causes the platform form to fail rendering that field — a serious usability bug, not a soft warning.

**Fix** (`src/validation/schema.js`):
- Both `input_property_unsupported_editor` and `input_param_unsupported_editor` upgraded `warn` → **error**.
- Message strengthened: for `text` specifically, "will cause the form field to not render. Use \"input\" for a single-line text field..."; for other unknown editors, lists all 12 documented editor values.
- Wording changed from "may cause" to "will cause" (confirmed behavior).

**Tests**: 2 tests updated (text-editor → error severity; param_list slider → error). 375 pass, 0 fail.

**Status**: ✅ Resolved

### Resolved: concurrency field non-array downgraded to warn (platform-verified)

**Date**: 2026-07-14

**Issue**: `input_schema_concurrency_field_not_array` and `input_schema_b_not_array` were `error`, claiming the platform rejects concurrency fields that point to non-array properties.

**Platform verification (2026-07-14)**: Ran zillow-property-scanner (`01KWXWYADD2390HP9H1P7VRYPM`) whose `concurrency.fields: ["location"]` points to a `string` property. The platform **accepted the schema and the run succeeded** (1 subtask, 0 results — a script business-logic issue, not a schema rejection). A non-array concurrency field simply cannot be split, so the run executes as a single task.

**Fix**:
- `src/validation/schema.js`: both checks downgraded `error` → `warn`; messages now say "The platform accepts the schema, but a non-array field cannot be split into multiple tasks — it will run as a single task."
- `src/runtime/input.js` `meaningConcurrencyItems`: a non-array value is now treated as "no value" (returns `[]`) instead of throwing `field [X] must be an array`, so local `--split` matches cloud behavior (which skips non-array fields rather than hard-erroring).
- Tests updated: `warns when b points to a non-array property`; `legacy b reports missing field separately from non-array field` now expects the empty-field error for non-array values.

**Tests**: 374 pass, 0 fail.

**Status**: ✅ Resolved

### Resolved: editor/type mismatch downgraded to warn; "code 4000" wording removed (plan C1)

**Date**: 2026-07-13

**Issue**: `src/validation/schema.js` messages (and tests + reference docs) told users the platform rejects editor/type mismatches with "Invalid custom parameters (code 4000)". The official `api/error-codes.md` table has no code 4000 — business-layer codes start at 10000 (`SYSTEM_ERROR`).

**Platform verification (2026-07-13)**: Uploaded `examples/verify-code4000` v2 — 11 mismatched editor/type combos in one schema (textarea+array, switch+array, json+string, select-multiple+string, input+boolean, number+string, checkbox+string, requestList+string, radio+object, datepicker+integer, stringList+string). The platform **accepted the upload and ran all 11 successfully**, delivering each field's value per its declared type. The only observed side effect was a form-rendering glitch (checkbox+string options were unselectable in the UI) — no hard rejection.

**Fix** (`src/validation/schema.js`):
- Downgraded `input_editor_type_mismatch` (3 sites: expected-types, string-only-editors, array-with-non-array-editor) and `input_select_multiple_type_mismatch` from `error` to `warn`.
- Replaced all "The platform will reject this as 'Invalid custom parameters' (code 4000)" wording with "The platform accepts the schema and runs it, but the form control may render or behave incorrectly".
- Updated 5 tests in `test/schema.test.js` (renamed "as error" → "as warn", assert warn severity + absence of "code 4000" wording).

**Tests**: 366 pass, 0 fail.

**Status**: ✅ Resolved

### Resolved: documented required property fields severity (plan C2)

**Date**: 2026-07-13

**Issue**: `input-schema.md` L229-236 marks `title`/`name`/`type`/`editor`/`description`/`required` as Required=Yes on every property. The CLI previously only validated `name`+`type`.

**Platform verification (2026-07-13)**: Uploaded `examples/verify-required-fields` v2 — 7 properties each omitting a different field (missing title / description / editor / required / type / naked-name-only / valid control). The platform **accepted the upload and ran all 7 successfully**, delivering each default value. Even `p_missing_type` and `p_naked` (only name+default) were accepted.

**Fix**: `input_property_missing_title/editor/description/required` remain **warn** severity (confirmed correct — platform does not enforce these as hard requirements; the warnings serve as documentation-convention reminders).

**Status**: ✅ Resolved (kept as warn)

### Resolved: 2026-07-11 docs sweep — six new validators

**Issue**: Full docs comparison (scraper-webui-docs) found documented rules the CLI did not enforce: CamoufoxDomain as a browser endpoint, Camoufox playwright pinning, upsert unique-key existence, header-before-push ordering, axios `proxy:false`, and hardcoded proxy credentials.

**Fix** (all in `src/validation/project.js`):
- `scanSourceForBrowserContract` now recognizes `CamoufoxDomain` (builds-and-runs.md L72-74); `BROWSER_AUTOMATION_DOCS` includes camoufox.md.
- `validateCamoufoxPlaywrightVersion` — python worker reading `CamoufoxDomain` must pin `playwright==1.49.1` (camoufox.md L18) → **error**.
- `validateUpsertUniqueKey` — statically scans `upsert_data`/`upsertData`/`UpsertData` literal key arg, errors if the key is not an output_schema.json column (output-schema.md L101-129) → **error**.
- `validateHeaderBeforePush` — warns when a `set_table_header` call appears after a `push_data` call in the same file (sdk-modules.md L241) → **warn**. Scoped to "header exists but late" so the runtime hard-error on missing header is not duplicated.
- `validateNodeSocksProxyDependencies` extended — warns when axios + socks-proxy-agent is used without `proxy: false` (proxy-support.md L192) → **warn**.
- `validateHardcodedProxyCredentials` — detects literal `socks5://user:pass@` URLs (proxy-support.md L190, camoufox.md L32) → **error**. Template-literal URLs (`${PROXY_AUTH}`) are intentionally not flagged.

**Tests**: 11 new test cases in `test/project.test.js`. 365 pass, 0 fail.

**Status**: ✅ Resolved

### Resolved: output_schema.json missing upgraded to error

**Date**: 2026-07-11

**Issue**: CLI warned when output_schema.json was absent ("legacy compat"), but the docs list it as required: project-structure.md includes output_schema.json in every language's required-files tree, and builds-and-runs.md L35 states platform ZIP validation checks "entry file, input_schema.json, output_schema.json".

**Fix**: Upgraded `missing_output_schema` (renamed from `missing_output_schema_legacy`) from `warn` to `error`. Code renamed so stale ignore-profiles do not silently swallow a hard error.

**Tests**: Updated project/validate/pack/verify/audit tests to use the new code and to use `missing_readme` as the canonical warning trigger for warn-gate tests. 354 pass, 0 fail.

**Status**: ✅ Resolved

### Low Priority: requestListSource default validation severity

**Current**: `warn` for invalid requestListSource defaults
**Consideration**: requestListSource defaults have complex param_list structure; keeping as `warn` for now since platform may be more lenient with these.

### Low Priority: output_schema.json missing from project

**Current**: `error` when output_schema.json is absent (upgraded 2026-07-11).
**Consideration**: Resolved — docs list it as required (project-structure.md, builds-and-runs.md L35). See Resolved section above.

---

## Pattern Notes

### Common Gap Types

1. **Missing Validation**: Rule exists in docs but not implemented
2. **Wrong Severity**: Rule implemented as warn() but should be error()
3. **Missing Test**: Rule implemented but no test coverage
4. **Incomplete Error Message**: Rule implemented but error message not helpful
5. **Edge Case Missing**: Rule implemented but doesn't handle all cases

### Severity Guidelines

- **error**: Platform will reject the worker at upload or runtime (missing required files/fields like output_schema.json, HTTP scripts not reading proxy, hardcoded proxy credentials, camoufox playwright pin, upsert key not in output_schema). Editor/type mismatches are **not** in this category — platform verification (2026-07-13) confirmed they are accepted.
- **warn**: Platform accepts but the form may misbehave or it's a best-practice convention (editor/type mismatch, missing documented-required title/editor/description/required, unknown editor, legacy type alias, missing README)
- **info**: Informational only (case mismatches, optional recommendations)

### Testing Strategy

When fixing a gap:
1. Add validation logic in schema.js or project.js
2. Add test case with both valid and invalid inputs
3. Run `npm test` to verify no regressions
4. Test with real workers if applicable
5. Update contract-checklist.md to mark rule as [x]
6. Update this file with resolution notes
7. Commit and push
