---
name: script-audit
description: >
  Audit a CoreClaw worker script end-to-end: static rules (error/warn), live
  input+output verification via API or MCP, output correctness, and concrete
  improvement suggestions (including concurrency.fields tuning for throughput).
  The rule set is sourced from and kept in sync with the Core-Claw/coreclaw-cli
  audit skill. Use when reviewing any CoreClaw worker before upload or after a
  bad run. Trigger on: "audit this worker", "审核脚本", "check this worker",
  "is this upload-safe", "why did this run fail", "improve concurrency".
---

# Script Audit (CoreClaw Worker)

Audit one CoreClaw worker script across five layers, then surface findings
ranked by severity with a source pointer for each. The static rule set is
**not authored here** — it is sourced from the `coreclaw-cli-audit` skill in
`Core-Claw/coreclaw-cli` and kept in sync. This skill adds the layers the CLI
audit does not cover: live API/MCP verification of input and output, output
correctness, and improvement suggestions (concurrency, throughput, cost).

## Sources

- **Authoritative rule set** (sync from here, do not re-derive):
  `Core-Claw/coreclaw-cli` → `skills/coreclaw-cli-audit/`
  - `SKILL.md` — audit workflow, severity policy, Phase-2 probe gate
  - `references/contract-checklist.md` — versioned rule checklist
  - `references/known-gaps.md` — resolved + open gaps with probe results
  - `references/concurrency-rules.md` — task-splitting rules (basis for improvement suggestions)
  - `scripts/diff-contract.cjs` — automated rule-vs-code diff
- **Platform docs**:
  - EN: https://docs.coreclaw.com/ · API: https://docs.coreclaw.com/api/
  - ZH: https://docs.coreclaw.com/zh-cn/ · API: https://docs.coreclaw.com/zh-cn/api/
  - MCP: https://docs.coreclaw.com/integrations/ai/mcp · ZH: https://docs.coreclaw.com/zh-cn/integrations/ai/mcp
  - Pricing: https://www.coreclaw.com/pricing
- **Local upstream contract mirror**: `D:/Coreclaw_Work/github/exported-api-docs/openapi.json` (37 operations, `/api/v2`, Bearer auth)
- **Local CLI clone** (run the audit script from here): `D:/Coreclaw_Work/github/coreclaw-cli/`
- Reference files in this skill: `references/verification-protocol.md`, `references/concurrency-suggestions.md`, `references/sync-procedure.md`

## Scope: what this skill audits

A single CoreClaw worker project, typically:
- `input_schema.json` — input fields, editors, types, concurrency config
- `output_schema.json` — output columns
- `main.py` / `index.js` — the scraper logic
- `README.md` / `README_CN.md` — input docs (cross-check against actual fields)

It does NOT audit the CLI's own validation code (that is `coreclaw-cli-audit`'s
job). The two skills are complementary: the CLI audit keeps the rule engine
correct; this skill applies that engine to a real worker and adds live
verification + suggestions.

## The five audit layers

### Layer 1 — Static rules (error / warn)

Run the CLI's validator against the worker, or apply its rule set by hand if
the worker is not yet packaged. The rule set lives in `coreclaw-cli-audit`;
**do not redefine rules here** — cite the rule code from
`references/contract-checklist.md`.

Severity policy (from the source skill, do not deviate):
- `error` = platform upload/runtime hard-rejects, or form won't render, or a
  correctness/security defect. Missing `output_schema.json`, hardcoded proxy
  credentials, Camoufox not pinning `playwright==1.49.1`, upsert key absent
  from output_schema, unknown editor value, HTTP script ignoring proxy, v2
  caller using `api-key` header.
- `warn` = platform accepts but form/runtime may misbehave, or a documented
  should/conventional. editor/type mismatch (proven accepted 2026-07-13),
  axios+socks without `proxy:false`, header-after-push, missing README, missing
  doc-marked title/editor/description/required.

**Iron rule (from the source skill): any `error` claim must be backed by a real
probe (`examples/verify-*`) or be structurally obvious (missing required file,
hardcoded credential literal). No `error` from a doc "must" alone.** The
2026-06-17 "code 4000" incident — fabricating an error code from a doc
assumption, overturned by 2026-07-13 probes — is the cautionary tale.

Run the CLI validator if the worker is packaged:
```bash
cd D:/Coreclaw_Work/github/coreclaw-cli
node src/cli.js validate <path-to-worker-project>
node skills/coreclaw-cli-audit/scripts/diff-contract.cjs   # rule + API-operation coverage
```

### Layer 2 — Live input verification (API / MCP)

Static rules say the schema is well-formed; they do not say the platform
accepts the actual input values. Verify by running the worker with a minimal
real input.

Prefer MCP (it carries the pagination compensation + freshness fixes):
- `get_worker_input_schema` — re-read the live schema; never invent field names.
- `run_worker` with a minimal `input_json` built from the live schema (async).
- `get_worker_run` + `get_worker_run_log` — capture the real `code` + `message`
  if the platform rejects. This IS the probe that justifies any `error`.

REST fallback (MCP unavailable): base URL `https://openapi.coreclaw.com`,
`Authorization: Bearer <token>` or `?token=<token>`. Contract:
`exported-api-docs/openapi.json`, operationId `runWorker`.

Full verification protocol with probe artifact format:
`references/verification-protocol.md`.

### Layer 3 — Output correctness

A run that succeeds can still produce wrong output. Verify the result rows
against ground truth, not just "the run finished":

- **Field presence**: every `output_schema.json` column appears in actual
  result rows (sample via `list_worker_run_results`).
- **Field correctness**: spot-check 3-5 rows against the source page. A
  `phone` field that carries a website URL, a `rating` that is a string not a
  number, a `reviews_count` that is null on a place with 200 reviews — these
  are correctness bugs the schema validator cannot catch.
- **Shape vs schema**: `output_schema` says `array<string>` but rows carry a
  comma-separated string → mismatch.
- **Dedup / pagination**: with `concurrency.fields` splitting, confirm no
  duplicate rows across split tasks and no missing rows from the 1-based
  offset trap (see `references/concurrency-suggestions.md` P2).

Export a small sample for diffing:
```bash
# via MCP: export_worker_run_results → signed download_url, format csv/json/jsonl/xlsx/xls/xml/html/rss
```
The platform supports 8 export formats: **CSV, JSON, JSONL, XLSX, XLS, XML,
HTML, RSS** (source: platform docs + `exported-api-docs`).

### Layer 4 — Improvement suggestions

This is the layer the CLI audit does not provide. For each finding, give a
concrete, actionable improvement, ranked by impact. The richest vein is
concurrency tuning — see `references/concurrency-suggestions.md` for the full
matrix. Summary:

- **Throughput**: if the worker has an array input (e.g. `keywords`,
  `place_ids`, `google_maps_urls`) but no `concurrency.fields`, suggest adding
  it so the platform splits the input into parallel tasks instead of running
  it serially as one task.
- **Cost control**: if a field can explode precharge (e.g. a URL list where
  each URL may return hundreds of results), suggest a `concurrency.limits`
  rule capping precharge per item. `limits` does NOT change task count or task
  content — only the precharged (billing) count per item.
- **Legacy migration**: if the worker still uses legacy `b` for splitting,
  suggest migrating to `concurrency.fields` (`b` is ignored when `fields` is
  present; `b` is compatibility-only).
- **`remove_fields`**: if a split field's values should not appear in
  downstream task custom objects (e.g. internal IDs), suggest
  `concurrency.remove_fields` so they are deleted, not retained as `[""]`.
- **Result quality**: if spot-checks found empty or malformed fields, suggest
  fixing the extractor rather than documenting the gap.

Other improvement categories: input-schema UX (editor choice, defaults,
descriptions), output completeness (missing useful columns), error messages
(include fix suggestions, never "code 4000"), README accuracy (fields match
actual schema — route to the `readme-writer` skill).

### Layer 5 — Ranked report

One finding per line, `error` first, then `warn`, then `VERIFY` (needs a
probe), then `SUGGEST` (improvement). Each carries a source pointer.

```
[ERROR]  L1: <rule code> — <claim>. src: coreclaw-cli-audit/contract-checklist.md R### [file:line]
[VERIFY] L2: <claim> — ship examples/verify-<topic>, run via MCP run_worker [file:line]
[WARN]   L1: <rule code> — <claim>. src: <doc or rule> [file:line]
[SUGGEST] L4: <improvement>. src: concurrency-rules.md §<section> [file:line]
```

End with `net: <E> errors, <W> warns, <V> pending probes, <S> suggestions.`
Apply nothing unless asked — this skill reports; the user decides.

## MCP / API adaptation

When verifying, use the MCP surface (it already fixes the pagination offset
and `/last` freshness bugs that raw REST callers hit):

- Discovery: `list_store_workers` (public) / `list_workers` (owned) →
  `get_worker` → `get_worker_input_schema`.
- Run: `run_worker` (async, ad-hoc input) or `run_worker_task` (saved preset).
  For regression across many workers: `run_workers_batch` with `verify` on,
  `concurrency=1` to avoid rate-limit masking.
- Status: `get_worker_run` (explicit `run_id`, preferred over `/last` which
  can be stale on REST).
- Results: `list_worker_run_results` (preview) / `export_worker_run_results`
  (download, 8 formats).
- Verdict without row inspection: `verify_run` → PASS / NO_DATA / FAILED /
  ERROR_RECORD / RUNNING / SUBMIT_FAIL (guards against CAPTCHA/403 rows being
  misread as PASS).
- Logs on failure: `get_worker_run_log` (supports grep/context_lines).

Auth: MCP forwards `Authorization: Bearer <token>` upstream. v2 has **no**
`api-key` header — only Bearer or `?token=` (a v2 caller using `api-key` is
silently unauthenticated, an `error` finding).

## Keeping the rule set in sync

The `coreclaw-cli-audit` skill is actively iterated (recent commits added
`hardcoded_api_key`, `aiohttp_without_proxy`, `asyncio_run_with_sdk`,
`external_worker_slug_reference`, `dynamic_css_class_selector` rules). Before
a serious audit, pull the latest and diff. Procedure:
`references/sync-procedure.md`.

## Recency

Rule set reflects `coreclaw-cli` as of 2026-07-21 (commits through `cd48129`).
Concurrency rules reflect the 2026-07 platform HTML. Upstream drifts — re-sync
before relying on rule codes, and re-run any `error` claim against a live
probe.
