# Known Pitfalls — Script Audit Cross-Check

Canonical pitfall set for CoreClaw work scripts. Each entry: the trap, how to
spot it in a script, the severity, and the source pointer. When a script
matches, cite the source in the finding.

## P1 — SDK input not wrapped as `parameters.custom`

**Trap:** `worker.run({ input: {...} })` passes input top-level. The SDK
expects `parameters.custom`. Top-level input is silently ignored or rejected.

**Spot:** grep for `worker.run(` / `.run(` calls; check whether the input
object is nested under `parameters.custom`.

**Severity:** `error` (runtime — input never reaches the worker).

**Source:** memory `[[coreclaw-sdk-input-pitfall]]`. Confirmed across Node and
Python SDK evaluation (`[[coreclaw-sdk-evaluation]]`).

## P2 — Pagination `offset` treated as absolute row offset

**Trap:** upstream list endpoints (`/workers`, `/workers/{id}/runs`,
`/workers/{id}/tasks`, etc.) interpret `offset` as 1-based page index, i.e.
`page_index = offset/limit + 1`. A caller doing `offset += limit` to skip rows
gets wrong pages — duplicate or missing rows, no error.

**Spot:** any loop that increments `offset` by `limit` and expects row
semantics; any REST caller paginating without aligning `offset` to a `limit`
multiple.

**Severity:** `error` (correctness — silent wrong data).

**Source:** memory `[[coreclaw-pagination-bug-fix-2026-07-15]]`. The
`coreclaw-mcp-server` adds a transparent compensation layer; raw REST callers
must align manually. Note: do not write the literal token `page_index` in docs
consumed by `validate_skill.py` (its FORBIDDEN_PATTERNS includes it) — phrase
as "1-based paging".

## P3 — `schedule_weekday` enum 0-6 / 0=Sunday

**Trap:** the real enum is **1-7, 1=Monday, 7=Sunday**. Any code or schema
writing 0-6 or 0=Sunday is wrong.

**Spot:** grep `schedule_weekday` / `scheduleWeekday`; check enum and default.
n8n `type:'options'` param default must be an enum value, not `''`.

**Severity:** `error` (wrong day scheduled, or n8n CI lint red).

**Source:** `scraper-webui-docs/worker-tasks/create.mdx`; memory
`[[coreclaw-n8n-ci-lint-lesson]]`, `[[coreclaw-wrapper-repos-enum-fix-2026-07-10]]`.

## P4 — `format` enum incomplete or mis-ordered

**Trap:** export `format` has 8 values — `csv, json, jsonl, xlsx, xls, xml,
html, rss`. Option arrays must be **alphabetical**; format names in prose must
be **uppercase** (`JSON`, not `json`).

**Spot:** any `format` option array; any description mentioning format names
in lowercase.

**Severity:** `warn` (platform accepts, but n8n CI lint red and inconsistent).

**Source:** `[[coreclaw-wrapper-repos-enum-fix-2026-07-10]]`,
`[[coreclaw-n8n-ci-lint-lesson]]`.

## P5 — Hardcoded proxy credentials

**Trap:** `socks5://user:pass@host:port` literal in source commits credentials
to git. Template literals (backtick) are acceptable (env-injected); string
literals are not.

**Spot:** grep `socks5://`, `http://.*:.*@`, `proxy` literals.

**Severity:** `error` for string-literal creds; `warn` for axios +
socks-proxy-agent without `proxy:false` (request bypasses proxy).

**Source:** CLI validation rules A6/A7, `[[coreclaw-cli-validation-audit-2026-07-11]]`.

## P6 — Camoufox + Playwright not pinned

**Trap:** a Camoufox-domain browser script must pin `playwright==1.49.1`.
Unpinned versions break Camoufox compatibility at runtime.

**Spot:** grep `camoufox` / `CamoufoxDomain`; check `playwright` version pin
in requirements/package.

**Severity:** `error` (runtime break).

**Source:** CLI validation rule A3, `[[coreclaw-cli-validation-audit-2026-07-11]]`.

## P7 — Missing `output_schema.json`

**Trap:** worker project missing `output_schema.json` (legacy `_legacy` name
deprecated). Platform rejects.

**Spot:** check project tree for `output_schema.json`.

**Severity:** `error` (was `warn` before 2026-07-11).

**Source:** rule A1; `scraper-webui-docs` `builds-and-runs.md` L35,
`project-structure.md`.

## P8 — Upsert key not in output_schema

**Trap:** `upsert_data`/`upsertData`/`UpsertData` second argument is a literal
key; if that key is not a column in `output_schema`, the upsert is undefined.

**Spot:** grep upsert calls; resolve the literal key against schema columns.

**Severity:** `error`.

**Source:** CLI validation rule A4, `[[coreclaw-cli-validation-audit-2026-07-11]]`.

## P9 — Header after push

**Trap:** `set_table_header` called after `push_data` — header arrives too
late. Only flag when header exists but is later than push (don't duplicate the
runtime hard-error).

**Severity:** `warn`.

**Source:** CLI validation rule A5.

## P10 — n8n CI lint passes locally but fails CI

**Trap:** `npm ci --ignore-scripts` installs the CI-pinned `@n8n/node-cli`
rule set, which can be stricter than the developer's stale `node_modules`.
Local `npm run lint` green ≠ CI green.

**Spot:** before pushing an n8n node, run `npm ci --ignore-scripts && npm run
lint` locally.

**Severity:** process gate (not a code finding, a workflow finding).

**Source:** `[[coreclaw-n8n-ci-lint-lesson]]`.

## P11 — `/last` run endpoint stale

**Trap:** `/workers/.../runs/last` can return stale run state. MCP server
fixed (commit 0d22581); raw REST callers can still hit it.

**Spot:** any REST caller hitting a `/last` path for status.

**Severity:** `warn` (use `get_worker_run` with explicit `run_id` instead).

**Source:** `[[coreclaw-mcp-server-skill-audit-2026-07-10]]`,
`[[coreclaw-skill-plugin-wrapper]]`.

## P12 — Callback body field name

**Trap:** run-status callback body uses `run_status`, **not** `status`. The
`run_status` enum is lowercase strings (`succeeded`, `failed`, `running`,
`ready`, `submit_fail`) — **no `aborted`** value (abort is an action, not a
status).

**Spot:** any callback handler reading `status`; any enum listing `aborted`.

**Severity:** `error` (handler silently misses status transitions).

**Source:** `[[coreclaw-skill-plugin-wrapper]]` 2026-07-15 sync;
`[[coreclaw-sdk-v2-deep-bugs]]`.

## P13 — v2 auth uses Bearer, not `api-key` header

**Trap:** v1 used `api-key` header; v2 spec has **no** `api-key` header — only
`Authorization: Bearer <token>` or `?token=<token>`. A v2 caller using
`api-key` is silently unauthenticated.

**Spot:** grep `api-key` / `api_key` headers in v2 callers.

**Severity:** `error` (auth fails).

**Source:** `[[coreclaw-api-v2-surface-and-cli-gap]]`; v2 client rewrite commit
5eb1ca3 in `coreclaw-cli`.

## P14 — Business error code 4000

**Trap:** there is **no** code 4000. Business codes start at 10000 (10000
SYSTEM_ERROR, 12001/12002 auth, 30001 balance, 50001 worker-not-found, ...).
Any error message referencing "code 4000" is fabricated from a stale doc
assumption.

**Spot:** grep `4000` in error messages / tests.

**Severity:** `error` (misleading diagnostics).

**Source:** `exported-api-docs/error-codes.md`; `[[coreclaw-cli-validation-audit-2026-07-11]]`
2026-07-13 finalize.
