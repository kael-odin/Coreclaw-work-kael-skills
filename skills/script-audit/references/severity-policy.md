# Severity Policy

## Two tiers

| Severity | Meaning | Decides upload? |
|----------|---------|-----------------|
| `error` | Platform upload or runtime hard-rejects (non-zero `code`, HTTP 4xx/5xx, script does not run), OR a correctness bug producing silent wrong output, OR a security leak. | Block. |
| `warn` | Platform accepts but form/runtime may misbehave, OR a documented should/conventional, OR a run-derived claim without a file home. | Do not block. |

`info` exists for pure tips; rarely used in audit findings.

## The iron rule

**Any `error` severity claim must be backed by a real probe result
(`examples/verify-<topic>/`), not by a doc "must".**

If no probe covers the claim:
- The finding is `[VERIFY]`, not `[ERROR]`.
- Ship a minimal worker under `examples/verify-<topic>/`, upload, run, record
  the real `code` + `message`.
- Promote to `error` only if the platform hard-rejects; otherwise demote to
  `warn`.

Exceptions where a probe is not required (the rejection is structural, not
behavioral): missing required files (`output_schema.json`, `main.py`/`index.js`),
hardcoded credential literals, missing Bearer auth on v2 calls. These are
`error` by construction.

## Why this rule exists — the code 4000 incident

- **2026-06-17:** CLI audit lifted a doc "must" (editor/type should match)
  into `error` severity and wrote "code 4000 / Invalid custom parameters" as
  the rejection message. No probe was run. Based on doc assumption + a
  `schema.js` comment, not a real run.
- **2026-07-13:** Probes `verify-code4000` (11 editor/type mismatches) and
  `verify-required-fields` (7 missing-field cases) were uploaded and run. The
  platform **accepted every one** and ran them successfully. There is no code
  4000 — `error-codes.md` starts at 10000.
- **Result:** all editor/type mismatches demoted `error`→`warn`; "code 4000"
  wording removed everywhere; `input_property_missing_*` kept `warn`
  (confirmed correct).

Two rounds of work to undo one unsourced `error`. The rule is the lesson.

## Correctness `error` without a probe

Correctness bugs (silent wrong output, not platform rejection) can be `error`
without an upload probe, but MUST have a runnable self-check demonstrating the
wrong output: an `assert`-based `demo()`/`__main__` block or one small
`test_*.py`/`test_*.js` that fails if the logic breaks. The pagination offset
trap (P2) is the canonical example — demonstrate the off-by-page with a small
loop, no platform call needed.

## Severity cheat sheet (from validated rules)

`error`:
- Missing `output_schema.json` (rule A1)
- Camoufox not pinning `playwright==1.49.1` (A3)
- Upsert key not in output_schema (A4)
- Hardcoded proxy credential string literal (A7)
- v2 caller using `api-key` header (P13)
- Callback handler reading `status` not `run_status` (P12)
- SDK input not wrapped as `parameters.custom` (P1)
- Pagination offset as row offset producing wrong data (P2, with self-check)

`warn`:
- editor/type mismatch (platform accepts — proven 2026-07-13)
- axios + socks-proxy-agent without `proxy:false` (A6)
- `set_table_header` after `push_data` (A5)
- Missing README / missing doc-marked title/editor/description/required
- format option array not alphabetical; format names lowercase in prose (P4)
- `/last` endpoint staleness in REST callers (P11)
