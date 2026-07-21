# Sync Procedure — Keeping the rule set in sync with coreclaw-cli-audit

The static rule set (Layer 1) is authored in `Core-Claw/coreclaw-cli` →
`skills/coreclaw-cli-audit/`. This skill does NOT redefine those rules; it
cites them. Before a serious audit, sync.

## When to sync

- Before auditing a worker you haven't audited in the last 2 weeks.
- When a finding cites a rule code and you're unsure it still exists.
- After the `coreclaw-cli` repo gets new commits on `audit`/`validation`
  (watch commits touching `skills/coreclaw-cli-audit/` or `src/validation/`).

## Sync steps

```bash
cd D:/Coreclaw_Work/github/coreclaw-cli
git fetch origin
git log --oneline origin/main -10              # scan for audit/validation commits
git pull --ff-only
```

Then diff the rule sources against what this skill's last audit assumed:

```bash
# 1. Rule checklist (the canonical rule codes + severity)
diff skills/coreclaw-cli-audit/references/contract-checklist.md <(echo "<last-audit-assumed>")

# 2. Known gaps + probe results (resolved/open)
cat skills/coreclaw-cli-audit/references/known-gaps.md

# 3. Concurrency rules (basis for improvement suggestions)
cat skills/coreclaw-cli-audit/references/concurrency-rules.md

# 4. Run the automated diff (rule coverage + API operationId coverage)
node skills/coreclaw-cli-audit/scripts/diff-contract.cjs
```

## What to carry into this skill

- New rule codes → cite them in Layer 1 findings by their code (e.g. `R216`,
  `hardcoded_api_key`). Do not copy the rule text into this skill — point to
  the source.
- New probe results in `known-gaps.md` → update severity assumptions. A rule
  marked `✅ Resolved` as `error` stays `error`; a rule marked `⚠️ 实测推翻`
  means the prior `error` is now `warn` (or gone).
- New concurrency behavior in `concurrency-rules.md` → update
  `references/concurrency-suggestions.md`.
- New operationId in `exported-api-docs/openapi.json` → update the MCP
  adaptation list in this skill's SKILL.md if a verification step needs it.

## What NOT to carry

- The CLI's own validation code (`src/validation/*.js`) — that's the engine,
  not the rules. This skill runs the engine; it doesn't port it.
- The CLI's `test/` fixtures — they test the CLI, not your worker.

## Recency stamp

After syncing, update the `## Recency` line at the bottom of
`skills/script-audit/SKILL.md` with the `coreclaw-cli` commit SHA and date.
This is the only place this skill asserts "current as of" — every other claim
points to a source instead.
