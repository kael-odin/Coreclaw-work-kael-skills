# Verification Protocol — Live Input/Output via API/MCP

Static rules say the schema is well-formed. They do not say the platform
accepts the actual values, or that the output is correct. This is the protocol
for the live-verification layers (L2 + L3).

## L2 — Live input verification

Goal: confirm the platform accepts a real input, and capture the real
`code`/`message` on rejection. This is the probe that justifies any `error`
severity claim without a structural reason.

### Build the probe input

1. `get_worker_input_schema` — re-read the live schema. Never invent field
   names from memory or from the worker's README; the live schema is
   authoritative.
2. Construct a minimal `input_json` that exercises one field at a time. Minimal
   = smallest input that should produce a non-empty result. For a Google Maps
   worker: one keyword + one small city, not 500 keywords across 50 cities.
3. For concurrency-split workers, test both a single-item array (smallest) and
   a two-item array (confirms split produces two tasks, not one).

### Run via MCP (preferred)

```
run_worker(worker_id, input_json, is_async=true)  → run_id
get_worker_run(run_id)                            → status, code, message
get_worker_run_log(run_id)                        → on failure: real error
```

MCP carries the pagination compensation and `/last` freshness fixes; raw REST
does not.

### REST fallback

```
POST https://openapi.coreclaw.com/api/v2/workers/{worker_id}/runs
Authorization: Bearer <token>
Content-Type: application/json
{"input": {...}}        # top-level input, NOT wrapped (v2 runWorker)
```
Wait, then `GET /api/v2/workers/{worker_id}/runs/{run_id}`. Contract:
`exported-api-docs/openapi.json` operationId `runWorker`, `getWorkerRun`.

**Auth trap**: v2 has no `api-key` header. Bearer header or `?token=` query
only. A v2 caller using `api-key` is silently unauthenticated → `error`.

### Probe artifact

Record the probe result so the `error` claim is auditable later:

```
examples/verify-<topic>/
  README.md      # input, expected, actual: platform accepted/rejected, real code+message, date
  input.json     # the exact input submitted
  result.json    # captured response (status, code, message, result_count)
```

Status markers: `⏳ 待验证` → `✅ Resolved` (accepted) or `⚠️ 实测推翻`
(rejected the hypothesis). Resolved probes stay as regression artifacts.

### Severity decision after probe

- Platform hard-rejects (non-zero `code`, HTTP 4xx/5xx, does not run) → `error`.
- Platform accepts but form/runtime misbehaves (e.g. checkbox option won't
  check) → `warn`.
- Platform accepts and runs cleanly → not a finding, or `info` only.
- No probe yet → `[VERIFY]`, never `[ERROR]`.

## L3 — Output correctness

Goal: the run succeeded, but is the output right? Schema validation cannot
catch a `phone` field carrying a URL, or a numeric `rating` shipped as a
string.

### Sample the results

```
list_worker_run_results(run_id, limit=20)   # preview rows
export_worker_run_results(run_id, format='json')  # signed download_url for full diff
```

8 export formats: **CSV, JSON, JSONL, XLSX, XLS, XML, HTML, RSS**.

### Check matrix

| Check | What to verify | Failure example |
|-------|----------------|-----------------|
| Field presence | every `output_schema` column present in rows | schema has `email`, rows never include it |
| Field correctness | spot-check 3-5 rows vs source page | `phone` holds a website URL; `rating` is a string not number |
| Shape vs schema | schema `array<string>` vs row value | schema says array, row carries comma-separated string |
| Dedup across splits | no duplicate rows across `concurrency.fields` tasks | same place appears twice from two split tasks |
| No missing rows | row count vs expected (mind 1-based offset trap) | 120-cap not hit because offset misused as row-skip |
| CAPTCHA/403 rows | error rows not misread as success | a 403 HTML body captured as a "result" row |

For the last one, prefer `verify_run` — it returns a structured verdict
(`PASS`/`NO_DATA`/`FAILED`/`ERROR_RECORD`/`RUNNING`/`SUBMIT_FAIL`) that guards
against CAPTCHA or 403 rows being misread as a successful PASS.

### Correctness findings are `error`

Unlike platform-rejection findings, correctness bugs don't need an upload
probe — the wrong output IS the evidence. But cite the row that demonstrates
it: `[ERROR] L3: phone field carries website URL on row 3. src: verify_run
sample 2026-07-21 [result.json:row3]`.

## Recency

Protocol reflects v2 API + MCP server behavior as of 2026-07-21. The MCP
server's pagination compensation and `/last` freshness fix are in place; raw
REST callers still need to align `offset` to a `limit` multiple manually.
