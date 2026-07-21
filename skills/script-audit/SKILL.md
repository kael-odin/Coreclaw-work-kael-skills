---
name: script-audit
description: >
  Full-stack audit of a CoreClaw work script — correctness, security, convention,
  and known-pitfall checklist, with evidence pointers. Use when reviewing any
  script in the CoreClaw workspace: scraper workers, CLI modules, n8n node
  operations, MCP server handlers, or content-repo scripts. Trigger on: "audit
  this script", "review this worker", "审核脚本", "脚本安全检查", "check this
  against known pitfalls", "is this upload-safe".
---

# Script Audit (CoreClaw Work)

Audit a single script across four dimensions, then surface findings ranked by
severity. Every finding cites a source: a workspace file path, a memory note,
a commit, or an upstream interface. No unsourced severity claims.

This is **not** `coreclaw-cli-audit` (which checks the CLI's own validation
logic against platform docs). This audits *any* script you work on — a worker,
a CLI module, an n8n node op, an MCP handler, a content-repo helper.

## Sources

- Workspace root: `D:/Coreclaw_Work/github/`
- Upstream API contract: `exported-api-docs/openapi.json` (37 operations, `/api/v2`, Bearer auth)
- Platform docs: `scraper-webui-docs/` (worker definition, concurrency rules, API playground)
- Known-pitfall memory notes (auto-recalled, see checklist below for the canonical set)
- Reference files in this skill: `references/known-pitfalls.md`, `references/severity-policy.md`

## Background: why these dimensions

CoreClaw work has burned real time on four recurring failure classes. Each
audit dimension maps to one:

1. **Correctness** — the script runs but produces wrong output. Biggest sink:
   pagination offset is 1-based page index, not absolute row offset (fixed
   upstream + MCP compensation layer, 2026-07-15). A script that treats
   `offset` as rows-skipped silently returns duplicate or missing rows.
2. **Security** — credentials leak, proxies bypassed, input trusted. Workers
   that hardcode `socks5://user:pass@...` literals or read socks proxy without
   `proxy:false` on axios leak or misroute.
3. **Convention** — the platform accepts the script but the form renders
   wrong or the n8n CI lint goes red. `schedule_weekday` enum is 1-7 (1=Mon),
   not 0-6; format option arrays must be alphabetical; JSON-ish format names
   must be uppercase.
4. **Known-pitfall cross-check** — the script trips something already
   diagnosed once. The input-wrapping pitfall (`input` must be wrapped as
   `parameters.custom` in SDK `worker.run`) is the canonical example.

## The severity policy (do not skip)

Two severity tiers, and the rule that cost two rounds to learn:

- `error` = platform upload or runtime **hard-rejects** (non-zero `code`, HTTP
  4xx/5xx, script does not run). Missing required files, type/editor mismatch
  that breaks the form, HTTP script that ignores proxy, hardcoded proxy
  credentials, Camoufox not pinning `playwright==1.49.1`, upsert key absent
  from output_schema.
- `warn` = platform accepts but the form/runtime may misbehave, or it's a
  documented should/conventional. editor-type mismatch (platform does NOT
  reject — proven 2026-07-13), legacy type alias, missing README, missing
  doc-marked title/editor/description/required.

**Iron rule: any `error` severity claim must be backed by a real probe
(`examples/verify-*`), not by a doc "must".** The 2026-06-17 "code 4000"
incident lifted a doc "must" into `error` + a fabricated error code; 2026-07-13
real-run probes proved the platform accepts every editor/type mismatch and
there is no code 4000 (business codes start at 10000). Reverted. If you cannot
point to a probe result, the finding is `warn` with `（待平台实测）`, never
`error`.

Full policy with the incident timeline: `references/severity-policy.md`.

## Audit workflow

### Phase 1 — Read the whole script first

Before tagging anything, trace the full flow end to end. Read the script, its
callers, and the output it feeds. A finding at the wrong function is a second
bug. Use Grep on every caller of any function you're about to flag — the lazy
fix is the root-cause fix (one guard in the shared function beats one guard
per caller).

### Phase 2 — Four-dimension scan

Run each dimension's checklist (see `references/known-pitfalls.md` for the
canonical set with sources). For each hit, record: dimension, file:line,
claim, severity, source pointer.

### Phase 3 — Source every finding

For each finding, attach one of:
- Workspace path with line, e.g. `coreclaw-mcp-server/v2_tools.go:L120`
- Memory slug, e.g. `[[coreclaw-sdk-input-pitfall]]`
- Upstream path, e.g. `exported-api-docs/openapi.json` operationId `runWorker`
- `（实测结论 YYYY-MM-DD，待复核）` for run-derived claims with no file home

Unsourced → drop to `warn` and mark pending, or discard.

### Phase 4 — Probe gate for any `error`

If you want to assert `error` and no existing probe result covers it, the
finding becomes `[VERIFY]` — must ship an `examples/verify-<topic>/` minimal
worker, upload, run, record real code+message, then promote to `error` or
demote to `warn`. Never assert `error` from a doc "must" alone.

### Phase 5 — Ranked output

One finding per line, `error` first:

```
[ERROR] <dimension>: <claim>. <source> [file:line]
[VERIFY] <dimension>: <claim> — no probe yet, ship verify-<topic>. [file:line]
[WARN]  <dimension>: <claim>. <source> [file:line]
```

End with `net: <E> errors, <W> warns, <V> pending probes.` If clean:
`No findings. Ship.` Apply nothing unless asked.

## Canonical known-pitfall set (cross-check every script)

These are the pitfalls that have already cost a real run. Full source pointers
in `references/known-pitfalls.md`.

- **Input wrapping (SDK)** — `worker.run` input must be wrapped as
  `parameters.custom`, not passed top-level. Source: `[[coreclaw-sdk-input-pitfall]]`.
- **Pagination offset** — upstream list endpoints use 1-based page index
  (`page_index = offset/limit + 1`), not absolute row offset. MCP server has a
  transparent compensation layer; REST callers must align offset to a limit
  multiple. Source: `[[coreclaw-pagination-bug-fix-2026-07-15]]`.
- **schedule_weekday enum** — 1-7 (1=Monday, 7=Sunday), NOT 0-6 / 0=Sunday.
  Source: `scraper-webui-docs/worker-tasks/create.mdx`, `[[coreclaw-n8n-ci-lint-lesson]]`.
- **format enum** — 8 values: csv/json/jsonl/xlsx/xls/xml/html/rss. Option
  arrays alphabetical; format names uppercase in prose. Source: `[[coreclaw-wrapper-repos-enum-fix-2026-07-10]]`.
- **Hardcoded proxy credentials** — `socks5://user:pass@` literals in source =
  `error`. axios + socks-proxy-agent without `proxy:false` = `warn`. Source:
  `[[coreclaw-cli-validation-audit-2026-07-11]]` rules A6/A7.
- **Camoufox + Playwright pin** — Camoufox-domain script must pin
  `playwright==1.49.1`. Source: rule A3, same note.
- **output_schema presence** — missing `output_schema.json` is `error` (was
  warn). Source: rule A1, `builds-and-runs.md`.
- **upsert key in schema** — `upsert_data`/`upsertData` second-arg literal key
  must exist in output_schema, else `error`. Source: rule A4.
- **n8n CI lint ≠ local lint** — `npm ci --ignore-scripts` syncs to CI's rule
  set before `npm run lint`; local clean does not guarantee CI green. Source:
  `[[coreclaw-n8n-ci-lint-lesson]]`.
- **/last freshness** — `/last` run endpoint can return stale state; MCP
  server fixed, REST callers beware. Source: `[[coreclaw-mcp-server-skill-audit-2026-07-10]]`.
- **callback body field** — run-status callback body uses `run_status`, not
  `status`; `run_status` enum is lowercase string, no `aborted`. Source:
  `[[coreclaw-skill-plugin-wrapper]]` 2026-07-15 sync.

## Script / command / MCP adaptation

When the audited script touches the CoreClaw platform, prefer the MCP surface
over hand-rolled HTTP (the MCP server applies the pagination compensation and
freshness fixes already):

- Discover worker before judging input shape: `get_worker_input_schema` —
  don't invent field names; the live schema is authoritative.
- Confirm a run actually rejects before asserting `error`: use `run_worker`
  (async) + `get_worker_run` / `get_worker_run_log` to capture the real `code`
  and `message`. This IS the probe.
- For batch regression: `run_workers_batch` with `verify` on, `concurrency=1`
  to avoid rate-limit masking.
- REST fallback (MCP unavailable): `exported-api-docs/openapi.json` is the
  contract; base URL `https://openapi.coreclaw.com`, Bearer header or
  `?token=` query.

## Recency

This checklist reflects platform behavior as of 2026-07-15. Upstream drifts —
re-verify `error`-severity claims against a live probe before relying on them.
