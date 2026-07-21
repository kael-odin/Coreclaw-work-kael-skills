# Coreclaw Work — Kael's Skills

Personal Claude Code skills for CoreClaw work, all bundled in a single plugin (`kael-skills`). Skills are Sources-backed and evidence-pointed: every claim traces to the actual script, a platform doc, an upstream contract, or a memory note.

## Why this exists

CoreClaw work spans many surfaces (API v2, MCP server, n8n nodes, CLI, scraper workers, content repos). Know-how that took a real run to learn — the input-wrapping pitfall, the 1-based pagination offset, the concurrency.fields throughput lever — should be captured once and reused, not rediscovered every session.

These skills are written for **my own reuse**. They are not the consumer-facing CoreClaw-Skill (which teaches how to *operate* the platform API). These teach how to *do my job* on the platform.

## Install

```bash
claude plugin marketplace add kael-odin/Coreclaw-work-kael-skills
claude plugin install kael-skills@coreclaw-work-kael-skills
```

All skills load under the `kael-skills` plugin namespace.

## Skills

| Skill | What it does | Key sources |
|-------|--------------|-------------|
| `script-audit` | Five-layer audit of a CoreClaw worker: static rules (error/warn), live API/MCP input verification, output correctness, improvement suggestions (concurrency.fields tuning for throughput/cost). Rule set sourced from and kept in sync with `Core-Claw/coreclaw-cli` audit skill. | `Core-Claw/coreclaw-cli` audit skill · `exported-api-docs/openapi.json` · platform docs |
| `readme-writer` | Bilingual (EN + ZH) README for a CoreClaw worker, grounded in the actual script's scraping logic, input/output fields, and capability range. No fabricated info, no fabricated links, real input/output examples. | `D:/Coreclaw_Work/scripts/tiktok_2/` template · platform docs |

More to come: worker dev/packaging, worker-task CRUD acceptance cases, three-repo enum sync checklist, upstream-change triage. All will live in this same plugin.

## Source policy

Every skill carries a **Sources** section. Claims trace to:
- The actual script being audited/documented (file path + line)
- Platform docs (canonical URLs)
- Upstream contract (`exported-api-docs/openapi.json` operationId)
- `Core-Claw/coreclaw-cli` audit skill (rule codes, kept in sync)
- A memory note or a probe result with a date

Claims without a source are marked `（实测结论 YYYY-MM-DD，待复核）` and stamped with the verification date. Upstream behavior drifts — re-check before relying on a stale claim.

## Structure

```
.claude-plugin/
  marketplace.json          # marketplace: one plugin, kael-skills
  plugin.json               # the plugin manifest
skills/
  script-audit/
    SKILL.md
    references/             # verification-protocol, concurrency-suggestions, sync-procedure
  readme-writer/
    SKILL.md
    references/             # readme-structure, grounding-rules, bilingual-style
```

Adding a new skill = add `skills/<name>/` and it auto-loads under the plugin. No manifest change needed.
