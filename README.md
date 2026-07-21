# Coreclaw Work — Kael's Skills

Personal Claude Code skills for CoreClaw work — content operations, development, testing/acceptance, and maintenance. Each skill is Sources-backed and evidence-pointed: every claim traces to a file path, a memory note, a commit, or an upstream interface.

## Why this exists

CoreClaw work spans many surfaces (API v2, MCP server, n8n nodes, CLI, scraper workers, content repos). Know-how that took a real run to learn — the input-wrapping pitfall, the 1-based pagination offset, the enum sync checklist across three wrapper repos — should be captured once and reused, not rediscovered every session.

Skills are written for **my own reuse**. They are not the consumer-facing CoreClaw-Skill (which teaches how to *operate* the platform API). These teach how to *do my job* on the platform.

## Install

Add the marketplace, then install any skill individually:

```bash
claude plugin marketplace add kael-odin/Coreclaw-work-kael-skills
claude plugin install <plugin-name>@coreclaw-work-kael-skills
```

Each skill lives in `skills/<name>/`. After install it loads as `/<name>` (or `/<plugin-name>:<skill>` via marketplace).

## Skills

| Skill | What it does | Status |
|-------|--------------|--------|
| `script-audit` | Full-stack audit of a CoreClaw work script: correctness, security, convention, and known-pitfall checklist. Sources-backed. | ✅ v1 |
| `markdown-seo` | Write and SEO-optimize Markdown for CoreClaw content repos (READMEs, docs, guides). Not visual beautification. | ✅ v1 |

More to come: worker dev/packaging, worker-task CRUD acceptance cases, three-repo enum sync checklist, upstream-change triage.

## Source policy

Every skill carries a **Sources** section. Claims that come from a real run or audit point to:
- A file path under `D:/Coreclaw_Work/github/` (e.g. `exported-api-docs/openapi.json`)
- A memory note slug (e.g. `coreclaw-sdk-input-pitfall`)
- A commit SHA or upstream API path when the claim is about platform behavior

Claims without a source are marked `（实测结论，时效性见 skill 末尾）` and stamped with the verification date. Upstream behavior drifts — re-check before relying on a stale claim.
